'''
--- Command Line Interface ---
 - run flight_update through a cli
 - options to set logging/paths/update mode/change settings file 
'''


import click

import sys

# set archive path
# set path of dir where flights to be pushed are located
# set logging to true/false
# set logging to file or console 
# set to update mode
# set to add mode
# option to change settings.json? hosts, api key

@click.command()
@click.option('--logging', default=1, help='Set to True/False', prompt='Enable logging (y/n):')
@click.option('--enable_console_logging', default=1, help='Set to True/False', prompt='Log to console (y/n):')
@click.option('--archive_path', default=1, help='Set to True/False', prompt='Set archive path:')
@click.option('--flights_dir', default=1, help='Set to True/False', prompt='Set path to flights to be pushed:')
@click.option('--add_mode', default=1, help='Set to True/False', prompt='Set to mode to add (y/n):')
@click.option('--update_mode', default=1, help='Set to True/False', prompt='Set to update mode (y/n):')
@click.option('--update_settings', default=1, help='Update settings.json file', prompt='Update settings.json file (y/n):')


def str2bool(v):
    """
    Input parameter: Str
    Returns: Bool based on whether the string is part of list
    """
    return v.lower() in ("y", "yes", "true", "t", "1")


def main(logging, enable_console_logging, archive_path, flights_dir, add_mode, update_mode, update_settings):

    return 0

if __name__ == '__main__':
    main()