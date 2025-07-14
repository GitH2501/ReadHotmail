import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ImportConfig


class HotmailAPI:

    API_HOST = "http://192.168.1.77"
    
    def __init__(self, debug_mode=None):
        self.session = self._create_session()
        self.debug_mode = debug_mode if debug_mode is not None else ImportConfig.DEBUG_MODE
    
    def _create_session(self):
        """Create a session with connection pooling and retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=ImportConfig.API_MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy, 
            pool_connections=ImportConfig.POOL_CONNECTIONS, 
            pool_maxsize=ImportConfig.POOL_MAXSIZE
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
        
    # def __init__(self, api_key: str):
    #     self.api_key = api_key
    def get_hotmail_info(self):
        self.API_GET = f"{self.API_HOST}/api/v1/profiles/"
        self.header = { 
            'content-type': 'application/json'
        }

        req = self.session.get(url=self.API_GET, headers=self.header, timeout=10)
        if req.status_code == 200:
            data = req.json()
            print(f"result: {data}")
            return data
        else:
            print(f"Error fetching hotmail info: {req.status_code}, {req.text}")
            return []
        
        
    async def get_hotmail_info_for_id(self, profile_id):
        """Get hotmail info for a single profile ID"""
        return self.get_hotmail_info_for_id_sync(profile_id)
    
    def get_hotmail_info_for_id_sync(self, profile_id: str) -> Dict:
        """Synchronous version for better performance"""
        self.API_GET = f"{self.API_HOST}/api/v1/profiles/{profile_id}"
        self.header = { 
            'content-type': 'application/json'
        }

        try:
            req = self.session.get(url=self.API_GET, headers=self.header, timeout=ImportConfig.API_TIMEOUT)
            if req.status_code == 200:
                data = req.json()
                # Chỉ log khi được cấu hình
                if self.debug_mode and ImportConfig.SHOW_SUCCESS_LOGS:
                    print(f"result: {data}")
                return data
            else:
                # Kiểm soát log lỗi theo config
                should_log = (
                    (req.status_code != 404 or ImportConfig.SHOW_404_ERRORS) and 
                    ImportConfig.SHOW_API_ERRORS
                )
                if should_log:
                    print(f"Error fetching hotmail info: {req.status_code}, {req.text}")
                return {}
        except Exception as e:
            print(f"Exception fetching hotmail info for {profile_id}: {e}")
            return {}
    
    def get_hotmail_info_batch(self, profile_ids: List[str]) -> Dict[str, Dict]:
        """Get hotmail info for multiple profile IDs in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        def fetch_single(profile_id):
            try:
                data = self.get_hotmail_info_for_id_sync(profile_id)
                return profile_id, data
            except Exception as e:
                if self.debug_mode:
                    print(f"Error fetching hotmail info for {profile_id}: {e}")
                return profile_id, {}
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=ImportConfig.MAX_WORKERS) as executor:
            future_to_id = {executor.submit(fetch_single, profile_id): profile_id for profile_id in profile_ids}
            
            for future in as_completed(future_to_id):
                try:
                    profile_id, data = future.result()
                    results[profile_id] = data
                except Exception as e:
                    profile_id = future_to_id[future]
                    if self.debug_mode:
                        print(f"Error processing hotmail profile {profile_id}: {e}")
                    results[profile_id] = {}
        
        return results

    def create_hotmail_profile(self,data_create: dict):
        self.API_POST = f"{self.API_HOST}/api/v1/profiles/"
        self.header = {
            'content-type':'application/json'
        }
        self.body = {
            "profile_name": data_create.get("profile_name"),
            "password": data_create.get("password"),
            "browser_id": data_create.get("browser_id"),
            "access_token": data_create.get("access_token"),
            "refresh_token": data_create.get("refresh_token"),
            "error": data_create.get("error"),
            "status": data_create.get("status"),
            "profile_id": data_create.get("profile_id"),
        }
        req = self.session.post(url=self.API_POST,headers=self.header,json=self.body, timeout=ImportConfig.API_TIMEOUT)
        if req.status_code == 200:
            print("create profile hotmail success")
            return True
        else:
            print("create profile hotmail failed")
            print(f"Status code: {req.status_code}, Response: {req.text}")
            return False

    def update_token_hotmail(self,id_profile, access_token: str, refresh_token: str):
        self.API_UPDATE = f"{self.API_HOST}/api/v1/profiles/{id_profile}"
        self.header = {
            'content-type':'application/json'
        }
        self.body = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        req = self.session.put(url=self.API_UPDATE,headers=self.header,json=self.body, timeout=ImportConfig.API_TIMEOUT)
        if req.status_code == 200:
            print("Update token success")
            return True
        else:
            print("Update token failed")
            print(f"Status code: {req.status_code}, Response: {req.text}")
            return False
