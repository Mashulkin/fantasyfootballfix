# -*- coding: utf-8 -*-
"""
Making requests to sites
"""
from simple_settings import settings
from common_modules.parser import Parser


__author__ = 'Vadim Arsenev'
__version__ = '1.0.0'
__data__ = '30.07.2021'


def get_statisticPlayers(mingw, maxgw, venue, season):
    url = f'{settings.API_URL}/players/?season={season}&min_gw={mingw} \
        &max_gw={maxgw}&home_away={venue}'
    requests_data = Parser(url, cookies={'sessionid': settings.SESSIONID})
    stats = requests_data.parser_result()
    return stats


def get_statisticTeams(mingw, maxgw, venue, season):
    url = f'{settings.API_URL}/teams/?season={season}&min_gw={mingw} \
        &max_gw={maxgw}&home_away={venue}&opposition=ALL'
    requests_data = Parser(url, cookies={'sessionid': settings.SESSIONID})
    stats = requests_data.parser_result()
    return stats
