# Jira-wrklg to get worklog from jira


Fetch token from https://confluence.atlassian.com/cloud/api-tokens-938839638.html

```shell
python3 -m pip install git+https://github.com/vishes-shell/gitlab-mr.git
jira-wrklg init
# provide all prompt data
jira-wrklg time -i ISSUE-1 -i ISSUE-123 --from 01.01.1970 01:20 --to 10.01.2043
# get your worklog time for ISSUE-1 and ISSUE-123 from 01.01.1970 01:20 to 10.01.2043
```
