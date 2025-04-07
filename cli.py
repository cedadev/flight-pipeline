import click
import sys
from flight_update import addFlights, updateFlights, openConfig

root, archive = openConfig()

# Helper function for converting string to boolean
def str2bool(v):
    """
    Input parameter: Str
    Returns: Bool based on whether the string is part of list
    """
    return v.lower() in ("y", "yes", "true", "t", "1")

@click.group()
def main():
    """Command Line Interface for flight update"""
    pass

@main.command()
@click.option('--logging', default="y", type=bool, help='Enable logging (True/False)', prompt='Enable logging (y/n)')
@click.option('--enable_console_logging', default="n", type=bool, help='Log to console (True/False)', prompt='Log to console (y/n)')
@click.option('--archive_path', default=archive, required=True, help='Set archive path', prompt='Set archive path')
@click.option('--flights_dir', default=root, required=True, help='Set path where flights will be pushed', prompt='Set path to flights to be pushed')
@click.option('--add_mode', default="y", type=str, help='Set mode to just add flights', prompt='Set mode to add flights (y/n)')
@click.option('--update_mode', default="n", type=str, help='Set mode to update flights', prompt='Set update mode (y/n)')
@click.option('--update_id', default="n", type=str, help='Update based on specific id', prompt='Flight id to update')



def run_flight_update(logging, enable_console_logging, archive_path, flights_dir, add_mode, update_mode, update_id):
    """
    Main function running the flight_update.py script based on the given command line parameters
    """
    IS_FORCE = False
    REPUSH = False

    # Convert add_mode and update_mode from strings to booleans
    add_mode = str2bool(add_mode)
    update_mode = str2bool(update_mode)

    if add_mode:
        # Ensure archive_path and flights_dir are not empty
        if not archive_path:
            print('Error: Please provide an archive path.')
            sys.exit(1)
        elif not flights_dir:
            print('Error: Please provide a directory for flights.')
            sys.exit(1)
        else:
            addFlights(flights_dir, archive_path, repush=REPUSH)

    elif update_mode:
        updateFlights(update_id)

    else:
        print('Error: Mode unrecognized. Please choose either add or update.')
        sys.exit(1)

if __name__ == '__main__':
    main()


__author__    = "Ioana Circu"
__contact__   = "ioana.circu@stfc.ac.uk"
__copyright__ = "Copyright 2025 United Kingdom Research and Innovation"