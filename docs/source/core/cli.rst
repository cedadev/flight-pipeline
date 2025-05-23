======================
Command Line Interface
======================

Instructions
============
The Command Line Interface (CLI) has been created with the ``click`` Python package. It provides an easy way to build and handle command line arguments.

The user can change the following options:

- ``archive_path``: the path where the flights will be pushed

- ``flights_path``: the path to where the flights to be pushed are currently located

- ``logging``: ``True`` or ``False``, this will enable or disable *logging to file*

- ``console_logging``: ``True`` or ``False``, this will enable or disable *logging to console*

- ``add_mode``: ``bool`` where the mode is set to add flights to archive

- ``update_mode``: ``bool`` where mode is set to update the archived flights


How to run the flightpipe:

``python cli.py run-flight-update``

When running with the above command, the user will be prompted with the following:

- ``Enable logging (y/n) [y]:``: ``bool`` defaults to ``True``
- ``Log to console (y/n) [n]:``: ``bool`` defaults to ``False``
- ``Set archive path [../..]:``: ``string`` defaults to value in config file ``dirconfig``
- ``Set path to flights to be pushed [../..]:``: ``string`` defaults to value in config file ``dirconfig``
- ``Set mode to add flights (y/n) [y]:``: ``bool`` defaults to ``True``
- ``Set update mode (y/n) [n]:``: ``bool`` defaults to ``False``
- ``Flight id to update [n]:``: ``string`` defaults to ``False``

.. note::

   Run with command ``flight-pipeline flight-update`` in order to get prompts in the console.

   Or run with command ``flight-pipeline flight-update --archive_path ../../ --flights_dir ../../ --add_mode y --update_mode n --update_id n`` where all the arguments are filled in already


When running the help command ``flight-pipeline --help``
========================================================

Usage: flight-pipeline [OPTIONS] COMMAND [ARGS]...

  Command Line Interface for flight update

Options:
  --help  Show this message and exit.

Commands:
  flight-update  Main function running the flight_update.py script based...


When running the help command ``flight-pipeline flight-update --help``
======================================================================

Usage: flight-pipeline flight-update [OPTIONS]

  Main function running the flight_update.py script based on the given command
  line parameters

Options:
========
  --logging BOOLEAN               Enable logging (True/False)
  --enable_console_logging BOOLEAN
                                  Log to console (True/False)
  --archive_path TEXT             Set archive path  [required]
  --flights_dir TEXT              Set path where flights will be pushed
                                  [required]
  --add_mode TEXT                 Set mode to just add flights
  --update_mode TEXT              Set mode to update flights
  --update_id TEXT                Update based on specific id
  --help                          Show this message and exit.

