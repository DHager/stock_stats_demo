## Purpose

A demo involving access to the Quandl WIKI Prices API and analysis of the data.

This demo deliberately does NOT use quandl's own python package.

## Requirements

Requires Python 3.x

## Installation 

You can install this tool using Distutils: Running `setup.py install` will create a `stock_stats` command. 

Installation is not required, you can also run the program in-place with `python3 -m stock_stats` .

## Example Usage

    stock_stats -h
    stock_stats list-symbols -k API_KEY
    stock_stats month-averages -k API_KEY 2017-01 2017-06 COF GOOGL MSFT

## Running Tests

    python3 -m unittest tests/test_*

