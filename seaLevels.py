import os
from numpy.lib.function_base import average
import requests
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Adds a log handler for bugs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logfile_seaLevels.log', 'w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logging.getLogger('matplotlib.font_manager').disabled = True # Disables annoying matplot messages

### Defining Functions
# Pulls temp data
def get_data_level():
    '''Queries the url to generate a CSV file with Global temp data. CSV
        will be stored in folder used to run file

    Returns: None, but creates SeaLevelData.csv'''
    url = 'https://datahub.io/core/sea-level-rise/r/csiro_recons_gmsl_yr_2015.csv'
    response = requests.get(url, allow_redirects=True)
    if response:
        logging.debug('Successfully connected to data source, grabbing Sea Data...')
        open('SeaLevelData.csv', 'wb').write(response.content)
    else:
        logging.debug('Could not connect to data source...')
        logging.debug('Exiting program')
        print('Error querying data')
        quit()

# Cleans temp Data
def clean_data_level(file='SeaLevelData.csv'):
    '''Processes raw SeaLevelData file. Removes Uncertainty column, and cleans up year entry.

    Returns: None, but creates SeaLevelClean.csv'''
    try:
        data = np.loadtxt(file, delimiter=',', dtype=str)
        rows = []
        for i in range(1,len(data)):
            row = [int(data[i][0][0:4]), float(data[i][1]), float(data[i][2])]
            rows.append(row)
        clean_data = np.array(rows, dtype='O')
        pd.DataFrame(clean_data).to_csv('SeaLevelClean.csv')
        logging.debug(
            'Sea Data Sucessfully Cleaned...')
    except:
        logging.debug('Error cleaning data, check raw data file...')
        print('Error Cleaning Data')
        quit()


# Checks for data files in local folder, and generates them if unavailable
def get_sea_csv():
    '''Builds both the clean and raw CSV files for use in the module'''
    if os.path.exists('SeaLevelClean.csv') == False:
        # Searches for the clean CSV, and if it does not exist attempts to clean the raw CSV
        logging.debug('No clean Sea Data file found locally, creating clean file...')
        if os.path.exists('SeaLevelData.csv') == False:
            # Searches for the raw CSV, and if it does not exist attempts to query data
            logging.debug(
                'No Sea Data file found locally, querying data file from internet...')
            get_data_level()
            clean_data_level('SeaLevelData.csv')  # Cleans raw CSV
        else:
            clean_data_level('SeaLevelData.csv')  # Cleans raw CSV
        logging.debug('Clean Sea Data generated...')
    else:
        logging.debug('Clean Sea Data found...')


### Creates local data array and dataframe for use in arg parse
def create_sea_local():
    '''Returns a dataframe and numpy array of the clean sea level CSV and ensures 
        that both are in proper format to be processed by command line arguments
        
    Returns:    df - A pandas dataframe of the clean CSV data
                data - A numpy array of the clean CSV data
    '''
    df = pd.read_csv('SeaLevelClean.csv', index_col=0)     # Creates dataframe from Clean CSV
    df.columns = ['Year', 'Sea Level', 'Uncertainty']
    data = df.values.astype('object')    # Creates np array from Clean CSV
    data[:, 0] = data[:, 0].astype('int')       # Insures correct datatype for year
    logging.debug('Sea Dataframe and numpy array created...')
    return df, data

def main():
    ### Configuring arg parser (Adding Command line arguments)
    parser = argparse.ArgumentParser(
        description='Reads Sea Level file. NOTE: Sea levels are represented by \
            Reconstructed Global Mean Sea Level in mm (GMSL), and GMSL uncertainty in same units.')
    plot = None
    display = None
    sortType = None
    ave = None

    parser.add_argument('-p', '--print', default=False, dest='display',
                        action='store_true', help='Displays the SealevelClean dataset')

    parser.add_argument('-sl', '--sortlevel', default=False, dest='sortlevel',
                        action='store_true', help='Sorts order of dataset according to \
                            sea level with highest sea level years first, and displays it. (Automatically runs -p arg)')

    parser.add_argument('-pl', '--plot', metavar='<plot type>',
                        choices=['annual', 'uncert', 'OLS', 'all'], dest='plot', action='store',
                        help='Chooses which plot to output, or allows all plots to be output. \n \
                            Options are "annual" for annual global mean sea level in mm, "uncert" for annual uncertainty,\
                            "OLS" which gives a OLS regression line over annual levels, and "all" which outputs all plots')

    parser.add_argument('-a', '--avg', default=False, dest='ave',
                        action='store_true', help='Displays the average global mean sea level and \
                            average change over the timeframe')

    args = parser.parse_args()
    ave = args.ave
    plot = args.plot
    display = args.display
    sortType = args.sortlevel

    get_sea_csv()
    df, data = create_sea_local()
    if sortType == True:
        print(df.sort_values(by=['Sea Level'],
                             ascending=False).to_string())
        logging.debug('Data sorted by sea level and displayed...')
    elif display == True:
        print(df.to_string())
        logging.debug('Data displayed...')

    if ave == True:
        print('Average sea level from 1880 to 2013:',
              round(data.mean(axis=0)[1], 5))
        print('Average increase in sea level per year:',
              round((data[-1][1]-data[0][1])/len(data), 5))
        print('\n'+'NOTE: Sea levels are represented by Reconstructed Global Mean Sea Level in mm (GMSL)')
        logging.debug('Averages drawn...')
    if plot != None:
        if plot == 'annual':
            plt.plot(df['Year'], df['Sea Level'])
            plt.xlabel('Year')
            plt.ylabel('Sea Level (GMSL)')
            plt.savefig('AnnualSeaLevel.png')
        elif plot == 'uncert':
            plt.plot(df['Year'], df['Uncertainty'], 'g-')
            plt.xlabel('Year')
            plt.ylabel('GMSL Uncertainty')
            plt.savefig('GMSL_Uncertainty.png')
        elif plot == 'OLS':
            plt.plot(df['Year'], df['Sea Level'], 'o')
            m, b = np.polyfit(df['Year'], df['Sea Level'], 1)
            plt.xlabel('Year')
            plt.ylabel('Sea Level (GMSL)')
            plt.plot(df['Year'], m*df['Year']+b, 'r-')
            plt.savefig('AnnualSeaLevelRegression.png')
        else:
            plt.plot(df['Year'], df['Sea Level'])
            plt.xlabel('Year')
            plt.ylabel('Sea Level (GMSL)')
            plt.savefig('AnnualSeaLevel.png')
            plt.close()
            plt.plot(df['Year'], df['Uncertainty'], 'g-')
            plt.xlabel('Year')
            plt.ylabel('GMSL Uncertainty')
            plt.savefig('GMSL_Uncertainty.png')
            plt.close()
            plt.plot(df['Year'], df['Sea Level'], 'o')
            m, b = np.polyfit(df['Year'], df['Sea Level'], 1)
            plt.xlabel('Year')
            plt.ylabel('Sea Level (GMSL)')
            plt.plot(df['Year'], m*df['Year']+b, 'r-')
            plt.savefig('AnnualSeaLevelRegression.png')
        logging.debug('Plot(s) created...')
    print('\n'+'Done!')
    logging.debug('Program successfully ran!')

if __name__ == "__main__":
    main()
