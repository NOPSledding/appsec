import datetime
import sys
from github import Github, UnknownObjectException


def create_codeowners_pr(repository):
    dt_now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    branch_name = f'Adding-CO-{dt_now}'
    file_reader = open("./CODEOWNERS", "r")
    codeowners_contents = file_reader.read()
    file_reader.close()

    try:
        repository.create_file(
            'CODEOWNERS', 'Creating CODEOWNERS File', codeowners_contents, branch_name)
        repository.create_pull(title='Creating missing CODEOWNERS File',
                               body='Creating necessary CODEOWNERS file for audit requirements', base=repository.default_branch, head=branch_name)
    except Exception as e:
        print(f'Exception thrown during github api calls: {e}')


def main(args):

    if not len(args) == 2:
        print("Format of command is repository-owner-checkup.py <GITHUB-TOKEN>")
        return

    github_token = args[1]
    if not len(github_token) == 40:
        print("Invalid Github token")
        return

    # This is fake for the purpose of the exercise
    github_org_name = "NOPSledding"

    try:
        git = Github(github_token)
        repo_list = sorted(git.get_organization(
            f'{github_org_name}').get_repos('all'), key=lambda repo: repo.name)
        for repo in repo_list:
            found_co_file = False
            try:
                codeowners_file = repo.get_contents(
                    "CODEOWNERS", ref=repo.default_branch)
                # If exception was not thrown, it found the CODEOWNERs file
                found_co_file = True
            except UnknownObjectException as e:
                print(
                    f'CODEOWNERS file not found in {repo.name}. Creating PR!')

            if not found_co_file:
                create_codeowners_pr(repo)

    except Exception as e:
        print(f'Exception thrown: {e}')


main(sys.argv)
