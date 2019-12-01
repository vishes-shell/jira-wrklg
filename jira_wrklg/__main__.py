try:
    from jira_wrklg import cli
except ImportError:
    from . import cli

cli.cli()
