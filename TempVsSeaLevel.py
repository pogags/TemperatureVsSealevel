import logging
import pandas as pd
import os
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import argparse
from globalTemp import get_temp_csv, create_temp_local
from seaLevels import get_sea_csv, create_sea_local

### Adding a log handler for bugs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logfile_TempVsSea.log', 'w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logging.getLogger('matplotlib.font_manager').disabled = True    # Disables annoying matplot messages

### Create function to run with __main__ to allow for correct argument parsing
def callfiles():
    '''Brings in Global Temp and Sea Level Files
    
    Returns:    df_merge - merged dataframe of Temp and Sea Data
                data_temp - numpy array of Temp Data
                data_sea - numpy array of Sea Data'''

    # Creates CSVs needed for analysis if they don't exist
    if os.path.exists('GlobalTempClean.csv') == False:
        get_temp_csv()
    if os.path.exists('SeaLevelClean.csv') == False:
        get_sea_csv()

    # Create local dataframes and arrays of the clean Temp and Sea Data
    df_temp, data_temp = create_temp_local()
    df_sea, data_sea = create_sea_local()

    # This handy bit of code merges the two dataframes on 'Year'
    df_merge = pd.merge(left=df_temp, right=df_sea,
                            left_on='Year', right_on='Year')
    return df_merge, data_temp, data_sea

### Configuring arg parser (Adding Command line arguments)
parser = argparse.ArgumentParser(
    description='Imports seaLevel.py and globalTemp.py files, and creates clean CSVs\
        of both datasets if needed. Gives analysis options for both sets.')
plot = None
display = None
regression = None

# Prints the pandas dataframe of clean temp data
parser.add_argument('-p', '--print', default=False, dest='display',
                    action='store_true', help='Displays the Merged GlobalTemp and SeaLevel dataset')

# Multivariable use for creating plots of data
parser.add_argument('-pl', '--plot', metavar='<plot type>',
                    choices=['annual', '5year', 'norm', 'all'], dest='plot', action='store',
                    help='Chooses which plot to output, or allows all plots to be output. \n \
                        Options are "annual" for annual avg temp VS sea level, "5year" for 5 year avg temp VS sea level,\
                        "norm" which plots Year VS normalized sets of avg temp and sea level,\
                        and "all" which outputs all plots')

# Fetches average temp and average increase per year
parser.add_argument('-r', '--regression', metavar='<variable>', dest='regression',
                    choices=['annual', '5year'],
                    action='store', help='Performs an OLS regression on Global Temp vs Sea Level.\n \
                        Options are "annual" for comparing the annual avg temp to sea level, and\
                            "5year" for comparing 5 year avg to sea level')

args = parser.parse_args()
plot = args.plot
display = args.display
regression = args.regression

if __name__ == "__main__":
    df_merge, data_temp, data_sea = callfiles()
    if display == True:
        print(df_merge.to_string())
        logging.debug('Data displayed...')
    if plot != None:
        if plot == 'annual':
            plt.plot(df_merge['Annual Avg Temp'], df_merge['Sea Level'],'ro')
            plt.xlabel('Annual Avg Temp (Relative to 1951-1980 Avg)')
            plt.ylabel('Sea Level (GMSL)')
            plt.title('Average Temp VS Sea Level')
            plt.savefig('TempVsSeaLevel.png')
        elif plot == '5year':
            plt.plot(df_merge['5-Year Avg Temp'], df_merge['Sea Level'], 'ro')
            plt.xlabel('5-Year Avg Temp (Relative to 1951-1980 Avg)')
            plt.ylabel('Sea Level (GMSL)')
            plt.title('5-Year Average Temp VS Sea Level')
            plt.savefig('Temp5YearVsSeaLevel.png')
        elif plot == 'norm':
            norm_temp = (data_temp[:-3, 1]/np.linalg.norm(data_temp[:-3, 1]))
            norm_sea = (data_sea[:, 1]/np.linalg.norm(data_sea[:, 1]))
            # This creates normalized arrays of temp and sea data
            plt.plot(df_merge['Year'], norm_temp, 'ro', label='Avg Temp')
            plt.plot(df_merge['Year'], norm_sea, 'bo', label='Sea Level')
            plt.xlabel('Year')
            plt.ylabel('Global Sea Level/Avg Temp')
            plt.title('Annual Avg Temp and Sea Level (Normalized)')
            plt.legend(loc="upper left")
            plt.savefig('AnnualTemp+SeaNormalized.png')
        else:
            plt.plot(df_merge['Annual Avg Temp'], df_merge['Sea Level'], 'ro')
            plt.xlabel('Annual Avg Temp (Relative to 1951-1980 Avg)')
            plt.ylabel('Sea Level (GMSL)')
            plt.title('Average Temp VS Sea Level')
            plt.savefig('TempVsSeaLevel.png')
            plt.close()
            plt.plot(df_merge['5-Year Avg Temp'], df_merge['Sea Level'], 'ro')
            plt.xlabel('5-Year Avg Temp (Relative to 1951-1980 Avg)')
            plt.ylabel('Sea Level (GMSL)')
            plt.title('5-Year Average Temp VS Sea Level')
            plt.savefig('Temp5YearVsSeaLevel.png')
            plt.close()
            norm_temp = (data_temp[:-3, 1]/np.linalg.norm(data_temp[:-3, 1]))
            norm_sea = (data_sea[:, 1]/np.linalg.norm(data_sea[:, 1]))
            plt.plot(df_merge['Year'], norm_temp, 'ro', label='Avg Temp')
            plt.plot(df_merge['Year'], norm_sea, 'bo', label='Sea Level')
            plt.xlabel('Year')
            plt.ylabel('Global Sea Level/Avg Temp')
            plt.title('Annual Avg Temp and Sea Level (Normalized)')
            plt.legend(loc="upper left")
            plt.savefig('AnnualTemp+SeaNormalized.png')
        logging.debug('Plot(s) created...')
    if regression != None:
        if regression == 'annual':
            mod=sm.OLS(df_merge['Sea Level'], df_merge['Annual Avg Temp'])
            results=mod.fit()
            print(results.summary())
        elif regression == '5year':
            mod=sm.OLS(df_merge['Sea Level'], df_merge['5-Year Avg Temp'])
            results=mod.fit()
            print(results.summary())
        logging.debug('Regression Analysis Complete...')
    print('\n'+'Done!')
    logging.debug('TempVsSea Program successfully ran!')





### Unused main() function
# def main(raw_args=None):
#     parser = argparse.ArgumentParser(
#         description='Imports seaLevel.py and globalTemp.py files, and creates clean CSVs\
#             of both datasets if needed. Gives analysis options for both sets.')
#     plot = None
#     display = None
#     regression = None

#     # Prints the pandas dataframe of clean temp data
#     parser.add_argument('-p', '--print', default=False, dest='display',
#                         action='store_true', help='Displays the Merged GlobalTemp and SeaLevel dataset')

#     # Multivariable use for creating plots of data
#     parser.add_argument('-pl', '--plot', metavar='<plot type>',
#                         choices=['annual', '5year', 'norm', 'all'], dest='plot', action='store',
#                         help='Chooses which plot to output, or allows all plots to be output. \n \
#                             Options are "annual" for annual avg temp VS sea level, "5year" for 5 year avg temp VS sea level,\
#                             "norm" which plots Year VS normalized sets of avg temp and sea level,\
#                             and "all" which outputs all plots')

#     # Fetches average temp and average increase per year
#     parser.add_argument('-r', '--regression', metavar='<variable>', dest='regression',
#                         choices=['annual', '5year'],
#                         action='store', help='Performs an OLS regression on Global Temp vs Sea Level.\n \
#                             Options are "annual" for comparing the annual avg temp to sea level, and\
#                                 5year for comparing 5 year avg to sea level')

#     args = parser.parse_args(None)
#     plot = args.plot
#     display = args.display
#     regression = args.regression
