from github import Github
from github.InputFileContent import InputFileContent
from datetime import datetime
import urllib

TOKEN = ''
GIST_ID = ''
GIST_DESCRIPTION = ''
GIST_FILENAME = ''

REPOS = [
    'gnosis/safe-react',
    'gnosis/safe-android',
    'gnosis/safe-ios',
    'gnosis/safe-browser-extension',
    'gnosis/safe-relay-service',
]

def main():
    g = Github(TOKEN)

    output = '_Last updated: {}_\n\n'.format(datetime.now())

    # Go through the given repositories
    for repo_name in REPOS:
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
                milestone.due_on.date())
            
            # Go through all issues. First the closed ones, then the open ones
            output += process_issues(repo, milestone, 'closed')
            output += process_issues(repo, milestone, 'open')
        
        if open_milestones.totalCount == 0:
            output += 'Currently no milestones opens.\n\n'

    # Write gist.        
    gist = g.get_gist(GIST_ID)

    gist.edit(
        description=GIST_DESCRIPTION,
        files={GIST_FILENAME: InputFileContent(content=output)},
    )

    # Print success and gist url for easy access.
    print('View output at {}'.format(gist.html_url))

def process_issues(repo, milestone, state):
    output = ''
    num_bugs = 0

    icon = '✅' if state == 'closed' else '🏗'

    for issue in repo.get_issues(milestone=milestone, state=state):
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
        bugs_url = '{}/issues?q=is%3Aissue+is%3A{}+label%3Abug+milestone%3A%22{}%22'.format(
            repo.html_url,
            state,
            urllib.parse.quote_plus(milestone.title)
        )
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