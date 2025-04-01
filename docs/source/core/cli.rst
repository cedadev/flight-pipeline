======================
Command Line Interface
======================

Instructions
============
The Command Line Interface (CLI) has been created with the ``click`` Python package. It provides an easy way to build and handle command line arguments.

The user can change the following options:
- ``archive_path``

- ``flights_path``: the path to where the flights to be pushed are currently located

- ``logging``: ``True`` or ``False``, this will enable or disable *logging to file*

- ``console_logging``: ``True`` or ``False``, this will enable or disable *logging to console*

- ``add_mode``: ``bool`` where the mode is set to add flights to archive

- ``update_mode``: ``bool`` where mode is set to update the archived flights
