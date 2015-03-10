from django.db import models

# Create your models here.

# A rally user
class RallyUser(models.Model):
	#key
	username = models.CharField(max_length=50, primary_key=True)
	password = models.CharField(max_length=50)
	userwd   = models.CharField(max_length=256)
	created  = models.DateField()
	#Admin user
	isAdmin  = models.BooleanField(default=False)

	#helper
	def __str__(self):
		return '%s:%s' %(self.username, self.created)
	def __unicode__(self):
		return self.__str__()

#Schema of a session associated with the User
class RallyUserSession(models.Model):
	#For the user instance
	user = models.ForeignKey(RallyUser)	
	#Key
	session_id = models.CharField(max_length=256, primary_key=True)

	last_activity = models.DateField()
	taskId = models.CharField(max_length=256)
	current_scenario_selection = []
	
	#helper
	def __str__(self):
		return'%s:%s' % (self.user.username, self.session_id)
	def __unicode__(self):
		return self.__str__()

#Schema of placeholder for user scenarios
#class MasterScenario(models.Model):
#	user = models.ForeignKey(RallyUser)
#	scenario_folder_path = models.CharField(max_length=256)
#	
#	#helper
#	def __str__(self):
#		return '%s:%s' %(self.user, self.scenario_folder_path)
#	def __unicode__(self):
#		return self.__str__()

#Schema of a scenario
class Scenario(models.Model):
	#Key 
	#Scenario name, eg: create_and_assign_ip_ports
	scenario_file_name = models.CharField(max_length=256, primary_key=True)
	#Scenario type, eg: neutron
	scenario_type = models.CharField(max_length=16)
	

#Schema for a rally deployment
class Deployment(models.Model):
	#Deployment for a user
	user = models.ForeignKey(RallyUser)
	#Key
	uniqueid = models.CharField(max_length=256, primary_key=True)

	osc_friendly_name = models.CharField(max_length=256)
	osc_tenant_name = models.CharField(max_length=256)
	osc_username = models.CharField(max_length=50)
	osc_password = models.CharField(max_length=50)
	osc_auth_url = models.CharField(max_length=256)
	osc_type = models.CharField(max_length=24)
	osc_endpoint_type = models.CharField(max_length=24, default='public')
	osc_region_name = models.CharField(max_length=50)
	
	in_use = models.BooleanField(default=True)
	validated = models.BooleanField(default=False)

	#helper
	def __str__(self):
		return'For user %s -> %s:%s' % (self.user.username,self.uniqueid, self.osc_auth_url)
	def __unicode__(self):
		return self.__str__()

#Schema for individual task
class RallyTask(models.Model):
	#Deployment in use
	deployment_id = models.ForeignKey(Deployment)
	#Key
	task_id = models.CharField(max_length=50, primary_key=True)

	is_running = models.BooleanField(default=False)
	output_folder = models.CharField(max_length=256)
	

	

