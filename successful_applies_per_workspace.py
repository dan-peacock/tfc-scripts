import requests
import json

# Open the file in read mode
with open('credentials.json', 'r') as file:
    # Load JSON content from the file
    data = json.load(file)

token = data['token']
organization = data['organization']

# Fetch all workspace IDs
workspaces_url = f'https://app.terraform.io/api/v2/organizations/{organization}/workspaces'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/vnd.api+json'
}

response_workspaces = requests.get(workspaces_url, headers=headers)

if response_workspaces.status_code == 200:
    workspaces_data = response_workspaces.json().get("data", [])

    # Iterate through each workspace
    for workspace in workspaces_data:
        workspace_id = workspace.get("id")
        workspace_name = workspace.get("attributes", {}).get("name")

        # Run the script for each workspace ID
        url = f'https://app.terraform.io/api/v2/workspaces/{workspace_id}/runs'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Extract the status counts from the JSON response
            status_counts = response.json().get("meta", {}).get("status-counts", {})
            total_runs = status_counts.get("total", 0)

            # Print percentages on the same line
            output_line = f"Workspace Name: {workspace_name} - "
            for status, count in status_counts.items():
                if status != "total" and total_runs > 0 and count > 0:
                    percentage = (count / total_runs) * 100
                    output_line += f"{status}: {percentage:.2f}% | "

            print(output_line.rstrip(" | "))

        else:
            print(f"Error fetching runs for Workspace Name {workspace_name}. Status Code: {response.status_code}")

else:
    print(f"Error fetching workspaces. Status Code: {response_workspaces.status_code}")
