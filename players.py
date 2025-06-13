# -*- coding: utf-8 -*-
"""
Getting information about players on Fantasy Football Fix with improved features.
- Automatic authentication
- Enhanced error handling
- Comprehensive logging
- Data validation
- Progress tracking
"""

import argparse
import os
import sys
import time
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
import addpath

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common_modules import (
    write_csv, read_txt, print_headline, remove_file,
    setup_parser_logger, Config, validate_required_fields
)
from functions.auth import get_fff_session
from functions.statistic import FFFStatsClient
from functions.format import (
    validate_player_data, format_position, format_null_data,
    calculate_expected_goals_involvement, format_gameweek_range
)

__author__ = 'Vadim Arsenev'
__version__ = '2.0.0'
__date__ = '13.06.2025'


class FFFPlayersParser:
    """Fantasy Football Fix players data parser with enhanced features."""
    
    def __init__(self, config_path: str = './settings/general.py'):
        """
        Initialize parser with configuration.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.logger = setup_parser_logger('fff_players')
        self.config_path = config_path
        
        # Ensure required directories exist
        Config.ensure_directories()
        
        # Load configuration
        self._load_config()
        
        # Initialize stats client
        self.stats_client = None
        
        # Processing statistics
        self.processing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'players_processed': 0,
            'errors_encountered': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _load_config(self):
        """Load configuration from settings file."""
        try:
            # Try to load simple_settings configuration
            from simple_settings import settings
            
            self.api_url = getattr(settings, 'API_URL', 'https://www.fantasyfootballfix.com/api/stats')
            self.session_id = getattr(settings, 'SESSIONID', None)
            self.year = getattr(settings, 'YEAR', '2024')
            self.columns_file = getattr(settings, 'COLUMNS', './settings/FFFplayers.txt')
            self.result_files = getattr(settings, 'RESULT_FILE', ['./data/FFFplayers.csv'])
            
            # Authentication credentials (if available)
            self.email = getattr(settings, 'EMAIL', None)
            self.password = getattr(settings, 'PASSWORD', None)
            
            self.logger.info("Configuration loaded from simple_settings")
            
        except ImportError:
            # Fallback to default configuration
            self.logger.warning("simple_settings not available, using default configuration")
            self.api_url = 'https://www.fantasyfootballfix.com/api/stats'
            self.session_id = None
            self.year = '2024'
            self.columns_file = './settings/FFFplayers.txt'
            self.result_files = ['./data/FFFplayers.csv']
            self.email = None
            self.password = None
    
    def _get_column_order(self) -> List[str]:
        """
        Get column order from settings file.
        
        Returns:
            List[str]: List of column names in order
        """
        try:
            columns_text = read_txt(self.columns_file)
            if not columns_text:
                raise ValueError(f"Empty columns file: {self.columns_file}")
            
            # Parse column definitions (format: key:value per line)
            order = []
            for line in columns_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    key = line.split(':', 1)[0].strip()
                    order.append(key)
            
            if not order:
                raise ValueError("No valid columns found")
            
            self.logger.info(f"Loaded {len(order)} columns from {self.columns_file}")
            return order
            
        except Exception as e:
            self.logger.error(f"Error loading column order: {e}")
            # Return default order as fallback
            return ['known_name', 'abbr', 'position', 'price', 'goals', 'assists']
    
    def _authenticate(self) -> bool:
        """
        Authenticate and get session ID.
        
        Returns:
            bool: True if authentication successful
        """
        # If session_id is already available, validate it first
        if self.session_id:
            self.logger.info("Using existing session ID from configuration")
            self.stats_client = FFFStatsClient(self.api_url, self.session_id)
            
            # Test the session with a simple request
            test_data = self.stats_client.get_players_stats(1, 1, 'home', self.year)
            if test_data is not None:
                self.logger.info("Existing session ID is valid")
                return True
            else:
                self.logger.warning("Existing session ID is invalid, need to re-authenticate")
        
        # Check if we have credentials for authentication
        if not self.email or not self.password:
            self.logger.error("No valid session ID and no credentials provided for authentication")
            self.logger.error("Please provide EMAIL and PASSWORD in settings or valid SESSIONID")
            return False
        
        # Perform authentication
        self.logger.info("Performing authentication")
        session_id = get_fff_session(self.email, self.password)
        
        if session_id:
            self.session_id = session_id
            self.stats_client = FFFStatsClient(self.api_url, self.session_id)
            self.logger.info("Authentication successful")
            return True
        else:
            self.logger.error("Authentication failed")
            return False
    
    def _process_player_data(self, stats: List[Dict], min_gw: int, venue: str) -> Dict[tuple, Dict]:
        """
        Process raw player statistics into formatted data.
        
        Args:
            stats (List[Dict]): Raw player statistics
            min_gw (int): Minimum gameweek
            venue (str): Venue (home/away/home/away)
            
        Returns:
            Dict[tuple, Dict]: Processed player data keyed by (name, team)
        """
        if not stats:
            self.logger.warning("No player statistics to process")
            return {}
        
        processed_data = {}
        
        for item in stats:
            try:
                # Extract player information
                player_info = item.get('player', {})
                stats_info = item.get('stats', {})
                
                # Required fields validation
                required_fields = ['code', 'known_name', 'team_short_name', 'position_name', 'price']
                missing_fields = []
                for field in required_fields:
                    if field not in player_info:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.logger.warning(f"Player missing required fields {missing_fields}, skipping")
                    continue
                
                # Extract basic player data
                player_id = player_info['code']
                known_name = player_info['known_name']
                abbr = player_info['team_short_name']
                position = format_position(player_info['position_name'])
                price = player_info['price']
                game_started = stats_info.get('game_started', 0)
                
                # Calculate expected goals + assists
                exp_goals = stats_info.get('exp_goals', 0) or 0
                exp_assists = stats_info.get('exp_assists', 0) or 0
                exp_ga = exp_goals + exp_assists
                
                # Calculate expected goals involvement
                exp_goals_team = stats_info.get('exp_goals_team', 0) or 0
                exp_goals_involvement = calculate_expected_goals_involvement(
                    exp_goals, exp_assists, exp_goals_team
                )
                
                # Filter stats to only include columns we want
                order = self._get_column_order()
                filtered_stats = {}
                for key in stats_info.keys():
                    if key in order:
                        filtered_stats[key] = stats_info[key]
                
                # Build complete player record
                player_record = {
                    'known_name': known_name,
                    'playerId': player_id,
                    'abbr': abbr,
                    'position': position,
                    'price': price,
                    'expGA': exp_ga,
                    'exp_goals_involvement': exp_goals_involvement,
                    'gw': min_gw,
                    'venue': venue,
                    'game_started': game_started,
                    **filtered_stats  # Add all filtered stats
                }
                
                # Validate and clean the data
                player_record = validate_player_data(player_record)
                
                # Use (name, team) as key for uniqueness
                key = (known_name, abbr)
                processed_data[key] = player_record
                
                self.processing_stats['players_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing player data: {e}")
                self.processing_stats['errors_encountered'] += 1
                continue
        
        self.logger.info(f"Processed {len(processed_data)} players successfully")
        return processed_data
    
    def _save_data(self, data: Dict[tuple, Dict], order: List[str]):
        """
        Save processed data to CSV files.
        
        Args:
            data (Dict[tuple, Dict]): Processed player data
            order (List[str]): Column order for CSV
        """
        if not data:
            self.logger.warning("No data to save")
            return
        
        for result_file in self.result_files:
            try:
                # Write header if file doesn't exist
                print_headline(result_file, self.columns_file, order)
                
                # Write player data
                for player_data in data.values():
                    write_csv(result_file, player_data, order)
                
                self.logger.info(f"Data saved to {result_file}")
                
            except Exception as e:
                self.logger.error(f"Error saving data to {result_file}: {e}")
    
    def parse_gameweek_range(
        self, 
        min_gw: int, 
        max_gw: int, 
        venue: str
    ) -> bool:
        """
        Parse data for a specific gameweek range.
        
        Args:
            min_gw (int): Minimum gameweek
            max_gw (int): Maximum gameweek
            venue (str): Venue filter
            
        Returns:
            bool: True if parsing successful
        """
        try:
            self.processing_stats['total_requests'] += 1
            
            gw_range = format_gameweek_range(min_gw, max_gw)
            self.logger.info(f"Parsing {gw_range} data for venue: {venue}")
            
            # Get data from API
            stats = self.stats_client.get_players_stats(min_gw, max_gw, venue, self.year)
            
            if stats is None:
                self.logger.error(f"Failed to get data for {gw_range}, venue: {venue}")
                return False
            
            # Process the data
            processed_data = self._process_player_data(stats, min_gw, venue)
            
            if not processed_data:
                self.logger.warning(f"No valid data processed for {gw_range}, venue: {venue}")
                return False
            
            # Save the data
            order = self._get_column_order()
            self._save_data(processed_data, order)
            
            self.processing_stats['successful_requests'] += 1
            self.logger.info(f"Successfully completed {gw_range}, venue: {venue}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error parsing gameweek range {min_gw}-{max_gw}: {e}")
            self.processing_stats['errors_encountered'] += 1
            return False
    
    def parse_full_season(self, venue: str = 'home/away') -> bool:
        """
        Parse data for all gameweeks individually.
        
        Args:
            venue (str): Venue filter
            
        Returns:
            bool: True if parsing successful
        """
        self.logger.info(f"Starting full season parse for venue: {venue}")
        self.processing_stats['start_time'] = time.time()
        
        success_count = 0
        total_gameweeks = 38
        
        for gw in range(1, total_gameweeks + 1):
            try:
                self.logger.info(f"Processing gameweek {gw}/{total_gameweeks}")
                
                if venue == 'home/away':
                    # Parse both home and away for this gameweek
                    success_home = self.parse_gameweek_range(gw, gw, 'home')
                    success_away = self.parse_gameweek_range(gw, gw, 'away')
                    
                    if success_home and success_away:
                        success_count += 1
                else:
                    # Parse specified venue only
                    if self.parse_gameweek_range(gw, gw, venue):
                        success_count += 1
                
                # Add small delay between requests
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.warning("Process interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error processing gameweek {gw}: {e}")
                continue
        
        self.processing_stats['end_time'] = time.time()
        
        # Log final statistics
        self._log_final_stats(success_count, total_gameweeks)
        
        return success_count > 0
    
    def _log_final_stats(self, successful_gameweeks: int, total_gameweeks: int):
        """Log final processing statistics."""
        duration = 0
        if self.processing_stats['start_time'] and self.processing_stats['end_time']:
            duration = self.processing_stats['end_time'] - self.processing_stats['start_time']
        
        final_stats = {
            'successful_gameweeks': successful_gameweeks,
            'total_gameweeks': total_gameweeks,
            'success_rate': f"{(successful_gameweeks/total_gameweeks)*100:.1f}%" if total_gameweeks > 0 else "0%",
            'duration_seconds': round(duration, 2),
            'players_processed': self.processing_stats['players_processed'],
            'errors_encountered': self.processing_stats['errors_encountered']
        }
        
        # Log API client stats as well
        if self.stats_client:
            api_stats = self.stats_client.get_stats_summary()
            final_stats.update(api_stats)
        
        from common_modules.logger import log_parser_stats
        log_parser_stats(self.logger, final_stats)
    
    def run(self, min_gw: int = 1, max_gw: int = 38, venue: str = 'home/away') -> bool:
        """
        Main execution method.
        
        Args:
            min_gw (int): Minimum gameweek
            max_gw (int): Maximum gameweek
            venue (str): Venue filter
            
        Returns:
            bool: True if execution successful
        """
        self.logger.info("=== Fantasy Football Fix Players Parser Started ===")
        
        try:
            # Step 1: Authenticate
            if not self._authenticate():
                return False
            
            # Step 2: Clear existing output files
            for result_file in self.result_files:
                remove_file(result_file)
                self.logger.info(f"Cleared existing file: {result_file}")
            
            # Step 3: Parse data
            if min_gw == 1 and max_gw == 38:
                # Full season parse (individual gameweeks for better granularity)
                success = self.parse_full_season(venue)
            else:
                # Single gameweek range parse
                success = self.parse_gameweek_range(min_gw, max_gw, venue)
            
            if success:
                self.logger.info("=== Parsing completed successfully ===")
            else:
                self.logger.error("=== Parsing completed with errors ===")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Critical error in parser execution: {e}")
            return False


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Fantasy Football Fix Players Parser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python players.py                          # Parse full season, both venues
  python players.py --min-gw 1 --max-gw 5   # Parse first 5 gameweeks
  python players.py --venue home             # Parse only home games
  python players.py --min-gw 10 --max-gw 10 --venue away  # Parse GW10 away only
        """
    )
    
    parser.add_argument(
        '--min-gw', 
        type=int, 
        default=1,
        help='Minimum gameweek (1-38, default: 1)'
    )
    parser.add_argument(
        '--max-gw', 
        type=int, 
        default=38,
        help='Maximum gameweek (1-38, default: 38)'
    )
    parser.add_argument(
        '--venue', 
        choices=['home/away', 'home', 'away'],
        default='home/away',
        help='Venue filter (default: home/away)'
    )
    parser.add_argument(
        '--config', 
        default='./settings/general.py',
        help='Path to configuration file (default: ./settings/general.py)'
    )
    
    args = parser.parse_args()
    
    # Validate gameweek range
    if not (1 <= args.min_gw <= 38) or not (1 <= args.max_gw <= 38):
        print("Error: Gameweeks must be between 1 and 38")
        return 1
    
    if args.min_gw > args.max_gw:
        print("Error: min-gw cannot be greater than max-gw")
        return 1
    
    # Create and run parser
    fff_parser = FFFPlayersParser(args.config)
    success = fff_parser.run(args.min_gw, args.max_gw, args.venue)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
