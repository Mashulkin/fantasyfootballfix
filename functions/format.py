# -*- coding: utf-8 -*-
"""
Formatting of data
"""


__author__ = 'Vadim Arsenev'
__version__ = '1.0.0'
__data__ = '30.07.2021'


def formatNullData(data):
    for key, value in data.items():
        try:
            if float(value) == 0:
                data.update({key: ''})
        except ValueError:
            pass
    return data


def formatPosition(positionId):
    position = ''
    position = 'GK' if positionId == 'Goalkeeper' else position
    position = 'D' if positionId == 'Defender' else position
    position = 'M' if positionId == 'Midfielder' else position
    position = 'F' if positionId == 'Forward' else position

    return position
