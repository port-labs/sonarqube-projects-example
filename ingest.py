## Import the needed libraries
import requests
from decouple import config

# Get environment variables using the config object or os.environ["KEY"]
# These are the credentials passed by the variables of your pipeline to your tasks and in to your env
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

def retrieve_sonarqube_projects():
    """A function to make API request to SonarQube and retrieve projects within an organization"""

    ## get SonarQube components/projects within the account
    headers = {'Authorization': f'Bearer {SONARQUBE_TOKEN}'}
    components_response = requests.get(f'{SONARQUBE_URL}/api/components/search?organization={SONARQUBE_ORGANIZATION_ID}', headers=headers)
    components = components_response.json()['components']

    # ## Iterate through the components array and create port entities
    for component in components:
        entity_body = {
        "identifier": component["key"],
        "title": component["name"],
        "properties": {
            "serverUrl": SONARQUBE_URL,
            "projectName": component["name"],
            "projectUrl": f'{SONARQUBE_URL}/project/overview?id={component["key"]}'
        },
        "relations": {}
        }
        create_port_entity(entity_body)

retrieve_sonarqube_projects()