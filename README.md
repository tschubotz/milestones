# Milestones
Fetch info and details about milestones of Github repos and their issues in order to put the info into a gist.

1. `pip install -r requirements.txt`
2. Generate Github API token and put into `GITHUB_TOKEN`. Make sure it can edit gists.
3. Create a gist and put its id into `GIST_ID`
4. Put the description of your gist info `GIST_DESCRIPTION`
5. Put the filename of your gist info `GIST_FILENAME`
6. Generate Zenhub API token and put into `ZENHUB_TOKEN`
7. Put your Zenhub workspace id into `ZENHUB_WORKSPACE_ID`
8. Put list of Zenhub pipeline ids that contain open issues into `ZENHUB_OPEN_PIPELINE_IDS`
9. Put the list of repositories that base releases on milestones into `REPOS_M`
10. Put the list of repositories that don't use milestones into `REPOS_P`
11. `python run.py`
