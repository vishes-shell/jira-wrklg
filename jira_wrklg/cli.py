import os
from collections import Counter
from configparser import ConfigParser
from datetime import datetime

import click
from jira import JIRA

APP_NAME = "Jira WorkLog"
JIRA_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def get_formatted_seconds(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@click.group()
@click.pass_context
def cli(ctx):
    app_path = click.get_app_dir(APP_NAME, force_posix=True)
    if not os.path.exists(app_path):
        os.makedirs(app_path)

    config_path = os.path.join(app_path, "config.ini")

    ctx.obj = {"config_path": config_path}


@cli.command(short_help="Init cli")
@click.option("--url", prompt=True)
@click.option("--username", prompt=True)
@click.option("--token", prompt=True, hide_input=True)
@click.pass_obj
def init(obj, token, username, url):
    config = ConfigParser()

    config.add_section("jira-wrklg")
    config.set("jira-wrklg", "url", url)
    config.set("jira-wrklg", "username", username)
    config.set("jira-wrklg", "token", token)

    config_path = obj["config_path"]
    with open(config_path, "w") as configfile:
        config.write(configfile)

    click.secho(f"We saved credentials in {click.format_filename(config_path)}")


@cli.command(short_help="Auth user")
@click.pass_obj
@click.pass_context
def auth(ctx, obj):
    config = ConfigParser()

    if not os.path.exists(obj["config_path"]):
        raise click.ClickException("You need to init first")

    config.read(obj["config_path"])

    jira = JIRA(
        options={"server": config.get("jira-wrklg", "url")},
        basic_auth=(
            config.get("jira-wrklg", "username"),
            config.get("jira-wrklg", "token"),
        ),
    )
    obj.update(jira=jira)


@cli.command(short_help="Time")
@click.option("--issues", "-i", "issues", multiple=True, help="issues")
@click.option(
    "--from",
    "from_",
    type=click.DateTime(["%d.%m.%Y", "%d.%m.%Y %H:%M"]),
    help="from time",
)
@click.option(
    "--to", "to_", type=click.DateTime(["%d.%m.%Y", "%d.%m.%Y %H:%M"]), help="to time"
)
@click.pass_obj
@click.pass_context
def time(ctx, obj, from_, to_, issues):
    ctx.invoke(auth)

    jira = obj["jira"]
    from_ = from_ or datetime.min
    to_ = to_ or datetime.max

    for issue in issues:
        worklogs = jira.worklogs(issue)
        click.secho(f"{issue}:", fg="blue", bold=True, nl=False)

        click.echo()
        counter = Counter()
        for worklog in worklogs:
            created_at = datetime.strptime(
                worklog.created, JIRA_DATETIME_FORMAT
            ).replace(tzinfo=None)

            if from_ < created_at < to_:
                counter[worklog.author.displayName] += worklog.timeSpentSeconds

                click.secho(f"\t{worklog.author.displayName}: ", nl=False)
                click.secho(
                    get_formatted_seconds(worklog.timeSpentSeconds), fg="cyan", nl=False
                )
                click.secho(f" (created {created_at:%d.%m.%Y %H:%M})")
            else:
                updated_at = datetime.strptime(
                    worklog.updated, JIRA_DATETIME_FORMAT
                ).replace(tzinfo=None)

                if from_ < updated_at < to_:
                    click.secho(f"\t{worklog.author.displayName}: ", nl=False)
                    click.secho(
                        f"{get_formatted_seconds(worklog.timeSpentSeconds)} (changed)",
                        fg="red",
                    )
                    click.secho(
                        f" (created: {created_at:%d.%m.%Y %H:%M} | updated: {updated_at:%d.%m.%Y %H:%M})"
                    )

        if not counter:
            click.secho("\tNo new time", fg="cyan")
        else:
            click.secho("\n\tTotal:", fg="cyan")
            for author, time in counter.items():
                click.secho(f"\t\t{author}: ", nl=False)
                click.secho(get_formatted_seconds(time))
