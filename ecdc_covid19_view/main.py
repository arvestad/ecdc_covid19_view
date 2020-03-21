import argparse
import matplotlib.pyplot as plt
import pandas as pd

#arve_selection = ['Sweden', 'Italy']
arve_selection = ['Sweden', 'Italy', 'USA', 'Denmark', 'Norway', 'UK', 'Spain', 'Finland', 'France', 'Germany', 'China', 'South_Korea', 'Iran', 'Belgium', 'Iraq']
europe = ['Sweden', 'Denmark', 'Norway', 'Finland', 'Iceland', 'Italy', 'France', 'Germany', 'Spain', 'Netherlands', 'Belgium', 'UK', 'Albania', 'Austria', 'Belarus', 'Bulgaria', 'Croatia', 'Cyprus', 'Estonia', 'Faroe_Islands', 'Greece', 'Hungary', 'Ireland', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Poland', 'Russia', 'Serbia', 'Slovakia', 'Slovenia', 'Ukraine']


def setup_argument_parsing():
    ap = argparse.ArgumentParser(description="Read data from ECDC's COVID-19 Excel sheets")
    ap.add_argument('infile', help="An Excel file from ECDC with the, uh, expected columns.")
    ap.add_argument('-a', '--arve-selection', action='store_true', help='Restrict to a subset of countries chosen by Lars Arvestad')
    ap.add_argument('-e', '--europe', action='store_true', help='Restrict to European countries')
    ap.add_argument('-lc', '--list-countries', action='store_true', help='List countries and territories')
    ap.add_argument('-d', '--deaths', action='store_true', help='List countries and deaths, sorted by deaths')
    ap.add_argument('-md', '--min-deaths', type=int, default=10, help='Start plotting cumulative deaths at this many deaths (default 10)')
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


def country_death_summary(df, country_list):
    table = {}
    for country in country_list:
        country_selection = df['Countries and territories'] == country
        country_data = df[country_selection]
        country_data = country_data.sort_values(by='DateRep') # Use chronologigal order, instead of reverse chronological order
        country_data['Cumulative deaths'] = country_data['Deaths'].cumsum()
        table[country] = sum(country_data['Deaths'])
    return table


def main():
    ap = setup_argument_parsing()
    args = ap.parse_args()

    pd.options.display.width = 0

    df = pd.read_excel(args.infile)
    fix_country_names(df)
    country_list = list(df['Countries and territories'].unique())
    country_list = remove_strange_names(country_list)
    if args.arve_selection:
        country_list = arve_selection
    elif args.europe:
        country_list = europe

    if args.list_countries:
        for country in country_list:
            print(country)

    elif args.deaths:
        table = country_death_summary(df, country_list)
        print('Land                        Total deaths  Recent increases')
        for country, deaths in [(c, table[c]) for c in sorted(table, key=table.get, reverse=True)]:
            country_selection = df['Countries and territories'] == country
            recently = ', '.join(map(str, list(df[country_selection]['Deaths'])[0:5]))
            print(f'{country:30}{deaths:>10}   {recently}')

    else:
        current_axis = plt.gca()
        countries_used = []
        for country in country_list:
            country_selection = df['Countries and territories'] == country
            country_data = df[country_selection]
            country_data = country_data.sort_values(by='DateRep') # Use chronologigal order, instead of reverse chronological order
            country_data['Cumulative deaths'] = country_data['Deaths'].cumsum()

            date_selection = country_data['Cumulative deaths'] >= args.min_deaths
            restricted_country_data = country_data[date_selection].copy()
            n_items = len(restricted_country_data)
            if n_items == 0:
                print(f'Less than {args.min_deaths} deaths for {country}. Not plotting.')
            else:
                x_title = f'Days since {args.min_deaths} deaths'
                restricted_country_data[x_title] = range(n_items)
                restricted_country_data.plot(kind='line', x=x_title, y='Cumulative deaths', ax=current_axis, logy=True, marker='.', legend=country)
                countries_used.append(country)

        current_axis.legend(loc=2, fontsize='xx-small')
        current_axis.legend(countries_used)
        plt.show()
