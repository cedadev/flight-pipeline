======================
Command Line Interface
======================

Instructions
============
The Command Line Interface (CLI) has been created with the ``click`` Python package. It provides an easy way to build and handle command line arguments.

The standard command to run the flight pipeline is ``flight-pipeline flight-upload``. The following arguments can be supplied via the CLI, or using other methods as shown:
 
- ``new_flights_dir``: Directory holding the flights to be pushed. This can also be set in the ``FLIGHT_CONFIG`` line 2. See below for details of how to use the config file.

- ``archive_path``: Directory to cache flights that have been pushed to Elasticsearch/STAC. This can also be set in the ``FLIGHT_CONFIG``, line 4.

- ``update``: Add to update the ES index using content from the archive directory. For example if an attribute has changed, this can be used to reupload the existing record.

- ``reindex``: Used to migrate the current index.

- ``config_file``: Specify the location of the config file. To avoid a long command string, this can be set using the ``$FLIGHT_CONFIG`` environment variable instead.

- ``settings_file``: Elasticsearch connection settings file path. To avoid a long command string, this can be set using the ``$FLIGHT_CONNECTION`` environment variable instead.

- ``stac_template``: STAC template to apply to all new records. To avoid a long command string, this can be set using the ``$STAC_TEMPLATE`` environment variable instead.

- ``verbose``: Level of logging (``-v`` gives info messages, ``-vv`` gives debug messages)

Run with command ``flight-pipeline flight-update`` if all above values are configured using environment variables etc.

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

