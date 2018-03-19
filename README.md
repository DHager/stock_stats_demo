## Purpose

A demo involving access to the Quandl WIKI Prices API and analysis of the data.

This demo does not use Quandl's own REST client.

## Requirements

If you do not wish to use Docker, you will require:

* Python 3 (3.6 recommended)
* `dateutil` package

## Installation 

### Option 1: Install locally

Using setuptools/distutils:

    python setup.py install # Creates stock_stats command
    stock_stats --help

### Option 2: Run locally without installation

    python -m stock_stats --help

### Option 3: Use a disposable test Docker container

    # On local box, creates/runs docker container
    docker/run.sh

    # Inside docker container prompt
    python setup.py install
    stock_stats --help

## Example Usage

Show help:
    
    stock_stats --help
    
List financial symbols that can be used

    stock_stats list-symbols -k API_KEY --pretty
    
Get average open/close statistics for a 6 month span for 3 stocks (end month inclusive) 
 
    stock_stats month-averages -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty 

Determine which day had the biggest low-high variance for each symbol.

    stock_stats top-variance-days -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty

Determine days were significantly busier than average for each symbol.

    stock_stats busy-days -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty
    
Determine which of the symbols had the most down-closing days.

    stock_stats biggest-loser -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty

## Running Tests

Note: Some tests are disabled unless you place a file called `apikey.txt` in the project root containing your API key.

    python -m unittest tests/test_*
   
## Removing

If you used installation Option 1, you can remove the `stock_stats` command with:

    python -m pip uninstall "Stock-Price-Demo"
