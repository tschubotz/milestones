from github import Github
from github.InputFileContent import InputFileContent
from datetime import datetime

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

g = Github(TOKEN)

output = '_Last updated: {}_\n\n'.format(datetime.now())

for repo_name in REPOS:
    repo = g.get_repo(repo_name)
    

    output += '# [{}]({})\n\n'.format(repo.name, repo.html_url)

    open_milestones = repo.get_milestones(state='open')
    
    for milestone in open_milestones:
        
        # Milestones don't have .html_url, so creating it manually:
        milestone_html_url = '{}/milestone/{}'.format(repo.html_url, milestone.number)

        output += '### [{}]({}) {}/{} issues ({:.0f}%)\n\n'.format(
            milestone.title, 
            milestone_html_url,
            milestone.closed_issues,
            milestone.open_issues + milestone.closed_issues,
            100 * milestone.closed_issues / (milestone.open_issues + milestone.closed_issues))
        
        for issue in repo.get_issues(milestone=milestone, state='closed'):
            output += '- ✅ [{}]({})\n'.format(issue.title, issue.html_url)
        for issue in repo.get_issues(milestone=milestone, state='open'):
            output += '- 🏗 [{}]({})\n'.format(issue.title, issue.html_url)
    
    if open_milestones.totalCount == 0:
        output += 'Currently no milestones opens.\n\n'
            
gist = g.get_gist(GIST_ID)

gist.edit(
    description=GIST_DESCRIPTION,
    files={GIST_FILENAME: InputFileContent(content=output)},
)