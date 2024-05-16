#!powershell
#Requires -Module Ansible.ModuleUtils.Legacy
#AnsibleRequires -CSharpUtil Ansible.Basic

# s.fauquembergue(sii)
# v1.0
# 13/05/2024
# initial release

from ansible.module_utils.basic import AnsibleModule
import apt, sys, subprocess

def Get_Resources (parameters):
    resources = None
    
    for a in apt.Cache():
        if a.name == parameters['name']:
            if parameters['version'] in apt.Cache()[parameters['name']].versions or parameters['version'] == "latest" :
                resources = {
                    "name": a.name,
                    "version": a.versions[0].version,
                    "is_installed": a.is_installed,
                }

    return resources


def Test_Resources (resource, parameters):
    compliant = True

    for p in parameters.keys():
        if resource[p] != parameters[p]:
            if not (p == "version" and parameters[p] == "latest"):
                compliant = False

    return compliant


def Set_Resources (parameters):
    if parameters['is_installed'] :
        cmd = "apt install " + parameters['name'] 
    else:
        cmd = "apt remove " + parameters['name'] 

    if parameters['version'] != "latest":
        cmd = cmd + "=" + parameters['version']

    cmd = cmd + " -y"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(result.stderr)   
    
#region main
def main():
    module_args = dict(
        name = dict(required=True, type='str'),
        version = dict(required=False, type='str'),
        is_installed = dict(required=False, type='bool')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(
        changed=False,
        skipped=False,
        message=None
    )

    try:       
        resources = Get_Resources(module.params)
        result['message'] = resources

        if resources:
            compliance = Test_Resources(resources, module.params)

            if not compliance:
                result['message'] = Set_Resources(module.params)
                result['changed'] = True

        else:
            result['message'] = Set_Resources(module.params)
            result['changed'] = True

    except:
        result['message'] = sys.exc_info()[1]

    finally:
        module.exit_json(**result)

if __name__ == '__main__':
    main()

#endregion
