import os
from numpy.lib.function_base import average
import requests
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Adding a log handler for bugs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logfile_GlobalTemp.log', 'w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logging.getLogger('matplotlib.font_manager').disabled = True # Disables annoying matplot messages

### Defining functions 
# Pulls temp data
def get_data_temp():
    '''Queries the url to generate a CSV file with Global temp data. CSV will be stored in 
        folder used to run file.

    Returns: None, but creates GlobalTempData.csv'''
    url = 'https://query.data.world/s/2rwx5ges7kbt3ouhzi2pe4dv2dxuit'
    response = requests.get(url, allow_redirects=True)
    if response:
        logging.debug('Successfully connected to data source, grabbing Temp Data...')
        open('GlobalTempData.csv', 'wb').write(response.content)
    else:
        logging.debug('Could not connect to data source...')
        logging.debug('Exiting program')
        print('Error querying data')
        quit()

# Cleans temp Data
def clean_data_temp(file='GlobalTempData.csv'):
    '''Processes raw GlobalTempData file and deletes unused columns as well as aggregates the
        annual-mean temp (second column) and five-year-mean temp (third column) onto same row. 
        Cleans up year entry.

    Returns: None, but creates GlobalTempClean.csv'''
    try:
        data = np.loadtxt(file,delimiter=',',dtype=str)
        rows=[]
        for i in range(1,len(data),2):
            row = [int(data[i][4][1:5]),float(data[i][5]),float(data[i+1][5])]
            rows.append(row)
        clean_data = np.array(rows,dtype='O')
        pd.DataFrame(clean_data).to_csv('GlobalTempClean.csv')
        logging.debug(
            'Temp Data Sucessfully Cleaned...')
    except:
        logging.debug('Error cleaning data, check raw data file...')
        print('Error Cleaning Data')
        quit()


# Checks for data files in local folder, and generates them if unavailable
def get_temp_csv():
    '''Builds both the clean and raw CSV files for use in the module'''
    if os.path.exists('GlobalTempClean.csv') == False:
        # Searches for the clean CSV, and if it does not exist attempts to clean the raw CSV
        logging.debug('No clean Temp Data file found locally, creating clean file...')
        if os.path.exists('GlobalTempData.csv') == False:
            # Searches for the raw CSV, and if it does not exist attempts to query data
            logging.debug('No Temp Data file found locally, querying data file from internet...')
            get_data_temp()
            clean_data_temp('GlobalTempData.csv')  # Cleans raw CSV
        else:
            clean_data_temp('GlobalTempData.csv')  # Cleans raw CSV
        logging.debug('Clean Temp Data generated...')
    else:
        logging.debug('Clean Temp Data found...')


# Creates local data array and dataframe for use in arg parse
def create_temp_local():
    '''Returns a dataframe and numpy array of the clean temp CSV and ensures 
        that both are in proper format to be processed by command line arguments
        
    Returns:    df - A pandas dataframe of the clean CSV data
                data - A numpy array of the clean CSV data
    '''
    df = pd.read_csv('GlobalTempClean.csv', index_col=0)  # Creates dataframe from Clean CSV
    df.columns = ['Year', 'Annual Avg Temp', '5-Year Avg Temp']
    data = df.values.astype('object')    # Creates np array from Clean CSV
    data[:, 0] = data[:, 0].astype('int')       # Insures correct datatype for year
    logging.debug('Temp Dataframe and numpy array created...')
    return df, data

### Defining Main Function, which examines command line args then performs duty
def main():
    ### Configuring arg parser (Adding Command line arguments)
    parser = argparse.ArgumentParser(
        description='Reads Global Temp file. NOTE: All temps are represented by change \
            in global surface temperature relative to 1951-1980 average temperatures')
    plot = None
    display = None
    sortType = None
    ave = None

    # Prints the pandas dataframe of clean temp data
    parser.add_argument('-p','--print', default=False, dest='display',
                        action='store_true', help ='Displays the GlobalTempClean dataset')

    # Sorts the pandas dataframe by temp, then prints it
    parser.add_argument('-st', '--sorttemp', default=False, dest='sorttemp',
                        action='store_true', help='Sorts order of dataset according to \
                            temperature with hottest years first, and displays it. (Automatically runs -p arg)')

    # Multivariable use for creating plots of data
    parser.add_argument('-pl', '--plot', metavar='<plot type>', 
                        choices=['annual', '5year','OLS','all'], dest='plot', action='store',
                        help='Chooses which plot to output, or allows all plots to be output. \n \
                            Options are "annual" for annual average temp, "5year" for 5 year average temp,\
                            "OLS" which gives a OLS regression line over annual averages, and "all" which outputs all plots')

    # Fetches average temp and average increase per year
    parser.add_argument('-a', '--avg', default=False, dest='ave',
                        action='store_true', help='Displays the average global temp and average \
                            yearly change over the timeframe')

    args = parser.parse_args()
    ave = args.ave
    plot = args.plot
    display = args.display
    sortType = args.sorttemp

    get_temp_csv()
    df, data = create_temp_local()
    if sortType == True:
        print(df.sort_values(by=['Annual Avg Temp'],
                             ascending=False).to_string())
        logging.debug('Data sorted by temp and displayed...')
    elif display == True:
        print(df.to_string())
        logging.debug('Data displayed...')

    if ave == True:
        print('Average global temp from 1880 to 2016:',
              round(data.mean(axis=0)[1], 5))
        print('Average increase in global temperature per year:',
              round((data[-1][1]-data[0][1])/len(data), 5))
        print('\n'+'NOTE: All temps are represented by change in global surface temperature relative to 1951-1980 average temperatures')
        logging.debug('Averages drawn...')
    if plot != None:
        if plot == 'annual':
            plt.plot(df['Year'], df['Annual Avg Temp'])
            plt.xlabel('Year')
            plt.ylabel('Annual Average Temperature')
            plt.savefig('AnnualAvgTemp.png')
        elif plot == '5year':
            plt.plot(df['Year'], df['5-Year Avg Temp'], 'g-')
            plt.xlabel('Year')
            plt.ylabel('5-Year Avgrage Temperature')
            plt.savefig('5-YearAvgTemp.png')
        elif plot == 'OLS':
            plt.plot(df['Year'], df['Annual Avg Temp'], 'o')
            m, b = np.polyfit(df['Year'], df['Annual Avg Temp'], 1)
            plt.xlabel('Year')
            plt.ylabel('Annual Average Temperature')
            plt.plot(df['Year'], m*df['Year']+b, 'r-')
            plt.savefig('AnnualAvgTempRegression.png')
        else:
            plt.plot(df['Year'], df['Annual Avg Temp'])
            plt.xlabel('Year')
            plt.ylabel('Annual Average Temperature')
            plt.savefig('AnnualAvgTemp.png')
            plt.close()
            plt.plot(df['Year'], df['5-Year Avg Temp'], 'g-')
            plt.xlabel('Year')
            plt.ylabel('5-Year Avgrage Temperature')
            plt.savefig('5-YearAvgTemp.png')
            plt.close()
            plt.plot(df['Year'], df['Annual Avg Temp'], 'o')
            m, b = np.polyfit(df['Year'], df['Annual Avg Temp'], 1)
            plt.xlabel('Year')
            plt.ylabel('Annual Average Temperature')
            plt.plot(df['Year'], m*df['Year']+b, 'r-')
            plt.savefig('AnnualAvgTempRegression.png')
        logging.debug('Plot(s) created...')
    print('\n'+'Done!')
    logging.debug('Temp Program successfully ran!')

if __name__ == "__main__":
    main()