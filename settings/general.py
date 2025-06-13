# import sys


__author__ = 'Vadim Arsenev'
__version__ = '0.9.0'
__data__ = '02.11.2021'


API_URL = 'https://www.fantasyfootballfix.com/api/stats'
SESSIONID = 'hpr3hvgrl97x2zwqjkhsdd1sho8kvsy'
YEAR = '2024'

# for players only
COLUMNS = './settings/FFFplayers.txt'
# for terminal and .exe in Windows
RESULT_FILE = ['./data/FFFplayers.csv']
# for app in Mac OS
# RESULT_FILE = ['/'.join(sys.argv[0].split('/')[:-4]), '/data/FFFplayers.csv']

# for teams only
COLUMNS_TEAMS = './settings/FFFteams.txt'
# for terminal and .exe in Windows
RESULT_FILE_TEAMS = ['./data/FFFteams.csv']
