from github import Github
from github.GithubObject import NotSet
from github.InputFileContent import InputFileContent
from datetime import datetime, timedelta
import urllib
import requests

GITHUB_TOKEN = ''
GIST_ID = ''
GIST_DESCRIPTION = ''
GIST_FILENAME = ''
GIST_ID = '0862e975ef2d8e180c416422d85dd031'
GIST_DESCRIPTION = 'Gnosis Safe milestones overview'
GIST_FILENAME = 'safe_milestones.md'

ZENHUB_TOKEN = ''
ZENHUB_WORKSPACE_ID = '5c1b98250e13551e8aae81eb'
ZENHUB_OPEN_PIPELINE_IDS = [
    '5c360b257727940fef836846',  # Dev Backlog
    '5c1b98250e13551e8aae81e8',  # Dev In Progress
    '5c1b98250e13551e8aae81e9',  # Dev Review/QA 
    '5c1b98250e13551e8aae81ea'  # Done
]

REPOS_M = [
    # Repositories that should be checked for open milestones.
    'gnosis/safe-react',
    'gnosis/safe-android',
    'gnosis/safe-ios',
    'gnosis/safe-browser-extension',
    'gnosis/safe-contracts'
]

REPOS_P = [
    # Repositories that don't use milestones, but instead Zenhub pipelines to get an overview.
    'gnosis/safe-relay-service',
    'gnosis/safe-notification-service',
    'gnosis/safe-transaction-service'
]

def main():
    g = Github(GITHUB_TOKEN)

    output = '_Last updated on {}_\n\n'.format(datetime.now())

    # Go through the given repositories that use milestones
    for repo_name in REPOS_M:
        repo = g.get_repo(repo_name)
        
        # Print repo header
        output += '# [{}]({})\n\n'.format(repo.name, repo.html_url)

        # Only check open milestones
        open_milestones = repo.get_milestones(state='open')
        
        # Go through all open milestones
        for milestone in open_milestones:
            
            # Milestones don't have .html_url, so creating it manually:
            milestone_html_url = '{}/milestone/{}'.format(repo.html_url, milestone.number)
            
            # Print milestone header including progress and due date.
            output += '### [{}]({}) {}/{} issues ({:.0f}%) - Due on {}\n\n'.format(
                milestone.title, 
                milestone_html_url,
                milestone.closed_issues,
                milestone.open_issues + milestone.closed_issues,
                100 * milestone.closed_issues / (milestone.open_issues + milestone.closed_issues),
                milestone.due_on.date() if milestone.due_on else '???')
            
            # Go through all issues. First the closed ones, then the open ones
            output += process_issues(repo, 'closed', milestone=milestone)
            output += process_issues(repo, 'open', milestone=milestone)
        
        if open_milestones.totalCount == 0:
            output += 'No milestones open.\n\n'

    # Go through the given repositories that don't use milestones. 
    for repo_name in REPOS_P:
        repo = g.get_repo(repo_name)
        
        # Print repo header
        output += '# [{}]({})\n\n'.format(repo.name, repo.html_url)

        # Get closed issues that were closed within the last week.
        last_week = datetime.today() - timedelta(days=7)
        output_closed_issues = process_issues(repo, 'closed', since=last_week)
        
        # Now get all open issues.
        output_open_issues = process_issues(repo, 'open')
        
        # Check if there was actually something to be printed.
        if (len(output_closed_issues) + len(output_open_issues)) > 0:
            # Print info
            output += '_Not based on milestones._\n_✅ -> Closed within the last 7 days._\n_🏗 -> In columns `Dev Backlog/In Progress/Review/QA` or `Done`_\n\n'
            output += output_closed_issues
            output += output_open_issues
        else:
            output += 'No issues to show.\n\n'
    
    # Write gist.        
    gist = g.get_gist(GIST_ID)

    gist.edit(
        description=GIST_DESCRIPTION,
        files={GIST_FILENAME: InputFileContent(content=output)},
    )

    # Print success and gist url for easy access.
    print('View output at {}'.format(gist.html_url))

def process_issues(repo, state, since=NotSet, milestone=NotSet):
    output = ''
    num_bugs = 0

    icon = '✅' if state == 'closed' else '🏗'

    for issue in repo.get_issues(milestone=milestone, state=state, since=since):
        if repo.full_name in REPOS_P:
            # If pipelines should we respected.
            request = requests.get('https://api.zenhub.io/p1/repositories/{}/issues/{}?access_token={}'.format(
                repo.id,
                issue.number,
                ZENHUB_TOKEN
            ))

            response = request.json()
            discard = True
            for pipeline in response.get('pipelines'):
                if pipeline.get('workspace_id') == ZENHUB_WORKSPACE_ID and pipeline.get('pipeline_id') in ZENHUB_OPEN_PIPELINE_IDS:
                if (pipeline.get('workspace_id') == ZENHUB_WORKSPACE_ID) and (pipeline.get('pipeline_id') in ZENHUB_OPEN_PIPELINE_IDS):
                    discard = False
                    break
            if discard:
                continue
        

        # Aggregate bug tickets to not clutter the output.
        if 'bug' in [label.name for label in issue.labels]:
            num_bugs += 1
        else:
            # Get task info.
            closed_tasks = get_tasks(issue, 'closed')
            open_tasks = get_tasks(issue, 'open')
            num_tasks = len(closed_tasks) + len(open_tasks)

            output += '- {} [{}]({})'.format(icon, issue.title, issue.html_url)

            if num_tasks > 0:
                output += ' ({}/{} {})\n'.format(
                    len(closed_tasks),
                    num_tasks,
                    'task' if num_tasks == 1 else 'tasks'
                    )
                # Uncomment if tasks should be printed as well.
                # for task in closed_tasks:
                #     output += '  - ✅ {}\n'.format(task)
                # for task in open_tasks:
                #     output += '  - 🏗 {}\n'.format(task)
            else:
                output += '\n'

    # Print aggregated info on bugs
    if num_bugs > 0:
        bugs_url = '{}/issues?q=is%3Aissue+is%3A{}+label%3Abug'.format(
            repo.html_url,
            state
        )
        if milestone != NotSet:
            bugs_url += '+milestone%3A%22{}%22'.format(urllib.parse.quote_plus(milestone.title))

        output += '- {} [{} {}]({})\n'.format(
            icon, 
            num_bugs, 
            'bug' if num_bugs == 1 else 'bugs',
            bugs_url)
    return output

def get_tasks(issue, state):
    tasks = []
    lines = issue.body.split('\n')
    for line in lines:
        if line.startswith('- [ ]' if state == 'open' else '- [x]'):
            tasks.append(line[5:])
    return tasks

if __name__ == "__main__":
    main()