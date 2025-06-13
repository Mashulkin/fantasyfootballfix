# -*- coding: utf-8 -*-
"""
Getting information about teams on fantasyfootballfix
"""
import sys

import addpath
from simple_settings import settings

from common_modules.csv_w import write_csv
from common_modules.txt_r import read_txt
from common_modules.headline import print_headline
from common_modules.my_remove import remove_file

from functions.statistic import get_statisticTeams
from functions.format import formatNullData


__author__ = 'Vadim Arsenev'
__version__ = '1.0.0'
__data__ = '31.07.2021'


ORDER = list(map(lambda x: x.split(':')[0].strip(), \
    read_txt(settings.COLUMNS_TEAMS).split('\n')))


def teamsInfo(stats):
    """
    Main function
    """
    data = {}
    for item in stats:
        short_name = item['team']['short_name']

        teamsStats = item['stats'].copy()
        for key in item['stats'].keys():
            if key not in ORDER:
                del teamsStats[key]

        teamsStats.update({'short_name': short_name, })
        teamsStats = formatNullData(teamsStats)
        data.update({(short_name): teamsStats})
    return data


def main(mingw=1, maxgw=8, venue='Home/away'):
    # venue= home/away, home, away
    parameters = {
        'mingw': mingw,
        'maxgw': maxgw,
        'venue': venue,
        'season': settings.YEAR,
    }

    data = teamsInfo(get_statisticTeams(**parameters))

    print_headline(settings.RESULT_FILE_TEAMS[0], \
        settings.COLUMNS_TEAMS, ORDER)
    for player in data.values():
        write_csv(settings.RESULT_FILE_TEAMS[0], player, ORDER)


if __name__ == '__main__':
    remove_file(settings.RESULT_FILE_TEAMS[0])
    # main(1, 38, 'Home/away')
    main(sys.argv[1], sys.argv[2], sys.argv[3])
