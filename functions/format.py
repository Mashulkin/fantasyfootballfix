# -*- coding: utf-8 -*-
"""Formatting and data processing utilities with improved validation."""

import logging
from typing import Dict, Any, Union, Optional

# Add parent directory to path for imports
import addpath

from common_modules import clean_text, clean_price

__author__ = 'Vadim Arsenev'
__version__ = '2.0.0'
__date__ = '13.06.2025'


def format_null_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format null and zero data values to empty strings.
    
    Args:
        data (Dict[str, Any]): Dictionary with data to format
        
    Returns:
        Dict[str, Any]: Formatted data dictionary
    """
    if not isinstance(data, dict):
        logging.warning(f"Expected dict, got {type(data)}")
        return data
    
    formatted_data = data.copy()
    
    for key, value in formatted_data.items():
        try:
            # Check if value can be converted to float and is zero
            if value is not None and float(value) == 0:
                formatted_data[key] = ''
        except (ValueError, TypeError):
            # Keep non-numeric values as they are
            pass
    
    return formatted_data


def format_position(position_id: str) -> str:
    """
    Format player position from full name to abbreviation.
    
    Args:
        position_id (str): Full position name
        
    Returns:
        str: Position abbreviation
    """
    if not isinstance(position_id, str):
        logging.warning(f"Expected string position, got {type(position_id)}")
        return str(position_id) if position_id is not None else ''
    
    # Clean the input
    position_clean = clean_text(position_id).lower()
    
    # Position mapping
    position_map = {
        'goalkeeper': 'GK',
        'defender': 'D',
        'midfielder': 'M',
        'forward': 'F'
    }
    
    # Return mapped position or original if not found
    return position_map.get(position_clean, position_id)


def format_price(price: Union[str, int, float]) -> float:
    """
    Format price value to float with validation.
    
    Args:
        price (Union[str, int, float]): Price value
        
    Returns:
        float: Formatted price value
    """
    if price is None:
        return 0.0
    
    try:
        # If it's already a number
        if isinstance(price, (int, float)):
            return float(price)
        
        # If it's a string, use clean_price function
        return clean_price(str(price))
        
    except (ValueError, TypeError) as e:
        logging.warning(f"Could not format price '{price}': {e}")
        return 0.0


def format_percentage(value: Union[str, int, float], total: Union[str, int, float]) -> Optional[float]:
    """
    Calculate percentage with error handling.
    
    Args:
        value (Union[str, int, float]): Numerator value
        total (Union[str, int, float]): Denominator value
        
    Returns:
        Optional[float]: Percentage value or None if calculation fails
    """
    try:
        num_value = float(value) if value is not None else 0.0
        num_total = float(total) if total is not None else 0.0
        
        if num_total == 0:
            return None
        
        percentage = (num_value / num_total) * 100
        return round(percentage, 2)
        
    except (ValueError, TypeError, ZeroDivisionError) as e:
        logging.warning(f"Could not calculate percentage for {value}/{total}: {e}")
        return None


def format_gameweek_range(min_gw: int, max_gw: int) -> str:
    """
    Format gameweek range for display.
    
    Args:
        min_gw (int): Minimum gameweek
        max_gw (int): Maximum gameweek
        
    Returns:
        str: Formatted gameweek range
    """
    try:
        min_val = int(min_gw)
        max_val = int(max_gw)
        
        if min_val == max_val:
            return f"GW{min_val}"
        else:
            return f"GW{min_val}-{max_val}"
            
    except (ValueError, TypeError):
        return f"{min_gw}-{max_gw}"


def clean_player_name(name: str) -> str:
    """
    Clean and format player name.
    
    Args:
        name (str): Player name
        
    Returns:
        str: Cleaned player name
    """
    if not isinstance(name, str):
        return str(name) if name is not None else ''
    
    # Clean whitespace and normalize
    cleaned_name = clean_text(name)
    
    # Remove any special characters that might cause issues
    # Keep letters, numbers, spaces, hyphens, and apostrophes
    import re
    cleaned_name = re.sub(r"[^\w\s\-']", '', cleaned_name)
    
    return cleaned_name


def format_team_abbreviation(team_name: str) -> str:
    """
    Format team name to standard abbreviation.
    
    Args:
        team_name (str): Team name
        
    Returns:
        str: Team abbreviation
    """
    if not isinstance(team_name, str):
        return str(team_name) if team_name is not None else ''
    
    # Clean the team name
    cleaned_name = clean_text(team_name)
    
    # Common team abbreviations mapping
    team_map = {
        'Arsenal': 'ARS',
        'Aston Villa': 'AVL',
        'Brighton & Hove Albion': 'BHA',
        'Brighton': 'BHA',
        'Burnley': 'BUR',
        'Chelsea': 'CHE',
        'Crystal Palace': 'CRY',
        'Everton': 'EVE',
        'Fulham': 'FUL',
        'Liverpool': 'LIV',
        'Luton Town': 'LUT',
        'Manchester City': 'MCI',
        'Manchester United': 'MUN',
        'Newcastle United': 'NEW',
        'Newcastle': 'NEW',
        'Nottingham Forest': 'NFO',
        'Sheffield United': 'SHU',
        'Sheffield Utd': 'SHU',
        'Tottenham Hotspur': 'TOT',
        'Tottenham': 'TOT',
        'West Ham United': 'WHU',
        'West Ham': 'WHU',
        'Wolverhampton Wanderers': 'WOL',
        'Wolves': 'WOL',
        'Brentford': 'BRE',
        'Leicester City': 'LEI',
        'Leicester': 'LEI',
        'Leeds United': 'LEE',
        'Leeds': 'LEE',
        'Southampton': 'SOU',
        'Watford': 'WAT',
        'Norwich City': 'NOR',
        'Norwich': 'NOR'
    }
    
    # Return mapped abbreviation or original if not found
    return team_map.get(cleaned_name, cleaned_name)


def validate_player_data(player_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean player data.
    
    Args:
        player_data (Dict[str, Any]): Raw player data
        
    Returns:
        Dict[str, Any]: Validated and cleaned player data
    """
    if not isinstance(player_data, dict):
        logging.error(f"Expected dict for player data, got {type(player_data)}")
        return {}
    
    cleaned_data = player_data.copy()
    
    # Clean player name if present
    if 'known_name' in cleaned_data:
        cleaned_data['known_name'] = clean_player_name(cleaned_data['known_name'])
    
    # Format team abbreviation if present
    if 'abbr' in cleaned_data:
        cleaned_data['abbr'] = format_team_abbreviation(cleaned_data['abbr'])
    
    # Format position if present
    if 'position' in cleaned_data:
        cleaned_data['position'] = format_position(cleaned_data['position'])
    
    # Format price if present
    if 'price' in cleaned_data:
        cleaned_data['price'] = format_price(cleaned_data['price'])
    
    # Format null data
    cleaned_data = format_null_data(cleaned_data)
    
    return cleaned_data


def validate_team_data(team_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean team data.
    
    Args:
        team_data (Dict[str, Any]): Raw team data
        
    Returns:
        Dict[str, Any]: Validated and cleaned team data
    """
    if not isinstance(team_data, dict):
        logging.error(f"Expected dict for team data, got {type(team_data)}")
        return {}
    
    cleaned_data = team_data.copy()
    
    # Format team name if present
    if 'short_name' in cleaned_data:
        cleaned_data['short_name'] = format_team_abbreviation(cleaned_data['short_name'])
    
    # Format null data
    cleaned_data = format_null_data(cleaned_data)
    
    return cleaned_data


def calculate_expected_goals_involvement(exp_goals: float, exp_assists: float, exp_goals_team: float) -> Optional[float]:
    """
    Calculate expected goals involvement percentage.
    
    Args:
        exp_goals (float): Expected goals
        exp_assists (float): Expected assists
        exp_goals_team (float): Team's expected goals
        
    Returns:
        Optional[float]: Expected goals involvement percentage or None if calculation fails
    """
    try:
        total_exp_contribution = float(exp_goals) + float(exp_assists)
        team_exp_goals = float(exp_goals_team)
        
        if team_exp_goals == 0:
            return None
        
        involvement = (total_exp_contribution / team_exp_goals) * 100
        return round(involvement, 2)
        
    except (ValueError, TypeError, ZeroDivisionError) as e:
        logging.warning(f"Could not calculate expected goals involvement: {e}")
        return None


# Legacy function names for backward compatibility
def formatNullData(data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function name for backward compatibility."""
    return format_null_data(data)


def formatPosition(position_id: str) -> str:
    """Legacy function name for backward compatibility."""
    return format_position(position_id)
