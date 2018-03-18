## Purpose

A demo involving access to the Quandl WIKI Prices API and analysis of the data.

This demo deliberately does NOT use quandl's own python package.

## Requirements

Requires Python 3.6 or higher

## Installation 

You can install this tool using Distutils: Running `setup.py install` will create a `stock_stats` command. 

Installation is not required, you can also run the program in-place with `python -m stock_stats` .

## Example Usage

Show help:
    
    stock_stats -h
    
List financial symbols that can be used

    stock_stats list-symbols -k API_KEY --pretty
    
Get average open/close statistics for a 6 month span for 3 stocks (end month inclusive) 
 
    stock_stats month-averages -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty 

Determine which day had the biggest low-high spread for each symbol.

    stock_stats best-days -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty

Determine days were significantly busier than average for each symbol.

    stock_stats busy-days -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty
    
Determine which of the symbols had the most down-closing days.

    stock_stats biggest-loser -k API_KEY 2017-01 2017-06 COF GOOGL MSFT --pretty

## Running Tests

Note: Some tests are disabled unless you place a file called `apikey.txt` in the project root containing your API key.

    python -m unittest tests/test_*
   

