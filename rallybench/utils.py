import json
import sys
import subprocess
import re

from os import listdir
from os.path import isfile, join, isdir

class UserContext:

    def __init__(self, name, deployments, scenarios, args):
        
        self.username = name
        self.deployment = deployments
        self.scenarios  = scenarios 

        self.results    = {}
        self.args    = args.copy()

class RallyUtility:
        
    def __init__(self, rally_bindir=None, rally_datadir=None, rally_userdir=None):
        self.bindir = rally_bindir
        self.userdir = rally_userdir
        self.datadir = rally_datadir
        self.version = '0.0.1'
        self.cmdtable = {
                #/usr/bin/rally, /home/sudhakso, /icehouse.json, favouritedeployment-name
                'Deployment_create' : '%s/rally deployment create --file %s --name %s',
                #/usr/bin/rally, favouritedeployment-name
                'Deployment_check'  : '%s/rally deployment check %s',
                #/usr/bin/rally, rally/samples/tasks/scenarios/nova, scenario.json
                'Execute_rallytests' : '%s/rally -v --rally-debug task start %s/%s',
                #/usr/bin/rally, /home/sudhakso, taskid.html
                'View_report' : '%s/rally task report %s --out %s/%s',
                #/usr/bin/rally, /home/sudhakso, name
                'Deployment_destroy': '%s/rally deployment destroy %s',
                #/usr/bin/rally, /home/sudhakso, name
                'Deployment_list': '%s/rally deployment list'
                }
        self.supported_components = ['nova', 'neutron', 'cinder']
        
    #Construct        
    def deployment_create(self, deployment_friendly_name, 
            deployment_owner, 
            osc_type, 
            osc_auth_url, 
            osc_endpoint_type, 
            osc_region_name, 
            osc_tenant_name, 
            osc_tenant_user, 
            osc_tenant_password):

        #json file path (eg: /home/sudhakso/sudhakso.json
        deployment_json = '%s/%s.json' % (self.userdir,deployment_owner)
        deployment_id = -1
        #create temporary deployment file
        with open(deployment_json, "w") as jsonfile:
            #{
            #    "type": "ExistingCloud",
            #    "auth_url": "http://example.net:5000/v2.0/",
            #    "region_name": "RegionOne",
            #    "endpoint_type": "public",
            #    "admin": {
            #        "username": "admin",
            #        "password": "myadminpass",
                #      "tenant_name": "demo"
            #    }
            #}
            json.dump(
                    {"type": "ExistingCloud",
                        "auth_url": osc_auth_url,
                        "region_name": osc_region_name,
                        "endpoint_type": osc_endpoint_type,
                         "admin": {
                            "username":osc_tenant_user,
                            "password":osc_tenant_password,
                            "tenant_name": osc_tenant_name                    
                        }
                    }, jsonfile, indent=4)        
        rally_cmdline = self.cmdtable['Deployment_create'] % (self.bindir, deployment_json, deployment_friendly_name)
        matched_lines = []
        pat_to_match  = r'Using deployment?[ ]*\:[\s+]([-a-z0-9]*)'
        #run the command and match the result
        try :
            match = []
            (exitCode, output, matched_lines) = self.execute(rally_cmdline, pat_to_match)
            matches = len(matched_lines)
            #expecting a single match only
            if matches == 1:
                #success, [uuid]
                match = matched_lines[0] 
                deployment_id = match[0]                
        except Exception:
            pass            
        return deployment_id
    
    #Validate
    def deployment_check(self, deployment_friendly_name):
        
        depl_status = {}
        rally_cmdline = self.cmdtable['Deployment_check'] % (self.bindir, deployment_friendly_name)
        matched_lines = []
        pat_to_match  = r'\|[\s+]([a-zA-Z]*)\s+'
        #run the command and match the result
        try :
            (exitCode, output, matched_lines) = self.execute(rally_cmdline, pat_to_match)
            matches = len(matched_lines)
            #multi-line match, 
            #keystone endpoints are valid and following services are available:
            #+----------+----------+-----------+
            #| services | type     | status    |
            #+----------+----------+-----------+
            #| glance   | image    | Available |
            #| keystone | identity | Available |
            #| neutron  | network  | Available |
            #| nova     | compute  | Available |
            #+----------+----------+-----------+
            if matches > 0:
                #success, [nova, compute, available]..[neutron, network, available]
                for amatch in matched_lines:
                    if len(amatch) == 3: 
                        depl_status[amatch[0]] = amatch[2]                    
        except Exception:
                pass            
        return depl_status
    
      #Listing deployment
      #rally deployment list
      #+--------------------------------------+----------------------------+----------------------+------------------+--------+
      #| uuid                                 | created_at                 | name                 | status           | active |
      #+--------------------------------------+----------------------------+----------------------+------------------+--------+
      #| e0411659-23c4-4c67-861b-95abfc648e91 | 2014-07-17 21:54:12.674379 | existing             | deploy->finished |        |
      #| ec5cda02-69ef-4302-a32b-6e410206f957 | 2014-07-19 02:55:21.570264 | existing1            | deploy->finished |        |
      #| 972fc4e9-d203-486c-8a97-4747358c5166 | 2014-08-17 02:52:40.923453 | myfriendlydeployment | deploy->finished | *      |
      #+--------------------------------------+----------------------------+----------------------+------------------+--------+
    def deployment_list(self):
         pass

    #List scenarios
    def scenario_list(self):
    #{'nova':[], 'neutron':[], 'cinder':[]}
            lookupdir = []
	    lookupdir.append(self.datadir + '/rally/samples/tasks/scenarios/')
            lookupdir.append(self.datadir + '/rally/scenarios/')
            lookupdir.append(self.userdir + '/rally/scenarios/')

            scenario_by_type = {}
    
            for loc in lookupdir:
                if (isdir( loc)):
                    allcomponents = [ f for f in listdir(loc) if isdir(join(loc,f)) ]
                    c = set(self.supported_components).intersection(allcomponents)
                    for acomp in c:
			compdir = loc + acomp
                        allfiles_by_component = [ f for f in listdir(compdir) if isfile(join(compdir,f)) ]
                        scenario_by_type[acomp] = allfiles_by_component
                else:
                    pass
            return scenario_by_type    

    #Destroy
    def deployment_delete(self, deployment_friendly_name):
        pass
    
    def rally_run_scenarios(self, deployment_friendly_name, scenario_listing = []):
        pass
    
    def rally_launch_report(self, task_id):
        pass

    def load_cmd_table(self) :
        pass
   
    #Utility method to execute and list the (interested) output
    def execute(self, command, patmatch=None):        
        matched_lines = []
        print 'Executing %s' %(command)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            match = []
            nextline = process.stdout.readline()
            #print 'line - %s' %(nextline)
            if nextline == '' and process.poll() != None:
               break
            if patmatch == None:
                match.append(nextline)
                matched_lines.append(match)            
            else:
                match = re.findall(patmatch, nextline)
                #print 'after matched - %s' %(match)
                if match != None and len(match)>0:
                    matched_lines.append(match)
                    print 'after matched - %s' %(match)               
            
        output, stderr = process.communicate()
        exitCode = process.returncode
        if (exitCode == 0):
            return (exitCode, output, matched_lines)
        else:
            raise Exception((output,exitCode, stderr))


def main(args):
    print 'Creating...'
    scene_by_component = {}
    commander = RallyUtility('/usr/local/bin/', '/home/sudhakso/', '/home/sudhakso')
    #id = commander.deployment_create('myfriendlydeployment', 
    #                           'sudhakso', 'existing', 'http://junk:5000/v2.0/auth', 'public', '', 'admin', 'demo', 'iso*help')
    #print '######################' 
    #print id
    #print '######################'

    depls = commander.deployment_check('existing') 
    print '#####################' 
    print depls
    print '#####################'
    
    scene_by_component = commander.scenario_list()
    print '#####################' 
    print scene_by_component
    print '#####################'
    
if __name__ == '__main__':
    main(sys.argv)



