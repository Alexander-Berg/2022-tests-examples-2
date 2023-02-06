from yt.wrapper.client import YtClient

from argparse import ArgumentParser
from os import getenv
from sys import stderr, stdout
import subprocess
import click


@click.group()
def main():
    pass


def get_url(row):
    if "url" in row:
        yield {"Url": row["url"]}


@click.command(help="Read fetcher logs")
@click.option("--proxy", help="YT proxy (YT_PROXY)", default=getenv("YT_PROXY", "hahn"), show_default=True, type=str)
@click.option("--yt-token", help="YT token (YT_TOKEN)", default=getenv("YT_TOKEN"), type=str)
@click.option("--src", help="Logs source table path", required=True, multiple=True, type=str)
@click.option("--dst", help="Destination table path", required=True, type=str)
@click.option("--row-count", help="Destination table row count", required=True, type=int)
@click.option("--out", help="Path to urls list file", required=True, type=str)
def read(proxy, src, dst, row_count, out, yt_token):
    assert dst not in src, "Error: overwrite requested"

    yt = YtClient(proxy=proxy, token=yt_token)

    in_row_count = sum((yt.row_count(t) for t in src), 0)
    sampling_rate = min(float(row_count) / in_row_count, 1.0)

    yt.run_map(
        binary=get_url,
        source_table=src,
        destination_table=dst,
        job_io={"table_reader": {"sampling_rate": sampling_rate}}
    )

    with open(out, "w") as f:
        for row in yt.read_table(dst):
            f.write(row["Url"] + "\n")


@click.command(help="Run test requests")
@click.option("--input", help="Path to urls list file", required=True, type=str)
@click.option("--client", help="Zora client tool path", default="zoracl", show_default=True, type=str)
@click.option("--source", help="Source type", default="any", show_default=True, type=str)
@click.option("--server", help="Server address", required=True, type=str)
def run(input, client, server, source):
    urls = open(input, "r").read()

    args = [
        client, "fetch",
        "-e",
        "--server", server,
        "--source", source,
        "--timeout", "10",
        "--send-timeout", "10",
        "--connect-timeout", "10",
        "--total-timeout", "3600"
    ]
    with subprocess.Popen(args, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr) as head:
        head.communicate(urls)


if __name__ == "__main__":
    main.add_command(read)
    main.add_command(run)
    main()
