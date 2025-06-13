# -*- coding: utf-8 -*-
"""Making requests to Fantasy Football Fix API with improved error handling."""

import time
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
import addpath

from common_modules import Parser, setup_parser_logger, validate_required_fields

__author__ = 'Vadim Arsenev'
__version__ = '2.0.0'
__date__ = '13.06.2025'


class FFFStatsClient:
    """Client for Fantasy Football Fix statistics API."""
    
    def __init__(self, api_url: str, session_id: str):
        """
        Initialize stats client.
        
        Args:
            api_url (str): Base API URL
            session_id (str): Authentication session ID
        """
        self.api_url = api_url
        self.session_id = session_id
        self.logger = setup_parser_logger('fff_stats')
        
        # Request statistics
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_players_fetched': 0,
            'total_teams_fetched': 0
        }
    
    def _make_request(self, url: str, description: str = "") -> Optional[List[Dict]]:
        """
        Make authenticated request to FFF API.
        
        Args:
            url (str): Request URL
            description (str): Description for logging
            
        Returns:
            Optional[List[Dict]]: API response data or None if failed
        """
        try:
            self.stats['requests_made'] += 1
            
            self.logger.info(f"Making request: {description}")
            self.logger.debug(f"URL: {url}")
            
            # Create parser with session cookie
            parser = Parser(
                url=url, 
                cookies={'sessionid': self.session_id},
                timeout=30,
                retries=3
            )
            
            # Add delay to be respectful to the server
            time.sleep(1)
            
            # Get data
            data = parser.parser_result()
            
            if data and isinstance(data, list):
                self.stats['successful_requests'] += 1
                self.logger.info(f"Request successful: {len(data)} items received")
                return data
            else:
                self.stats['failed_requests'] += 1
                self.logger.warning(f"Request returned empty or invalid data: {type(data)}")
                return None
                
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.logger.error(f"Request failed for {description}: {e}")
            return None
    
    def get_players_stats(
        self, 
        min_gw: int, 
        max_gw: int, 
        venue: str, 
        season: str
    ) -> Optional[List[Dict]]:
        """
        Get player statistics from FFF API.
        
        Args:
            min_gw (int): Minimum gameweek
            max_gw (int): Maximum gameweek
            venue (str): Venue filter (home/away, home, away)
            season (str): Season year
            
        Returns:
            Optional[List[Dict]]: Player statistics or None if failed
        """
        # Validate parameters
        required_params = {
            'min_gw': min_gw,
            'max_gw': max_gw,
            'venue': venue,
            'season': season
        }
        
        missing_fields = validate_required_fields(required_params, list(required_params.keys()))
        if missing_fields:
            self.logger.error(f"Missing required parameters: {missing_fields}")
            return None
        
        # Validate gameweek range
        if not (1 <= min_gw <= 38) or not (1 <= max_gw <= 38):
            self.logger.error(f"Invalid gameweek range: {min_gw}-{max_gw}")
            return None
        
        if min_gw > max_gw:
            self.logger.error(f"min_gw ({min_gw}) cannot be greater than max_gw ({max_gw})")
            return None
        
        # Validate venue
        valid_venues = ['home/away', 'home', 'away']
        if venue not in valid_venues:
            self.logger.error(f"Invalid venue '{venue}'. Must be one of: {valid_venues}")
            return None
        
        # Build URL
        url = (
            f'{self.api_url}/players/?season={season}&min_gw={min_gw}'
            f'&max_gw={max_gw}&home_away={venue}'
        )
        
        description = f"Players stats (GW{min_gw}-{max_gw}, {venue}, {season})"
        
        # Make request
        data = self._make_request(url, description)
        
        if data:
            self.stats['total_players_fetched'] += len(data)
            self.logger.info(f"Retrieved {len(data)} players")
        
        return data
    
    def get_teams_stats(
        self, 
        min_gw: int, 
        max_gw: int, 
        venue: str, 
        season: str
    ) -> Optional[List[Dict]]:
        """
        Get team statistics from FFF API.
        
        Args:
            min_gw (int): Minimum gameweek
            max_gw (int): Maximum gameweek
            venue (str): Venue filter (home/away, home, away)
            season (str): Season year
            
        Returns:
            Optional[List[Dict]]: Team statistics or None if failed
        """
        # Validate parameters (same as players)
        required_params = {
            'min_gw': min_gw,
            'max_gw': max_gw,
            'venue': venue,
            'season': season
        }
        
        missing_fields = validate_required_fields(required_params, list(required_params.keys()))
        if missing_fields:
            self.logger.error(f"Missing required parameters: {missing_fields}")
            return None
        
        # Validate gameweek range
        if not (1 <= min_gw <= 38) or not (1 <= max_gw <= 38):
            self.logger.error(f"Invalid gameweek range: {min_gw}-{max_gw}")
            return None
        
        if min_gw > max_gw:
            self.logger.error(f"min_gw ({min_gw}) cannot be greater than max_gw ({max_gw})")
            return None
        
        # Validate venue
        valid_venues = ['home/away', 'home', 'away']
        if venue not in valid_venues:
            self.logger.error(f"Invalid venue '{venue}'. Must be one of: {valid_venues}")
            return None
        
        # Build URL
        url = (
            f'{self.api_url}/teams/?season={season}&min_gw={min_gw}'
            f'&max_gw={max_gw}&home_away={venue}&opposition=ALL'
        )
        
        description = f"Teams stats (GW{min_gw}-{max_gw}, {venue}, {season})"
        
        # Make request
        data = self._make_request(url, description)
        
        if data:
            self.stats['total_teams_fetched'] += len(data)
            self.logger.info(f"Retrieved {len(data)} teams")
        
        return data
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """
        Get summary of all requests made.
        
        Returns:
            Dict[str, Any]: Statistics summary
        """
        success_rate = 0
        if self.stats['requests_made'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['requests_made']) * 100
        
        return {
            **self.stats,
            'success_rate_percent': round(success_rate, 2)
        }
    
    def log_stats_summary(self):
        """Log statistics summary."""
        from common_modules.logger import log_parser_stats
        summary = self.get_stats_summary()
        log_parser_stats(self.logger, summary)


# Legacy functions for backward compatibility
def get_statistic_players(min_gw: int, max_gw: int, venue: str, season: str, session_id: str = None) -> Optional[List[Dict]]:
    """
    Legacy function for getting player statistics.
    
    Args:
        min_gw (int): Minimum gameweek
        max_gw (int): Maximum gameweek
        venue (str): Venue filter
        season (str): Season year
        session_id (str): Session ID (for backward compatibility)
        
    Returns:
        Optional[List[Dict]]: Player statistics
    """
    if not session_id:
        # Try to get from settings for backward compatibility
        try:
            from simple_settings import settings
            session_id = settings.SESSIONID
            api_url = settings.API_URL
        except ImportError:
            raise ValueError("session_id is required when simple_settings is not available")
    else:
        api_url = 'https://www.fantasyfootballfix.com/api/stats'
    
    client = FFFStatsClient(api_url, session_id)
    return client.get_players_stats(min_gw, max_gw, venue, season)


def get_statistic_teams(min_gw: int, max_gw: int, venue: str, season: str, session_id: str = None) -> Optional[List[Dict]]:
    """
    Legacy function for getting team statistics.
    
    Args:
        min_gw (int): Minimum gameweek
        max_gw (int): Maximum gameweek
        venue (str): Venue filter
        season (str): Season year
        session_id (str): Session ID (for backward compatibility)
        
    Returns:
        Optional[List[Dict]]: Team statistics
    """
    if not session_id:
        # Try to get from settings for backward compatibility
        try:
            from simple_settings import settings
            session_id = settings.SESSIONID
            api_url = settings.API_URL
        except ImportError:
            raise ValueError("session_id is required when simple_settings is not available")
    else:
        api_url = 'https://www.fantasyfootballfix.com/api/stats'
    
    client = FFFStatsClient(api_url, session_id)
    return client.get_teams_stats(min_gw, max_gw, venue, season)
