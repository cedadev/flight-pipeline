# flight-pipeline
Repository for python code to concatenate data sources and construct new flight records for CEDA flight-finder

## Objectives:
  - Mechanism for finding new flight ids/paths
  - Use ES Client to determine array of ids that currently exists in the index
  - Construct Metadata 'properties' field
  - Determine Spatial Coordinates and Temporal dates
  - Push new records

## Run Pipeline
Run with command `python flight_update.py <filedir>`. Unless otherwise specified, __<filedir>__ should simply be jsons