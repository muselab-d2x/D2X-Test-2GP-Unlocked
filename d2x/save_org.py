import json
import os
import sys
import coreapi
from cumulusci.core.exceptions import SfdxOrgException
from cumulusci.cli.runtime import CliRuntime
from cumulusci.core.sfdx import sfdx

org_name = sys.argv[1]

cci = CliRuntime(load_keychain=True)
org = cci.keychain.get_org("feature")
print("Creating scratch org")
print(f"Username: {org.username}")
cci.keychain.set_org(org)
print("Getting sfdxAuthUrl from sfdx")
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

org.config["date_created"] = org.config["date_created"].isoformat()
org.config["sfdxAuthUrl"] = org_info["result"]["sfdxAuthUrl"]

print("Instantiating coreapi client")
auth = coreapi.auth.TokenAuthentication(
    scheme="Token",
    token=os.environ.get("D2X_CLOUD_TOKEN"),
)
client = coreapi.Client(auth=auth)
print("Getting schema")
schema = client.get(os.environ.get("D2X_CLOUD_BASE_URL") + "/docs/")

print("Calling scratch-create-requests/complete")

client.action(
    schema,
    ["scratch-create-requests", "complete"],
    params={
        "id": os.environ.get("SCRATCH_CREATE_REQUEST_ID"),
        "org_config": org.config,
    },
)
create_request = client.action(
    schema,
    ["scratch-create-request", "read"],
    params={
        "id": os.environ.get("SCRATCH_CREATE_REQUEST_ID"),
    },
)

print(f"D2X URL: {create_request['org_users'][0]['d2x_url']}")
