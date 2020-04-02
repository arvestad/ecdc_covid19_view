import argparse
import sys
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
from datetime import date, datetime as dt

#arve_selection = ['Sweden', 'Italy']
arve_selection = ['Sweden', 'USA', 'Denmark', 'Norway', 'UK', 'Italy', 'Spain', 'Finland', 'France', 'Germany', 'China', 'South_Korea', 'Japan', 'Iran', 'Belgium', 'Iraq']
europe = ['Sweden', 'Denmark', 'Norway', 'Finland', 'Iceland', 'Italy', 'France', 'Germany', 'Spain', 'Netherlands', 'Belgium', 'UK', 'Albania', 'Austria', 'Belarus', 'Bulgaria', 'Croatia', 'Cyprus', 'Estonia', 'Faroe_Islands', 'Greece', 'Hungary', 'Ireland', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Poland', 'Russia', 'Serbia', 'Slovakia', 'Slovenia', 'Ukraine']
nordic = ['Sweden', 'Denmark', 'Norway', 'Finland', 'Iceland']


colors = ['blue', 'lightblue', 'orange', 'pink', 'limegreen', 'green', 'red', 'brown', 'purple', 'cyan', 'magenta', 'grey', 'gold']


def setup_argument_parsing():
    ap = argparse.ArgumentParser(description="Read data from ECDC's COVID-19 data files.")
    ap.add_argument('infile', help="A file from ECDC with the, uh, expected columns. In CSV format.")
    ap.add_argument('-e', '--excel', action='store_true', help="Read ECDC's Excel file, rather than CSV file")
    ap.add_argument('-s', '--selection', choices=['arve', 'nordic', 'europe'], help='Restrict to chosen countries')
    ap.add_argument('-lc', '--list-countries', action='store_true', help='List countries and territories')
    ap.add_argument('-d', '--deaths', action='store_true', help='List countries and deaths, sorted by deaths')
    ap.add_argument('-md', '--min-deaths', type=int, default=10, help='Start plotting cumulative deaths at this many deaths (default 10)')
    ap.add_argument('-r', '--regression', metavar='n_days', type=int, help='Make a regression for the last few days.')
    return ap

def fix_country_names(df):
    translations = {'United_States_of_America':'USA',
                    'United_Kingdom':'UK',
                    'Central_African_Republic':'CAR',
                    'United_Arab_Emirates':'UAE',
                    'United_Republic_of_Tanzania':'Tanzania',
                    'Democratic_Republic_of_the_Congo':'Congo'}
    df.replace(translations, inplace=True)


def remove_strange_names(countries):
    strange_names=['Cases_on_an_international_conveyance_Japan']
    return filter(lambda c: c not in strange_names, countries)


def country_death_summary(df, country_list, country_header, date_header, deaths_header):
    table = {}
    for country in country_list:
        country_selection = df[country_header] == country
        country_data = df[country_selection]
        country_data = country_data.sort_values(by=date_header) # Use chronologigal order, instead of reverse chronological order
        country_data['Cumulative deaths'] = country_data[deaths_header].cumsum()
        table[country] = sum(country_data[deaths_header])
    return table


def compute_regression(df, x_title, n_recent_days):
    '''
    Fit a least-squares line to log of cumulative deaths, during the last n_recent_days,
    or whatever is available from data.
    '''
    y_title = 'Cumulative deaths'
    y_values = np.log(list(df[y_title])[-n_recent_days:])
    n_recent_days = min(len(y_values), n_recent_days)
    x_values = list(df[x_title][-n_recent_days:])

    matrix_A = np.vstack([x_values, np.ones(n_recent_days)]).T
    m, c = np.linalg.lstsq(matrix_A, y_values, rcond=None)[0]

    return n_recent_days, x_values, m, c

csv_headers = ['deaths', 'countriesAndTerritories', 'dateRep']
excel_headers=['Deaths', 'Countries and territories', 'DateRep']
def check_headers_in_csv(df):
    headers = list(df.columns.values)
    bad_data=False
    for h in csv_headers:
        if h not in headers:
            bad_data=True
            print(f"Missing '{h}' in the CSV file's headers.", file=sys.stderr)
    if bad_data:
        print(f"Found: {headers}", file=sys.stderr)
        sys.exit(2)

def check_headers_in_excel(df):
    headers = list(df.columns.values)
    bad_data=False
    for h in excel_headers:
        if h not in headers:
            bad_data=True
            print(f"Missing '{h}' in the Excel file's headers.", file=sys.stderr)
    if bad_data:
        print(f"Found: {headers}", file=sys.stderr)
        sys.exit(1)


def main():
    ap = setup_argument_parsing()
    args = ap.parse_args()

    pd.options.display.width = 0

    if args.excel:
        df = pd.read_excel(args.infile)
        deaths_header, country_header, date_header = excel_headers
        check_headers_in_excel(df)
    else:
        date_parser = lambda ds: dt.strptime(ds, '%d/%m/%Y')
        df = pd.read_csv(args.infile, encoding='iso-8859-1', parse_dates=[0], date_parser=date_parser)
        deaths_header, country_header, date_header = csv_headers
        check_headers_in_csv(df)

    fix_country_names(df)
    country_list = list(df[country_header].unique())
    country_list = remove_strange_names(country_list)
    if args.selection == 'arve':
        country_list = arve_selection
    elif args.selection == 'europe':
        country_list = europe
    elif args.selection == 'nordic':
        country_list = nordic

    if args.list_countries:
        for country in country_list:
            print(country)

    elif args.deaths:
        table = country_death_summary(df, country_list, country_header, date_header, deaths_header)
        print('Land                        Total deaths   Recent increases')
        for country, deaths in [(c, table[c]) for c in sorted(table, key=table.get, reverse=True)]:
            country_selection = df[country_header] == country
            recently = ', '.join(map(lambda x: f'{x:4}', list(df[country_selection][deaths_header])[0:5]))
            print(f'{country:30}{deaths:>10}   {recently}')

    else:
        plt.rcParams['figure.figsize'] = (16,9)
        current_axis = plt.gca()
        countries_used = []

        i = 0
        for country in country_list:
            country_selection = df[country_header] == country
            country_data = df[country_selection]
            country_data = country_data.sort_values(by=date_header) # Use chronologigal order, instead of reverse chronological order
            country_data['Cumulative deaths'] = country_data[deaths_header].cumsum()
            num_deaths = list(country_data['Cumulative deaths'])[-1]

            date_selection = country_data['Cumulative deaths'] >= args.min_deaths
            restricted_country_data = country_data[date_selection].copy()
            n_items = len(restricted_country_data)
            if n_items == 0:
                print(f'Less than {args.min_deaths} deaths for {country}. Not plotting.', file=sys.stderr)
            else:
                x_title = f'Days since {args.min_deaths} deaths'
                restricted_country_data[x_title] = range(n_items)
                current_color = colors[i%len(colors)]
                i += 1

                drawing_depth = -num_deaths
                restricted_country_data.plot(kind='line', x=x_title, y='Cumulative deaths', ax=current_axis, logy=True,
                                             marker='.', legend=country, color=current_color, linestyle='-', zorder=drawing_depth)
                if args.regression and n_items > 5:
                    n_recent_days, x_values, slant, offset = compute_regression(restricted_country_data, x_title, args.regression)
                    first_day = x_values[0]
                    last_obs_day = x_values[-1]
                    last_day = x_values[-1] + 5
                    y_first_day = math.exp(first_day * slant+ offset)
                    y_last_obs_day = math.exp(last_obs_day * slant + offset)
                    y_last_day = math.exp(last_day*slant+offset)
                    plt.plot([first_day, last_day], [y_first_day, y_last_day], linestyle=':', color=current_color, label='_nolegend_')
                    percent_increase = int(round(slant*100))
                    plt.annotate(f' {num_deaths} {country}', xy=(last_obs_day, y_last_obs_day), color=current_color,zorder=drawing_depth)
                    plt.annotate(f'{math.floor(y_last_day)}? ({percent_increase}%)', xy=(last_day, y_last_day), color=current_color,zorder=drawing_depth)
                countries_used.append(country)

        current_axis.legend(loc=2, fontsize='xx-small')
        current_axis.legend(countries_used)

        today = date.today()
        output_file_name = f'covid_deaths_{today}.pdf'
        plt.savefig(output_file_name)
        print(f'Saved figure as a PDF: {output_file_name}', file=sys.stderr)
        plt.show()
