# -*- coding: utf-8 -*-
"""
Getting information about players on fantasyfootballfix
"""
import sys

import addpath
from simple_settings import settings

from common_modules.csv_w import write_csv
from common_modules.txt_r import read_txt
from common_modules.headline import print_headline
from common_modules.my_remove import remove_file

from functions.statistic import get_statisticPlayers
from functions.format import formatNullData, formatPosition


__author__ = 'Vadim Arsenev'
__version__ = '1.0.0'
__data__ = '22.08.2021'


ORDER = list(map(lambda x: x.split(':')[0].strip(), \
    read_txt(settings.COLUMNS).split('\n')))


def playersInfo(stats, mingw, venue):
    """
    Main function
    """
    data = {}
    for item in stats:
        playerId = item['player']['code']
        known_name = item['player']['known_name']
        abbr = item['player']['team_short_name']
        position = formatPosition(item['player']['position_name'])
        price = item['player']['price']
        game_started = item['stats']['game_started']
        expGA = item['stats']['exp_goals'] + \
            item['stats']['exp_assists']
        exp_goals_involvement = ''
        try:
            exp_goals_involvement = float(expGA) / \
                float(item['stats']['exp_goals_team']) * 100
        except ZeroDivisionError:
            pass
        except KeyError:
            pass

        playerStats = item['stats'].copy()
        for key in item['stats'].keys():
            if key not in ORDER:
                del playerStats[key]

        playerStats.update({'known_name': known_name,
                            'playerId': playerId,
                            'abbr': abbr,
                            'position': position,
                            'price': price,
                            'expGA': expGA, 
                            'exp_goals_involvement': exp_goals_involvement,
                            'gw': mingw,
                            'venue': venue,
                            'game_started': game_started,
        })
        playerStats = formatNullData(playerStats)
        data.update({(known_name, abbr): playerStats})
    return data


def main(mingw=1, maxgw=38, venue='home/away'):
    # venue= home/away, home, away
    parameters = {
        'mingw': mingw,
        'maxgw': maxgw,
        'venue': venue,
        'season': settings.YEAR,
    }

    data = playersInfo(get_statisticPlayers(**parameters), mingw, venue)

    print_headline(settings.RESULT_FILE[0], settings.COLUMNS, ORDER)
    for player in data.values():
        write_csv(settings.RESULT_FILE[0], player, ORDER)


if __name__ == '__main__':
    remove_file(settings.RESULT_FILE[0])
    # main(1, 38, 'home/away')
    # main(sys.argv[1], sys.argv[2], sys.argv[3])
    for mingw in range(1,39):
        main(mingw, mingw, 'home')
        main(mingw, mingw, 'away')
