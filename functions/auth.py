# -*- coding: utf-8 -*-
"""Authentication module for fantasy football fix parser."""

import logging
import re
import time
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup

# Add parent directory to path for imports
import addpath

from common_modules import Config, setup_parser_logger

__author__ = 'Vadim Arsenev'
__version__ = '1.0.0'
__date__ = '13.06.2025'


class FFFAuth:
    """Fantasy Football Fix authentication handler."""
    
    def __init__(self, email: str, password: str):
        """
        Initialize authentication handler.
        
        Args:
            email (str): User email
            password (str): User password
        """
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session_id = None
        self.csrf_token = None
        
        # Set up logger
        self.logger = setup_parser_logger('fff_auth')
        
        # Set default headers
        self.session.headers.update(Config.get_headers('chrome'))
        
        # Base URLs
        self.base_url = 'https://www.fantasyfootballfix.com'
        self.login_url = f'{self.base_url}/signin/'
        self.api_url = f'{self.base_url}/api/stats'
    
    def _get_csrf_token(self) -> bool:
        """
        Get CSRF token from login page.
        
        Returns:
            bool: True if CSRF token obtained successfully
        """
        try:
            self.logger.info("Getting CSRF token from login page")
            response = self.session.get(self.login_url)
            response.raise_for_status()
            
            # Parse HTML to find CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            
            if csrf_input and csrf_input.get('value'):
                self.csrf_token = csrf_input['value']
                self.logger.info("CSRF token obtained successfully")
                return True
            else:
                self.logger.error("CSRF token not found in login page")
                return False
                
        except Exception as e:
            self.logger.error(f"Error getting CSRF token: {e}")
            return False
    
    def _perform_login(self) -> bool:
        """
        Perform login with email and password.
        
        Returns:
            bool: True if login successful
        """
        try:
            if not self.csrf_token:
                if not self._get_csrf_token():
                    return False
            
            # Prepare login data
            login_data = {
                'csrfmiddlewaretoken': self.csrf_token,
                'email': self.email,
                'password': self.password,
                'next': '',
            }
            
            # Set referer header
            self.session.headers.update({
                'Referer': self.login_url,
                'Origin': self.base_url
            })
            
            self.logger.info(f"Attempting login for user: {self.email}")
            response = self.session.post(self.login_url, data=login_data)
            
            # Check if login was successful
            if response.status_code == 200:
                # Check for error messages in response
                if 'Invalid email or password' in response.text:
                    self.logger.error("Login failed: Invalid credentials")
                    return False
                
                # Check if we were redirected (successful login)
                if response.url != self.login_url:
                    self.logger.info("Login successful - redirected to dashboard")
                    return True
                
                # Check if we're on a success page
                if 'dashboard' in response.text.lower() or 'logout' in response.text.lower():
                    self.logger.info("Login successful - found dashboard content")
                    return True
                    
                self.logger.warning("Login status unclear - checking session")
                return self._verify_login()
                
            else:
                self.logger.error(f"Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False
    
    def _extract_session_id(self) -> bool:
        """
        Extract session ID from cookies.
        
        Returns:
            bool: True if session ID extracted successfully
        """
        try:
            # Look for sessionid cookie
            for cookie in self.session.cookies:
                if cookie.name == 'sessionid':
                    self.session_id = cookie.value
                    self.logger.info("Session ID extracted from cookies")
                    return True
            
            self.logger.error("Session ID not found in cookies")
            return False
            
        except Exception as e:
            self.logger.error(f"Error extracting session ID: {e}")
            return False
    
    def _verify_login(self) -> bool:
        """
        Verify login by making a test API request.
        
        Returns:
            bool: True if login verified successfully
        """
        try:
            # Test API endpoint
            test_url = f'{self.api_url}/players/?season=2024&min_gw=1&max_gw=1&home_away=home'
            
            self.logger.info("Verifying login with test API request")
            response = self.session.get(test_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.logger.info("Login verification successful")
                        return True
                except ValueError:
                    pass
            
            self.logger.error("Login verification failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying login: {e}")
            return False
    
    def authenticate(self) -> Optional[str]:
        """
        Perform full authentication process.
        
        Returns:
            Optional[str]: Session ID if authentication successful, None otherwise
        """
        self.logger.info("Starting authentication process")
        
        # Step 1: Get CSRF token
        if not self._get_csrf_token():
            return None
        
        # Step 2: Perform login
        if not self._perform_login():
            return None
        
        # Step 3: Extract session ID
        if not self._extract_session_id():
            return None
        
        # Step 4: Verify login
        if not self._verify_login():
            return None
        
        self.logger.info(f"Authentication completed successfully. Session ID: {self.session_id[:10]}...")
        return self.session_id
    
    def get_authenticated_session(self) -> Optional[requests.Session]:
        """
        Get authenticated session object.
        
        Returns:
            Optional[requests.Session]: Authenticated session if successful
        """
        if self.authenticate():
            return self.session
        return None
    
    def save_session_to_file(self, filepath: str) -> bool:
        """
        Save session ID to file for future use.
        
        Args:
            filepath (str): Path to save session file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if not self.session_id:
                self.logger.error("No session ID to save")
                return False
            
            # Create session info with timestamp
            session_info = {
                'session_id': self.session_id,
                'timestamp': int(time.time()),
                'email': self.email
            }
            
            # Save to JSON file
            from common_modules import json_write
            json_write(filepath, session_info)
            
            self.logger.info(f"Session saved to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            return False
    
    @classmethod
    def load_session_from_file(cls, filepath: str) -> Optional[str]:
        """
        Load session ID from file.
        
        Args:
            filepath (str): Path to session file
            
        Returns:
            Optional[str]: Session ID if loaded successfully
        """
        try:
            from common_modules import json_read
            session_info = json_read(filepath)
            
            if not session_info:
                return None
            
            # Check if session is not too old (2 weeks)
            current_time = int(time.time())
            session_age = current_time - session_info.get('timestamp', 0)
            max_age = 14 * 24 * 60 * 60  # 14 days in seconds
            
            if session_age > max_age:
                logging.warning("Saved session is too old, need to re-authenticate")
                return None
            
            return session_info.get('session_id')
            
        except Exception as e:
            logging.error(f"Error loading session: {e}")
            return None


def get_fff_session(email: str, password: str, force_new: bool = False) -> Optional[str]:
    """
    Get FFF session ID with automatic fallback to saved session.
    
    Args:
        email (str): User email
        password (str): User password
        force_new (bool): Force new authentication even if saved session exists
        
    Returns:
        Optional[str]: Session ID if successful
    """
    logger = setup_parser_logger('fff_session')
    session_file = Config.get_file_path('fff_session.json', 'temp')
    
    # Try to load existing session first (unless forced)
    if not force_new:
        session_id = FFFAuth.load_session_from_file(session_file)
        if session_id:
            logger.info("Using saved session ID")
            return session_id
    
    # Authenticate and get new session
    auth = FFFAuth(email, password)
    session_id = auth.authenticate()
    
    if session_id:
        # Save session for future use
        auth.save_session_to_file(session_file)
        logger.info("New session obtained and saved")
    else:
        logger.error("Authentication failed")
    
    return session_id
