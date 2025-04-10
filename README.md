# flight-pipeline
Repository for python code to concatenate data sources and construct new flight records for CEDA flight-finder

## Objectives: 
  - Mechanism for uploading new flights to stac index
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records that are not currently in the index
  - Remove or archive pushed records on local system

## Installation:

You can either install the ``PyPi`` package through ``pip`` or clone the GitHub repository. The two options can be found below.

### 1. Install using pip

  - Run ``pip install ceda-flight-pipeline``
  - Install requirements into a local virtual environment using ``Poetry``:
    - ``poetry install``
  - Configure dirconfig with relative paths

### OR ###

### 2. Install by cloning GitHub repository

  - Clone the repository from github by running ``git clone https://github.com/cedadev/flight-pipeline.git``
  - Install requirements into a local virtual environment using ``Poetry``:
     - ``poetry install``
  - Configure dirconfig with relative paths

## Setting up environment variables
In order to run the `flight-pipeline` project, you will need the following variables in your environment.
```
CONFIG_FILE=/path/to/your/dir/config/dirconfig
STAC_TEMPLATE=/path/to/your/dir/config/stac_template.json
SETTINGS_FILE=/path/to/your/dir/config/settings.json
```

In `bash` you can run:
`export CONFIG_FILE=/path/to/your/dir/config/dirconfig`

## Running the program

### 1. Use stac_template to write new records
Follow the STAC template json file to create new flight records (more details further down)

### 2. Configure dirconfig file
Add on lines 2 and 4 the directory paths to where your new flights to push are stored, and where the pushed flights should go once they have been uploaded to the index (store them or write DELETE to remove them from the local system). Update line 6 with a directory path to a logfile.

### 3. Push New Flights
Run with command `flight-pipeline flight-update` with a filled in dirconfig file to push new records to the index.

Or run with command `flight-pipeline flight-update --archive_path ../../ --flights_dir ../../ --add_mode y --update_mode n --update_id n`

## Update Existing Flights
Note: In case of repair or adjustment to existing records, the individual records can be updated in place.

Run with command `python flight_update.py update <pyfile>`, where __pyfile__ is a python file containing an __update__ function that can be applied to each record in elasticsearch.

## STAC Template
From the template, the following should be filled in:
 - id (fnum/pcode * date)
 - es_id (random string of ASCII characters to generate one of 9 colours in flight finder)
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

## Geometries Development
Correct Version of mapping that exists in the arsf index
```
"spatial" : {
  "properties" : {
    "geometries" : {
      "properties" : {
        "display" : {
          "properties" : {
            "coordinates" : {
              "type" : "double",
              "index" : false
            },
            "type" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "full_search" : {
          "type" : "geo_shape"
        },
        "search" : {
          "type" : "geo_shape"
        }
      }
    }
  }
```

Incorrect version currently in __stac-flightfinder-items__
```
"geometry" : {
  "properties" : {
    "display" : {
      "properties" : {
        "coordinates" : {
          "type" : "float"
        },
        "type" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        }
      }
    },
    "geometries" : {
      "properties" : {
        "display" : {
          "properties" : {
            "coordinates" : {
              "type" : "float"
            },
            "type" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "search" : {
          "properties" : {
            "coordinates" : {
              "type" : "float"
            },
            "type" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        }
      }
    },
    "search" : {
      "properties" : {
        "coordinates" : {
          "type" : "float"
        },
        "type" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        }
      }
    }
  }
}
```
Ammendments:
 - Remove __geometries__ subfield.
 - Remove all subfields of __search__ and just add `"type":"geo_shape"`.
 - Add __full_search__ sub_field with `"type":"geo_shape"`.
