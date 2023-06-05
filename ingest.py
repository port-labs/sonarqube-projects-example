## Import the needed libraries
import requests
from decouple import config

# Get environment variables using the config object or os.environ["KEY"]
SONARQUBE_ORGANIZATION_ID = config("SONARQUBE_ORGANIZATION_ID")
SONARQUBE_URL = config("SONARQUBE_URL")
SONARQUBE_TOKEN = config("SONARQUBE_TOKEN")
PORT_CLIENT_ID = config("PORT_CLIENT_ID")
PORT_CLIENT_SECRET = config("PORT_CLIENT_SECRET")
PORT_API_URL = "https://api.getport.io/v1"


## Get Access Token
credentials = {'clientId': PORT_CLIENT_ID, 'clientSecret': PORT_CLIENT_SECRET}
token_response = requests.post(f'{PORT_API_URL}/auth/access_token', json=credentials)
access_token = token_response.json()['accessToken']

# You can now use the value in access_token when making further requests
headers = {
	'Authorization': f'Bearer {access_token}'
}

blueprint_id = 'sonarCloudAnalysis'
sonarqube_headers = {'Authorization': f'Bearer {SONARQUBE_TOKEN}'}

def create_port_entity(entity_object):
    """A function to create the passed entity in Port

    Params
    --------------
    entity_object: dict
        The entity to add in your Port catalog
    
    Returns
    --------------
    response: dict
        The response object after calling the API
    """
    response = requests.post(f'{PORT_API_URL}/blueprints/{blueprint_id}/entities?upsert=true&merge=true', json=entity_object, headers=headers)
    print(response.json())

def fetch_branches(project_key):
    """A function to retrieve branch information from a project"""

    api_url = f"{SONARQUBE_URL}/api/project_branches/list?project={project_key}"

    response = requests.get(api_url, headers=sonarqube_headers)
    if response.status_code == 200:
        data = response.json()
        branches = data.get("branches", [])
        main_branch = [branch for branch in branches if branch.get("isMain")]
        return main_branch[0]
    else:
        print(f"Error: {response.status_code}")
        return []

def fetch_project_status(project_key):
    """A function to get the quality gate status of a project"""

    api_url = f"{SONARQUBE_URL}/api/qualitygates/project_status?projectKey={project_key}"

    response = requests.get(api_url, headers=sonarqube_headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("projectStatus", {})
    else:
        print(f"Error: {response.status_code}")
        return {}

def fetch_quality_gate_name(organization, project_key):
    """A function to get the quality gate of a project"""

    api_url = f"{SONARQUBE_URL}/api/qualitygates/get_by_project?organization={organization}&project={project_key}"

    response = requests.get(api_url, headers=sonarqube_headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("qualityGate", {}).get("name", "")
    else:
        print(f"Error: {response.status_code}")
        return ""
    
def retrieve_sonarqube_projects():
    """A function to make API request to SonarQube and retrieve projects within an organization"""

    components_response = requests.get(f'{SONARQUBE_URL}/api/components/search?organization={SONARQUBE_ORGANIZATION_ID}', headers=sonarqube_headers)
    components = components_response.json()['components']
    return components

def get_coverage(quality_gate_conditions):
    """Returns the coverage value from the quality gates conditions"""
    for condition in quality_gate_conditions:
        condition_metric = condition.get("metricKey", "")
        condition_value = condition.get("actualValue", "")
        if condition_metric == "coverage":
            return condition_value
    return 0


components = retrieve_sonarqube_projects()

## Iterate through the components array and create port entities
for component in components:
    ## get project level information
    projectId = component["key"]
    projectName = component["name"]
    projectUrl = f"{SONARQUBE_URL}/project/overview?id={projectId}"

    ## fetch other information from API
    branches = fetch_branches(projectId)
    project_status = fetch_project_status(projectId)
    quality_gate_name = fetch_quality_gate_name(SONARQUBE_ORGANIZATION_ID, projectId)

    # Process the fetched data
    if branches and project_status and quality_gate_name:

        qualityGateStatus = branches.get("status", {}).get("qualityGateStatus", "")
        qualityGateConditions = project_status.get("conditions", [])
        coverage = get_coverage(qualityGateConditions)

        branchName = branches.get("name", "")
        branchType = branches.get("type", "")
        branchUrl = f"{SONARQUBE_URL}/summary/new_code?id={projectId}"
        status = project_status.get("status", "")

        entity_body = {
        "identifier": projectId,
        "title": projectName,
        "properties": {
            "serverUrl": SONARQUBE_URL,
            "status": status,
            "projectName": projectName,
            "projectUrl": projectUrl,
            "branchName": branchName,
            "branchType": branchType,
            "branchUrl":  branchUrl,
            "qualityGateName": quality_gate_name,
            "qualityGateStatus": qualityGateStatus,
            "qualityGateConditions": qualityGateConditions,
            "coverage": coverage
        },
        "relations": {}
        }
        create_port_entity(entity_body)