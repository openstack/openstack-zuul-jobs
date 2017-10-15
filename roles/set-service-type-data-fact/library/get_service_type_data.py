# Copyright (C) 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            project_name=dict(type='str'),
            service_types_file=dict(type='str'),
        ),
    )

    project_name = module.params['project_name']
    service_types_file = module.params['service_types_file']

    service_data = json.load(open(service_types_file, 'r'))
    if project_name in service_data['primary_service_by_project']:
        module.exit_json(
            service_data['primary_service_by_project'][project_name])
    else:
        module.fail_json(
            msg='Project {name} is not in the Service Types Authority'.format(
                name=project_name))


if __name__ == '__main__':
    main()
