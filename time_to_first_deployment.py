import requests
import json
from datetime import datetime

with open('credentials.json', 'r') as file:
    # Load JSON content from the file
    data = json.load(file)

token = data['token']
organization = data['organization']


url = f'https://app.terraform.io/api/v2/organizations/{organization}/workspaces'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/vnd.api+json'
}

response = requests.get(url, headers=headers)

workspace_list = []

if response.status_code == 200:
    workspaces_data = response.json().get("data", [])

    for workspace in workspaces_data:
        workspace_name = workspace.get("attributes", {}).get("name")
        created_at_workspace = workspace.get("attributes", {}).get("created-at")
        workspace_list.append((workspace_name, created_at_workspace))

        # Make subsequent API call for each workspace ID
        state_version_url = f'https://app.terraform.io/api/v2/state-versions?filter%5Bworkspace%5D%5Bname%5D={workspace_name}&filter%5Borganization%5D%5Bname%5D={organization}'
        state_version_response = requests.get(state_version_url, headers=headers)

        if state_version_response.status_code == 200:
            state_versions_data = state_version_response.json().get("data", [])

            if state_versions_data:
                # Extract the oldest state file creation time
                oldest_state_created_at = min(
                    state["attributes"]["created-at"] for state in state_versions_data
                )

                # Convert string dates to datetime objects for calculation
                created_at_workspace_dt = datetime.fromisoformat(created_at_workspace[:-1])  # Remove 'Z' at the end
                oldest_state_created_at_dt = datetime.fromisoformat(oldest_state_created_at[:-1])

                # Calculate the time difference (state - workspace)
                time_difference = oldest_state_created_at_dt - created_at_workspace_dt

                # Calculate days, hours, and minutes
                days, seconds = divmod(time_difference.total_seconds(), 86400)
                hours, seconds = divmod(seconds, 3600)
                minutes, seconds = divmod(seconds, 60)

                print(f"Workspace Name: {workspace_name}")
                print(f"Time to first apply: {int(days)} days, {int(hours)} hours, {int(minutes)} minutes\n")
            else:
                print(f"No state versions found for the workspace: {workspace_name}\n")
        else:
            print(f"Error fetching State Versions for Workspace {workspace_name}. Check your request or API status.\n")
else:
    print("Error fetching data. Check your request or API status.")
