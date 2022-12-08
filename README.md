# flight-pipeline
Repository for python code to concatenate data sources and construct new flight records for CEDA flight-finder

## Objectives:
  - Mechanism for uploading new flights to stac index
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records

## Run Pipeline
Run with command `python flight_update.py <filedir>`, where __filedir__ is the path to a directory of jsons that follow the STAC template.

## STAC Template
From the template, the following should be filled in:
 - id (fnum/pcode * date)
 - es_id (hash function for generating colours)
 - description_path
 - collection
 - geometry.display.coordinates
 - geometry.display.type (if coordinates are not MultiLineString)
 - properties:
   - data_format
   - start_datetime
   - end_datetime
   - flight_num (if applicable)
   - pcode (if applicable)
   - aircraft
   - variables
   - location
   - platform
   - instruments
   - pi