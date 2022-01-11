#!/usr/bin/env python3

import click
import sys
import readline
import traceback
from berlin.backend_dict import BackendDict
from berlin.commands import CommandHandler
from berlin.code_type import get_code_bank

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    click.echo("""
berliner   Z 9001
-----------------
Wilkommen, bienvenue, welcome. Come on in!

OS
    """.strip())

    if ctx.invoked_subcommand is None:
        interactive()

@cli.command()
def consistency(self):
    interactive('CONSISTENCY')

def interactive(command=None):
    code_bank = load()

    handler = CommandHandler(code_bank, printer=click.echo)
    if command:
        click.echo("> ", nl=False)
        handler.run(command)
    else:
        readline.parse_and_bind('set editing-mode vi')
        line = ""
        while True:
            line = input("> ").strip()
            if line:
                if line == 'QUIT':
                    break

                if line == 'REBUILD':
                    code_bank = load(rebuild=True)
                    handler.set_code_bank(code_bank)
                else:
                    line = line.split(' ')
                    command, arguments = line[0], line[1:]
                    try:
                        handler.run(command, *arguments)
                    except Exception as e:
                        traceback.print_exc()
            click.echo()

def load(rebuild=False):
    data_sources = {
        'iata_file': 'data/locode/airport-codes/data/airport-codes.csv',
        'state_file': 'data/locode/country-codes/data/country-codes.csv',
        'subdiv_file': [
            'data/locode/un-locode/data/subdivision-codes.csv',
            'data/locode/iso-3166-2/iso_3166_2.js',
        ],
        'locode_file': 'data/locode/un-locode/data/code-list.csv'
    }

    return get_code_bank(data_sources, build_combined=True, progress_bar=True, force_rebuild=rebuild)


if __name__ == '__main__':
    cli()
