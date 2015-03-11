import json
import sys
import subprocess
import re

class UserContext:

	def __init__(self, name, deployments, scenarios, args):
		
		self.username = name
		self.deployment = deployments
		self.scenarios  = scenarios 

		self.results	= {}
		self.args	= args.copy()

class RallyUtility:
        
    def __init__(self, rally_installdir=None, rally_datadir=None):
        self.installdir = rally_installdir
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
		'Deployment_destroy', '%s/rally deployment destroy %s',
                }
        
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
        deployment_json = '%s/%s.json' % (self.datadir,deployment_owner)
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
                         osc_tenant_name: {
                            "username":osc_tenant_user,
                            "password":osc_tenant_password,
                            "tenant_name": osc_tenant_name                    
                        }
                    }, jsonfile, indent=4)        
        rally_cmdline = self.cmdtable['Deployment_create'] % (self.installdir, deployment_json, deployment_friendly_name)
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
        rally_cmdline = self.cmdtable['Deployment_check'] % (self.installdir, deployment_friendly_name)
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
    
    #Destroy
    def deployment_delete(self, deployment_friendly_name):
        pass
    
    def rally_scenarios_list(self, component_types = {'neutron', 'nova'}):
        scene_by_type_list = []    
        scene_neutron_tuple = ('neutron', 'sample_scene')
        scene_nova_tuple = ('nova', 'sample_scene')
        
        scene_by_type_list.append(scene_neutron_tuple)
        scene_by_type_list.append(scene_nova_tuple)

        return scene_by_type_list

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
    commander = RallyUtility('/usr/local/bin/', '/home/sudhakso')
    id = commander.deployment_create('myfriendlydeployment', 
                                'sudhakso', 'existing', 'http://junk:5000/v2.0/auth', 'public', '', 'admin', 'demo', 'iso*help')
    print '######################' 
    print id
    print '######################'

    depls = commander.deployment_check('existing') 
    print '#####################' 
    print depls
    print '#####################'
    
if __name__ == '__main__':
    main(sys.argv)



