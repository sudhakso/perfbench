from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from rallybench.models import RallyUser,RallyUserSession, Scenario, Deployment, RallyTask, Transaction
from rallybench.utils import UserContext
from rallybench.utils import RallyUtility

import uuid
import os
import webbrowser

from string import lower
	
# Create your views here.
# '/'
def login(request):
    state = "Please log in below..."
    username = password = ''   
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
	#Authenticate
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:		
                ctxt = loginuser(request, user,password)
		return show_userdash(request, ctxt)
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    logincontext = RequestContext(request, {
	'state' : state,
	'username' : username,
    })
    return render_to_response('rallybench/auth.html', context_instance=logincontext)

#Show user dash
def show_userdash(request, context):
	#Redirect to users page.		
	usercontext = RequestContext(request, {
		'state': context.args['state'],
		'username': context.args['username'],
		'numdeployments': context.args['numdeployments'],
		'numscenarios': context.args['numscenarios'],
		'deployment': context.deployment, 
		'scenario': context.scenarios,
		'numtasks': context.args['numtasks'],
		'tasks':context.args['tasks'],
		'transactions': context.args['transactions']		
	    })
	return render_to_response('rallybench/user.html', context_instance=usercontext)

#pull information, and land the user to his login page 
def loginuser(request, user,passwd):
	ctxt = None
	userses = None
	state = ''
	#login is success, we need to fetch this user session from the DB.
	try:
		auser = RallyUser.objects.get(username=user)
	except RallyUser.DoesNotExist:
		auser = None
		
	if auser is None:
		auser = RallyUser(username=user, password=passwd, created=timezone.now())
		auser.userwd = '/home/%s'%(user)
		auser.save()
		state = "You're successfully logged in!"

	#get a user session
	try:
		userses = RallyUserSession.objects.filter(user__username=auser.username)
	except RallyUserSession.DoesNotExist:
		#create the first time user session
		sesid = '%s_%s' % (auser.username,uuid.uuid4())
		userses = RallyUserSession(auser,session_id=sesid, last_activity=timezone.now())
		#user dont have deployment or any scenarios to access!
		userses.save()

	#for the user, get the deployments, list the available scenarios
	real_deployments = False
	numdeployments = 0	
	depls = []
	scenes = []
	tasks = []
	trans = []
	try:
		deplQuerySet = Deployment.objects.filter(user__username=user)
		for adepl in deplQuerySet:
			numdeployments = numdeployments + 1
			depls.append(adepl)
		real_deployments = True
	except Deployment.DoesNotExist:
		pass		
	
	#scenarios are listed only for users with deployment
	if real_deployments:
		try:
			#TBD
			scenes = Scenario.objects.all()	
		except Scenario.DoesNotExist:
			pass		
	
	#tasks listed only for users with deployment
	if real_deployments:	
		try:
			taskQuerySet = RallyTask.objects.filter(user_id__username=user)
			for atask in taskQuerySet:			
				tasks.append(atask)
		except RallyTask.DoesNotExist:
			print 'cannot read tasks for the user %s' % (user)
			pass
	
	#transactions for the user
	try:
		transset = Transaction.objects.filter(user_id__username=user)
		for atransaction in transset:			
			trans.append(atransaction)
	except Transaction.DoesNotExist:
			print 'Dont have  any transaction for the user %s' % (user)
			pass
	print 'heavy trans %s' %(len(trans)) 
	#Create a user context to show in dashboard
	ctxt = UserContext(name=user.username, deployments=depls, scenarios=scenes, 
				args={  'numdeployments':numdeployments, 
					'numscenarios':len(scenes),
					'numtasks':len(tasks),
					'tasks':tasks,
					'transactions':trans,
					'state': state,
					'username': user
					})
	return ctxt

# '/username'
def usersession(request, username):
	#question_list = Question.objects.all()
	#template = loader.get_template('poll/index.html')
	#context = RequestContext(request, {
	#  'question_list' : question_list,
	#})
	return HttpResponse("logged-in as %s" % (username))

# '/username/deployment/'
def deployment(request, username):	
        #TBD: user profile to contain the home dir
	rallycmd = RallyUtility('/usr/local/bin/', '/home/%s/rally' % (username), '/home/%s' % (username))
	message  = 'All is Well for %s' %(username)	
	#login is success, we need to fetch this user session from the DB.
	try:
		auser = RallyUser.objects.get(username=username)
	except RallyUser.DoesNotExist:
		errorcontext = RequestContext(request, {
			'state': 'Fatal error while loading user. Happened while rendering Deployment.',
			'ErrorCode': 503,
			'username': username		
	    		})
		return render_to_response('rallybench/error.html', context_instance=errorcontext)
	
	#Run Scenario
	if request.POST.get('mybtn'): 
		print 'POST Request hit'
		print request.POST
		
		#<QueryDict: {u'csrfmiddlewaretoken': [u'VuoRMysrosOyXq9vDaaaBxiW2JNTHavF'], u'mybtn': [u'Run Scenario'], u'neutron': [u'neutron', 	
		#u'create_and_update_networks.json', u'create_and_list_subnets.json', u'create_and_delete_ports.json'], u'deployment': [u'trial']}>
		scenes = []
		scenario_type = ''
		if request.POST.get('neutron'):
			scenario_type = 'neutron'
			scenes = list(request.POST.getlist('neutron'))		
		elif request.POST.get('nova'):
			scenario_type = 'nova'
			scenes = list(request.POST.getlist('nova'))
		elif request.POST.get('cinder'):
			scenario_type = 'cinder'
			scenes = list(request.POST.getlist('cinder'))
			
		print "Request parsed %s/%s" % (scenario_type, scenes)
		
		(task_id, task_status, start_time, end_time) = create_task(request, username, deployment_friendly_name=request.POST.get('deployment'),
									 scenario_type=scenario_type, selected_scenarios = scenes)
		
		tasks = []
		sceneobjs = []
		scenes = []
		numtasks = 0
		try:
			taskQuerySet = RallyTask.objects.filter(user_id__username=username)
			for atask in taskQuerySet:
				numtasks = numtasks + 1
				sceneobjs = atask.scenarios.all()
				for ascene in sceneobjs:
					scenes.append(ascene.scenario_file_name)		
				tasks.append(atask)
		except RallyTask.DoesNotExist:
			pass
		#Create a user context to show in tasklist
		_context = {
			'username': username, 
			'numtasks': len(tasks),
			'scenarios' : scenes,
			'tasks': tasks
		   }
		
		context = RequestContext(request, _context)
		#redirect the user to the task list
		#return render_to_response('rallybench/tasklist.html', context_instance=context)
		return HttpResponseRedirect(reverse('task',args=(),
    							kwargs={'username': username}))
		
	#Create deployment
	if request.POST.get('createdepl'): 
		print 'POST request hit'
		print request.POST

		friendly_name = request.POST.get('name')

		deployment_type = request.POST.get('type')
		osc_endpoint_type = request.POST.get('osc_endpoint_type')
		osc_region_name = request.POST.get('osc_region_name')
		osc_auth_url = request.POST.get('osc_auth_url')
		osc_tenant_name = request.POST.get('osc_tenant_name')
		osc_tenant_user_name = request.POST.get('osc_tenant_user_name')
		osc_tenant_password = request.POST.get('osc_tenant_password')
		
		#Invoke commands to create rally deployment.		
		deployment_id = rallycmd.deployment_create(deployment_friendly_name=friendly_name, 
							deployment_owner=username, 
							osc_type=deployment_type,
	 						osc_auth_url=osc_auth_url, 
							osc_endpoint_type=osc_endpoint_type, 
							osc_region_name=osc_region_name,
							osc_tenant_name=osc_tenant_name, 	
							osc_tenant_user=osc_tenant_user_name, 
							osc_tenant_password=osc_tenant_password)
		if deployment_id == -1:
			errorcontext = RequestContext(request, {
			'state': 'Fatal error while creating a deployment.',
			'ErrorCode': 503,
			'username': username		
	    		})
			return render_to_response('rallybench/error.html', context_instance=errorcontext)
	
		allservices_up = True
		availability = rallycmd.deployment_check(friendly_name)
		for aComp in availability.keys():
			if aComp == 'services':
				pass
			if availability[aComp] != 'Available':
				allservices_up = False
				break

		deployment = Deployment(user=auser, uniqueid=deployment_id, 
				osc_friendly_name=friendly_name, 
				osc_tenant_name=osc_tenant_name, 
				osc_username=osc_tenant_user_name,
				osc_password=osc_tenant_password,
				osc_auth_url=osc_auth_url,
				osc_type=deployment_type,
				osc_endpoint_type=osc_endpoint_type,
				osc_region_name=osc_region_name)
		if allservices_up:
			deployment.validated = True

		#save the deployment
		deployment.save()
		
	#list deployments
	depls = []	
	scenarios = {}
	err = 0
	numdeployments = 0
	try:
		deplQuerySet = Deployment.objects.filter(user__username=username)
		for adepl in deplQuerySet:
			numdeployments = numdeployments + 1
			depls.append(adepl)
		#list scenarios
		scene_by_type = rallycmd.scenario_list()
		numscenarios = 0
		for acomponent in scene_by_type.keys():
			scenes = scene_by_type[acomponent]
			for scene in scenes:
				if len(Scenario.objects.filter(scenario_file_name=scene)) == 0:
		   			objScene = Scenario(scenario_type=acomponent, scenario_file_name=scene)
					objScene.save()

		#interested in neutron, nova scenarios
		try:			
			numscenario = 0
			scenarios = Scenario.objects.all()			
			numscenario = numscenario + len(scenarios)			
		except Scenario.DoesNotExist:
			pass

	except Deployment.DoesNotExist:
		err = 503
		message = 'Fatal error while filtering deployment for user %s' % (username)
		pass	
	
	#Create a user context to show in deployment
	_context = {
			'username': auser.username, 
			'deployments': depls,
			'scenariotypes' : ['nova', 'neutron', 'cinder'],
			'scenarios': scenarios, 
			'state':message, 
			'ErrorCode':err, 
			'numdeployments':numdeployments,
			'numscenarios':numscenarios
		   }
	deploymentcontext = RequestContext(request, _context)		
	return render_to_response('rallybench/deployment.html', context_instance=deploymentcontext)

# '/username/scenario/'
def scenario(request, username):
	return HttpResponse("For user %s, listing scenario ..." % (username))

# '/username/tasklist/'
def task(request, username):
	tasks = []
	sceneobjs = []
	scenes = []
	numtasks = 0
	try:
		taskQuerySet = RallyTask.objects.filter(user_id__username=username)
		for atask in taskQuerySet:
			numtasks = numtasks + 1
			sceneobjs = atask.scenarios.all()
			for ascene in sceneobjs:
				scenes.append(ascene.scenario_file_name)		
			tasks.append(atask)
	except RallyTask.DoesNotExist:
		pass
	#Create a user context to show in tasklist
	_context = {
			'username': username, 
			'numtasks': len(tasks),
			'scenarios' : scenes,
			'tasks': tasks
		   }
	
	#Launch report POST call
	if request.POST:		
		output = ''
		taskid = request.POST.get('taskid')
		
		try:
			taskset = RallyTask.objects.filter(task_id=taskid)
			atask = taskset[0]		
			resultfile =  os.path.join(settings.BASE_DIR, 'rallybench/templates/rallybench/userresult.html')
			##test			
			if atask.task_status == 'finished':	
				with open(atask.task_output_html) as f:
					with open(resultfile, "w+") as f1:
						for line in f:
							f1.write(line)				
				url = "file://%s" % (resultfile)
				new = 2
				webbrowser.open_new_tab(url)
				pass
			
		except RallyTask.DoesNotExist:
			errorcontext = RequestContext(request, {
												'state': 'Fatal error while loading user. Happened while creating benchmark task.',
												'ErrorCode': 503,
												'username': username		
	    							})
			return render_to_response('rallybench/error.html', context_instance=errorcontext)
		
	tasklistcontext = RequestContext(request, _context)		
	return render_to_response('rallybench/tasklist.html', context_instance=tasklistcontext)
	
# '/username/result/'
def result(request, username):	
	return render_to_response('rallybench/feelgooduser.html', context_instance=None)

#run a rally task
#create a rallytask instance and store objects
def create_task(request, username, deployment_friendly_name, scenario_type, selected_scenarios):
	#TBD: User home directory to be set via profile
	rallycmd = RallyUtility('/usr/local/bin/', '/home/%s/rally' % (username), '/home/%s' % (username))

	try:
		auser = RallyUser.objects.get(username=username)
	except RallyUser.DoesNotExist:
		errorcontext = RequestContext(request, {
			'state': 'Fatal error while loading user. Happened while creating benchmark task.',
			'ErrorCode': 503,
			'username': username		
	    		})
		return render_to_response('rallybench/error.html', context_instance=errorcontext)
	
	scenes = selected_scenarios[1:]
	(task_id, task_status, start_time, end_time, path_to_report) = rallycmd.rally_run_scenarios(deployment_friendly_name, scene_type=scenario_type, scenario_listing=scenes)	
	#Add task to the databse for tracking
	print "Task stats %s:%s:%s:%s - %s" % (task_id, task_status, start_time, end_time, path_to_report)
	 
	if task_id != -1:
		task = RallyTask(user_id=auser, task_id=task_id)
		task.task_status = task_status
		task.created_time = start_time
		task.finished_time = end_time		
		task.task_output_html = path_to_report
		
		print "linking scenarios"
		#Save all scenarios associated
		for ascenario in scenes:
			try: 
				resultset = Scenario.objects.filter(scenario_file_name=ascenario)
				if len(resultset):
					task.scenarios.add(resultset[0])
					task.deployment_name = deployment_friendly_name
					task.save()				
					
			except Scenario.DoesNotExist:
				pass
	
	return (task_id, task_status, start_time, end_time)
			
	

	





