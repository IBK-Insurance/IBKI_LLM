import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Union, Tuple, List
from pathlib import Path
import json
import urllib.parse

class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            base_url (str): Base URL of the API
            api_key (str, optional): API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.is_authenticated = False
        self.auth_token = None
        self.user_info = None
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
            self.is_authenticated = True

    def login(self, username: str, password: str, login_endpoint: str = 'auth/login') -> Tuple[bool, str]:
        """
        Authenticate with the API using username and password
        
        Args:
            username (str): Username for authentication
            password (str): Password for authentication
            login_endpoint (str, optional): Login endpoint path
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            login_data = {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
            
            url = f"{self.base_url}/token"
            print(f"\nSending login request to: {url}")
            print(f"Login data: {{'grant_type': 'password', 'username': '{username}', 'password': '****'}}")
            
            # Use form-data instead of JSON
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = self.session.post(url, data=login_data, headers=headers)
            print(f"Login response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Store user info if available
                if 'user' in data:
                    self.user_info = data['user']
                
                # Check for different token formats in the response
                token = None
                if 'token' in data:
                    token = data['token']
                elif 'access_token' in data:
                    token = data['access_token']
                elif 'jwt' in data:
                    token = data['jwt']
                
                if token:
                    self.auth_token = token
                    self.session.headers.update({
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    })
                    self.is_authenticated = True
                    return True, "Login successful"
                else:
                    return False, "Login response does not contain authentication token"
            else:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    error_msg = response.text
                return False, f"Login failed with status code: {response.status_code}, Error: {error_msg}"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get current authentication information
        
        Returns:
            Dict[str, Any]: Authentication information including token and user info
        """
        return {
            'is_authenticated': self.is_authenticated,
            'auth_token': self.auth_token,
            'user_info': self.user_info
        }
    
    def logout(self, logout_endpoint: str = 'auth/logout') -> Tuple[bool, str]:
        """
        Logout from the API
        
        Args:
            logout_endpoint (str, optional): Logout endpoint path
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            if not self.is_authenticated:
                return False, "Not authenticated"
                
            response = self.session.post(f"{self.base_url}/{logout_endpoint}")
            
            if response.status_code == 200:
                self.is_authenticated = False
                self.auth_token = None
                self.user_info = None
                # Remove the authorization header
                if 'Authorization' in self.session.headers:
                    del self.session.headers['Authorization']
                return True, "Logout successful"
            else:
                return False, f"Logout failed with status code: {response.status_code}"
                
        except Exception as e:
            return False, f"Logout error: {str(e)}"

    def _build_url(self, endpoint: str, path_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build URL with path parameters
        
        Args:
            endpoint (str): API endpoint
            path_params (dict, optional): Path parameters to replace in the endpoint
            
        Returns:
            str: Built URL
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if path_params:
            for key, value in path_params.items():
                url = url.replace(f"{{{key}}}", str(value))
        
        return url

    def _process_query_params(self, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process query parameters for URL
        
        Args:
            params (dict, optional): Query parameters
            
        Returns:
            dict: Processed query parameters
        """
        if not params:
            return None
            
        processed_params = {}
        for key, value in params.items():
            if isinstance(value, list):
                # Handle array parameters
                for item in value:
                    if key not in processed_params:
                        processed_params[key] = []
                    processed_params[key].append(str(item))
            else:
                processed_params[key] = str(value)
                
        return processed_params

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            path_params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None,
            stream: bool = False) -> requests.Response:
        """
        Send GET request to the API
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            path_params (dict, optional): Path parameters to replace in the endpoint
            headers (dict, optional): Additional headers for the request
            stream (bool, optional): Whether to stream the response
            
        Returns:
            requests.Response: Response from the API
        """
        if not self.is_authenticated and not self.api_key:
            raise Exception("Not authenticated. Please login first.")
            
        url = self._build_url(endpoint, path_params)
        query_params = self._process_query_params(params)
        
        # Merge headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
            
        print(f"\nSending GET request to: {url}")
        if query_params:
            print(f"Query parameters: {query_params}")
            
        response = self.session.get(url, params=query_params, headers=request_headers, stream=stream)
        print(f"Response status code: {response.status_code}")
        return response

    def post(self, endpoint: str, data: Dict[str, Any], 
             path_params: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             json_data: bool = True) -> requests.Response:
        """
        Send POST request to the API
        
        Args:
            endpoint (str): API endpoint
            data (dict): Data to send in the request body
            path_params (dict, optional): Path parameters to replace in the endpoint
            headers (dict, optional): Additional headers for the request
            json_data (bool, optional): Whether to send data as JSON
            
        Returns:
            requests.Response: Response from the API
        """
        if not self.is_authenticated and not self.api_key:
            raise Exception("Not authenticated. Please login first.")
            
        url = self._build_url(endpoint, path_params)
        
        # Merge headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
            
        print(f"\nSending POST request to: {url}")
        print(f"Request data: {data}")
            
        if json_data:
            response = self.session.post(url, json=data, headers=request_headers)
        else:
            response = self.session.post(url, data=data, headers=request_headers)
            
        print(f"Response status code: {response.status_code}")
        return response

    def put(self, endpoint: str, data: Dict[str, Any], 
            path_params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            json_data: bool = True) -> requests.Response:
        """
        Send PUT request to the API
        
        Args:
            endpoint (str): API endpoint
            data (dict): Data to send in the request body
            path_params (dict, optional): Path parameters to replace in the endpoint
            headers (dict, optional): Additional headers for the request
            json_data (bool, optional): Whether to send data as JSON
            
        Returns:
            requests.Response: Response from the API
        """
        if not self.is_authenticated and not self.api_key:
            raise Exception("Not authenticated. Please login first.")
            
        url = self._build_url(endpoint, path_params)
        
        # Merge headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
            
        print(f"\nSending PUT request to: {url}")
        print(f"Request data: {data}")
            
        if json_data:
            response = self.session.put(url, json=data, headers=request_headers)
        else:
            response = self.session.put(url, data=data, headers=request_headers)
            
        print(f"Response status code: {response.status_code}")
        return response

    def delete(self, endpoint: str, 
               path_params: Optional[Dict[str, Any]] = None,
               headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Send DELETE request to the API
        
        Args:
            endpoint (str): API endpoint
            path_params (dict, optional): Path parameters to replace in the endpoint
            headers (dict, optional): Additional headers for the request
            
        Returns:
            requests.Response: Response from the API
        """
        if not self.is_authenticated and not self.api_key:
            raise Exception("Not authenticated. Please login first.")
            
        url = self._build_url(endpoint, path_params)
        
        # Merge headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
            
        print(f"\nSending DELETE request to: {url}")
            
        response = self.session.delete(url, headers=request_headers)
        print(f"Response status code: {response.status_code}")
        return response

    def download_file(self, endpoint: str, save_path: Union[str, Path], 
                     params: Optional[Dict[str, Any]] = None,
                     path_params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None) -> Path:
        """
        Download a file from the API
        
        Args:
            endpoint (str): API endpoint
            save_path (str or Path): Path where the file should be saved
            params (dict, optional): Query parameters
            path_params (dict, optional): Path parameters to replace in the endpoint
            headers (dict, optional): Additional headers for the request
            
        Returns:
            Path: Path to the downloaded file
            
        Raises:
            requests.exceptions.RequestException: If the download fails
            IOError: If the file cannot be saved
        """
        if not self.is_authenticated and not self.api_key:
            raise Exception("Not authenticated. Please login first.")
            
        save_path = Path(save_path)
        
        # Create directory if it doesn't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get filename from Content-Disposition header or use endpoint name
        response = self.get(endpoint, params=params, path_params=path_params, headers=headers, stream=True)
        response.raise_for_status()
        
        # Try to get filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            import re
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                save_path = save_path.parent / filename_match.group(1)
        
        # Download the file
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return save_path 