# Analyze COVID-19 data from ECDC

European Centre for Disease Prevention and Control (ECDC) produces a convenient Excel file with the latest
COVID-19 data from all over the world. See this link for a download (the filename changes daily, it seems):

* https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide

I wanted to script some graphs based on this data, so I started to
write this script. I have focused on mortality, because I do not think that reported cases is so useful
now that testing differs so radically in different countries, which is also reflected in mortality rates differing
one order of magnitude (I think).

## Usage

Basic usage is:

``` shell
ecdc_covid19_view [options] ecdc_file.xlsx
```

## Options

Running with no options causes a plot of cumulative deaths, as counted from the day the country had at least MIN_DEATHS.

``` shell
usage: ecdc_covid19_view [-h] [-a] [-lc] [-d] [-md MIN_DEATHS] infile

Read data from ECDC's COVID-19 Excel sheets

positional arguments:
  infile                An Excel file from ECDC with the, uh, expected
                        columns.

optional arguments:
  -h, --help            show this help message and exit
  -a, --arve-selection  Restrict to a subset of countries chosen by Lars
                        Arvestad
  -lc, --list-countries
                        List countries and territories
  -d, --deaths          List countries and deaths, sorted by deaths
  -md MIN_DEATHS, --min-deaths MIN_DEATHS
                        Start plotting cumulative deaths at this many deaths
                        (default 10)
```
