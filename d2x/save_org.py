import json
import os
import sys
import coreapi
from cumulusci.core.exceptions import SfdxOrgException
from cumulusci.core.runtime import BaseCumulusCI
from cumulusci.core.sfdx import sfdx

org_name = sys.argv[1]

cci = BaseCumulusCI(load_keychain=True)
org = cci.keychain.get_org("feature")
p = sfdx("org display --verbose --json", org.username)
stderr_list = [line.strip() for line in p.stderr_text]
stdout_list = [line.strip() for line in p.stdout_text]

if p.returncode:
    self.logger.error(f"Return code: {p.returncode}")
    for line in stderr_list:
        self.logger.error(line)
    for line in stdout_list:
        self.logger.error(line)
    message = f"\nstderr:\n{nl.join(stderr_list)}"
    message += f"\nstdout:\n{nl.join(stdout_list)}"
    raise SfdxOrgException(message)

else:
    try:
        org_info = json.loads("".join(stdout_list))
    except Exception as e:
        raise SfdxOrgException(
            "Failed to parse json from output.\n  "
            f"Exception: {e.__class__.__name__}\n  Output: {''.join(stdout_list)}"
        )
  
org_config = org.config
org_config["sfdxAuthUrl"] = org_info["result"]["sfdxAuthUrl"]

auth = coreapi.auth.TokenAuthentication(
    scheme='Token',
    token=os.environ.get("D2X_CLOUD_TOKEN"),
)
client = coreapi.Client(auth=auth)
schema = client.get(os.environ.get("D2X_CLOUD_BASE_URL") + "/docs/")

client.action(schema, ['scratch-create-request','complete'], params={
  "id": os.environ.get("SCRATCH_CREATE_REQUEST_ID"),
  "org_config": org_config,
})
