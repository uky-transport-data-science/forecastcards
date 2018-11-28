# What are forecast cards?

Forecast cards are a simple data specification for storing key information about your travel forecast in order to:  
 - evaluate performance of a forecast over time,    
 - analyze the collective performance of forecasting systems and institutions over time, and
 - identify contributing factors to high performing forecasts.  


## Overview of forecast cards

There four are types of Forecast Cards:
 - Points of Interest, such as a roadway segment or transit line,
 - Projects, such as a roadway expansion, an HOV designation,
 - Scenarios or runs, including information about the forecasting system
 - Forecasts, which are predictions at the points of interest about what the project will do,
 - Observations, which are points of data used to evaluate the the forecasts

Each "card" is a text-based CSV file.  

### The Schema

![entity relationship diagram](spec/en/forecast-cards-erd.png?raw=true "Forecast Cards Schema Entity Relationship Diagram")

![Overview of data relationships](spec/en/forecast-cards-rg.png?raw=true "Forecast Cards Data Relationships")

Forecast Cards are compatible with the [Open Knowledge Foundation's]() [Frictionless Data](http://frictionlessdata.io) [Table Schema]( https://github.com/frictionlessdata/specs/blob/master/specs/table-schema.md) specification.

Explore the data schema from your web browser using [colaboratory](https://colab.research.google.com):

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/e_lo/forecast-cards/blob/master/notebooks/Explore_Data_Schemas)

### Included Examples

This project currently includes one example, which is the Emerald City DOT's HOV expansion for the Yellow Brick Road, which is contained in `forecastcards/examples/emeraldcitydot-rx123-yellowbrickroadhov`

This example can be analyzed and run with the `notebooks` folder of this directory and can be run using [binder](http://www.mybinder.org) or [colaboratory](https://colab.research.google.com).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/e_lo/forecast-cards/blob/master/notebooks/Estimate_Quantiles.ipynb)

Table Validity Status:  [![goodtables.io](https://goodtables.io/badge/github/e-lo/forecast-cards.svg)](https://goodtables.io/github/e-lo/forecast-cards)

### Suggested card naming and organization

In order to leverage a common set of tools, we suggest that forecast card data is stored in the following naming and folder structure:

    agency-name-project-id-project-short-name/
       |---README.md
       |---
       |---project-<project-id>-<project-short-name>.csv
       |---scenarios-<project-id>.csv
       |---poi-<project-id>.csv
       |---observations/
       |   |---observations-<date>.csv
       |
       |---forecasts/
       |   |---forecast-<scenario-id>-<scenario-year>-<forecast-creation>-<forecast-id>.csv

## How do I start on my own?

1. Make sure you have the required data by examining the schema.

2. Format Data as Forecast Cards
*[helper scripts on the way](https://github.com/e-lo/forecastcards/issues/1)*

3. Use template notebooks locally or on a hosted remote server (i.e. colaboratory) to clean data and estimate quantile regressions.  

## Making forecast cards publicly available

There are three likely options for making your data available:
1. Github (not great for extremely large datasets)
2. Amazon S3 / Microsoft Azure / Google Cloud (functionality coming soon)
3. Other agency-hosted web services (i.e. Socrata, webserver, etc.)

## Submitting forecast cards to community data store

You can submit forecast cards to the [community data store](https://github.com/e-lo/forecastcardsdata) by:

1. submitting a [pull-request to the forecastcardsdata repository](https://github.com/e-lo/forecastcardsdata/pulls)
2. submitting [an issue](https://github.com/e-lo/forecastcardsdata/issues) with a link to the location of the data along with permission to host it on the repository.
3. set up the public data store as a mirror.

## Getting Help

Please [submit an issue!](https://github.com/e-lo/forecastcards/issues)

## Suggested Workflow

### Initial setup

 - decide where the permanent "cold storage" of your data will live: local file server, cloud?
 - catalog and convert historic data

### Starting a new project

- create a new project folder and create project file
- determine points of interest and create POI file

### Adding a forecast to an existing project

- add a new forecast csv file with relevant data for points of interest
- add am entry to scenario csv file about the model run

### Adding observed data to existing project

- add a new observations csv
