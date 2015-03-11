from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.utils import timezone

from rallybench.models import RallyUser,RallyUserSession, Scenario, Deployment, RallyTask
from rallybench.utils import UserContext
from rallybench.utils import RallyUtility

import uuid
	
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
		'scenario': context.scenarios		
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
	numscenarios = 0
	depls = []
	scenes = []
	try:
		deplQuerySet = Deployment.objects.filter(user__username=user)
		for adepl in deplQuerySet:
			numdeployments = numdeployments + 1
			depls.append(adepl)
		real_deployments = True
	except Deployment.DoesNotExist:
		pass		
	#senarios are listed only for users with deployment
	if real_deployments:
		try:
			#TBD
			scenes = Scenario.objects.all()	
		except Scenario.DoesNotExist:
			pass		
	#Create a user context to show in dashboard
	ctxt = UserContext(name=user.username, deployments=depls, scenarios=scenes, 
				args={  'numdeployments':numdeployments, 
					'numscenarios':numscenarios,
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
	rallycmd = RallyUtility()
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

	#Create deployment call handler
	if request.POST:
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
		
		deployment = Deployment(user=auser, uniqueid=deployment_id, 
				osc_friendly_name=friendly_name, 
				osc_tenant_name=osc_tenant_name, 
				osc_username=osc_tenant_user_name,
				osc_password=osc_tenant_password,
				osc_auth_url=osc_auth_url,
				osc_type=deployment_type,
				osc_endpoint_type=osc_endpoint_type,
				osc_region_name=osc_region_name)
		#save the deployment
		deployment.save()
		
	#list deployments
	depls = []	
	scene_by_type = {}
	err = 0
	numdeployments = 0
	try:
		deplQuerySet = Deployment.objects.filter(user__username=username)
		for adepl in deplQuerySet:
			numdeployments = numdeployments + 1
			depls.append(adepl)
		#list scenarios
		rally_scenes = rallycmd.rally_scenarios_list()
		for ascene in rally_scenes:
   			objScene = Scenario(scenario_type=ascene[0], scenario_file_name=ascene[1])
			objScene.save()

		#interested in neutron, nova scenarios
		try:
			scenes = []
			scenes = Scenario.objects.filter(scenario_type='neutron')
			scene_by_type['neutron'] = scenes

			scenes = Scenario.objects.filter(scenario_type='nova')
			scene_by_type['nova'] = scenes
			
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
			'scenarios': scene_by_type, 
			'state':message, 
			'ErrorCode':err, 
			'numdeployments':numdeployments
		   }
	deploymentcontext = RequestContext(request, _context)		
	return render_to_response('rallybench/deployment.html', context_instance=deploymentcontext)

# '/username/scenario/'
def scenario(request, username):
	return HttpResponse("For user %s, listing scenario ..." % (username))

# '/username/task/'
def task(request, username):
	return HttpResponse("For user %s, listing tasks ..." % (username))

# '/username/result/'
def result(request, username):
	return HttpResponse("For user %s, listing result ..." % (username))


