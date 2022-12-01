import json
import requests
import sys
from github import Github
from urllib import response


def main(args):
    if not len(args) == 3:
        print("Format of command is snyk-auto-importer.py <GITHUB-TOKEN> <SNYK-TOKEN>")
        return

    github_token = args[1]
    if not len(github_token) == 40:
        print("Invalid github token")
        return

    snyk_token = args[2]
    if not len(snyk_token) == 36:
        print("Invalid Snyk Token")
        return

    # These are fake for the purpose of the exercise
    # Also, these aren't sensitive at all
    git_integration_id = "1275b88c-84a4-422a-8036-f31efc4d5397"
    org_id = "69842c18-7d95-4919-82c7-541b34f29c20"
    github_org_name = "NopSledding"

    # Get list of projects in the Snyk org to compare to
    headers = {
        'Authorization': 'token ' + snyk_token,
        'Content-Type': 'application/json'
    }

    existing_project_list = []

    snyk_projects = {
        "Projects": {

        }
    }

    try:
        response = requests.post(
            f"https://api.snyk.io/api/v1/org/{org_id}/projects", headers=headers)
        snyk_projects = json.loads(response.text.encode('utf8'))
    except Exception as e:
        print(f'Exception thrown in Snyk API call: {e}')

    for project in snyk_projects["projects"]:
        name = project["name"].split(':', 1)[0].replace(
            f'{github_org_name}/', '')

        # Sometimes the same project list will show up for multiple manifests.
        if name in existing_project_list:
            continue
        existing_project_list.append(name)

    # Now we iterate over all our repositories and tell Snyk to go get the ones we don't have
    git = Github(github_token)
    repo_list = sorted(git.get_organization(
        f'{github_org_name}').get_repos('all'), key=lambda repo: repo.name)

    for repo in repo_list:
        try:
            if repo.name in existing_project_list:
                continue

            print(f'Attempting to import {repo.name} into Snyk!')

            url = f'https://api.snyk.io/api/v1/org/{org_id}/integrations/{git_integration_id}/import'

            body = {
                'target': {
                    'owner': repo.owner.login,
                    'name': repo.name,
                    'branch': repo.default_branch
                }
            }

            response = requests.post(
                url, data=json.dumps(body), headers=headers)
            print(response)

        except Exception as e:
            print(f'Exception thrown: {e}')


main(sys.argv)
