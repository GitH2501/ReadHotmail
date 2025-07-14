from fastapi import UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import io
from jinja2 import Template
from models.account import Account
from models.fingerprint import Fingerprint
from models.browser import Browser
from models.model import Model
from api.EofficeAPI import EofficeAPI
from api.HotmailAPI import HotmailAPI
import sqlite3
import asyncio
from typing import List, Dict, Any
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ImportConfig

# Cấu hình debug mode từ environment variable
DEBUG_MODE = os.getenv('IMPORT_DEBUG', 'false').lower() == 'true'

account_model = Account()
fingerprint_model = Fingerprint()
browser_model = Browser()
eoffice_api = EofficeAPI(debug_mode=DEBUG_MODE)
model = Model()
hotmail_api = HotmailAPI(debug_mode=DEBUG_MODE)

page = 1
limit = 13

# Connection pool cho HTTP requests
session = None

def get_session():
    global session
    if session is None:
        session = requests.Session()
        retry_strategy = Retry(
            total=ImportConfig.API_MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=ImportConfig.POOL_CONNECTIONS, pool_maxsize=ImportConfig.POOL_MAXSIZE)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    return session

def close_session():
    global session
    if session:
        session.close()
        session = None

async def clear_old_data():
    try:
        conn = sqlite3.connect(model.database)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM account")
        cursor.execute("DELETE FROM browser")
        cursor.execute("DELETE FROM fingerprint")
        conn.commit()
        conn.close()
        print("Đã xóa dữ liệu cũ thành công")
    except Exception as e:
        print(f"Lỗi khi xóa dữ liệu cũ: {e}")

async def import_profile_task(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        model.createDB()
        await clear_old_data()
        content = await file.read()
        if file.filename and file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
            df = df.where(pd.notnull(df), None)
            table_data = df.to_dict("records")
            
            print(f"Bắt đầu import {len(table_data)} profiles...")
            
            try:
                check_write_db = await write_sync_localdb_onlinedb_optimized(table_data)
            except Exception as e:
                print(f"Lỗi import: {e}")
                close_session()
                hotmail_api.close()
                eoffice_api.close()
                return HTMLResponse(
                    content=f"<tr><td colspan='7' style='color: red;'>Error: {str(e)}</td></tr>",
                    status_code=500
                )
            
            close_session()
            hotmail_api.close()
            eoffice_api.close()
            
            if not check_write_db:
                print("status: 5000")
                return HTMLResponse(
                    content=f"<tr><td colspan='7' style='color: red;'>Error: Failed to write data to the database.</td></tr>",
                    status_code=500
                )
            else:
                data_from_db = model.getProfilePage(limit, (page - 1) * limit)
                total = len(table_data)
                elapsed_time = time.time() - start_time
                print(f"Import hoàn thành trong {elapsed_time:.2f} giây")
                return JSONResponse(
                    content={
                        "total": total,
                        "page": page,
                        "limit": limit,
                        "data": data_from_db,
                        "import_time": f"{elapsed_time:.2f}s"
                    }
                )
        else:
            return HTMLResponse(
                content=f"<tr><td colspan='7' style='color: red;'>Error: Unsupported file format. Please upload an Excel file.</td></tr>",
                status_code=400
            )
    except Exception as e:
        close_session()
        hotmail_api.close()
        eoffice_api.close()
        return HTMLResponse(
            content=f"<tr><td colspan='7' style='color: red;'>Error: {str(e)}</td></tr>",
            status_code=400
        )

def paginate(data, page, limit):
    total = len(data)
    start = (page - 1) * limit
    end = start + limit
    return {
        "data": data[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

def fetch_api_data_batch(profile_ids: List[str]) -> Dict[str, Dict]:
    """Fetch data for multiple profiles in parallel using optimized APIs"""
    # Use the optimized batch methods from both APIs
    hotmail_data = hotmail_api.get_hotmail_info_batch(profile_ids)
    eoffice_data = eoffice_api.get_profile_batch(profile_ids)
    
    # Combine the results
    results = {}
    for profile_id in profile_ids:
        results[profile_id] = {
            "hotmail": hotmail_data.get(profile_id, {}),
            "eoffice": eoffice_data.get(profile_id, {})
        }
    
    return results

async def write_sync_localdb_onlinedb_optimized(data_import: List[Dict]) -> bool:
    """Optimized version with batch processing and parallel API calls"""
    try:
        # Lưu dữ liệu gốc từ file Excel vào database
        model.writeRawExcel(data_import)
        # Extract all profile IDs
        profile_ids = [str(item['ID']) for item in data_import]
        
        # Fetch all API data in parallel
        print("Đang fetch dữ liệu từ API...")
        api_data = fetch_api_data_batch(profile_ids)
        
        # Process data in batches
        batch_size = ImportConfig.BATCH_SIZE
        all_account_profiles = []
        all_browser_profiles = []
        all_fingerprint_profiles = []
        
        for i in range(0, len(data_import), batch_size):
            batch = data_import[i:i + batch_size]
            
            # Process batch
            for data_item in batch:
                profile_id = str(data_item['ID'])
                api_result = api_data.get(profile_id, {})
                
                hotmail_data = api_result.get("hotmail", {})
                data_eoffice = api_result.get("eoffice", {})
                
                # Extract data
                access_token = hotmail_data.get("access_token") if hotmail_data else None
                refresh_token = hotmail_data.get("refresh_token") if hotmail_data else None
                error = hotmail_data.get("error", "null") if hotmail_data else "null"
                def is_valid_token(token):
                    return token not in [None, '', 'null', 'None', 'NULL']
                completed = bool(is_valid_token(access_token) and is_valid_token(refresh_token))
                print(f"IMPORT PROFILE ID={profile_id} | access_token={access_token} ({type(access_token)}) | refresh_token={refresh_token} ({type(refresh_token)}) | completed={completed}")

                
                browser_id = data_eoffice.get("browser", {}).get("id") if data_eoffice else None
                fingerprint_id = data_eoffice.get("id") if data_eoffice else None
                finger_info_node = data_eoffice.get("browser", {}).get("finger_info") if data_eoffice else {}
                
                # Build profile data
                all_account_profiles.append({
                    "ID": data_item['ID'],
                    "Profile_name": data_item['Profile_name'],
                    "Password": data_item['Password'],
                    "Access_token": access_token,
                    "Refresh_token": refresh_token,
                    "error": error,
                    "Completed": 1 if completed else 0,  # Đúng key schema
                    "Browser_id": browser_id,
                    "Fingerprint_id": fingerprint_id,
                })
                
                all_browser_profiles.append({
                    "ID": browser_id,
                    "Browser_type": data_item['Browser'],
                    "Proxy_type": "HTTP",
                    "Proxy_ip": data_item['Proxy_ip'],
                    "Proxy_port": data_item['Proxy_port'],
                    "Proxy_user": data_item['Proxy_user'],
                    "Proxy_pass": data_item['Proxy_pass'],
                    "Profile_name": data_item['Profile_name'],
                })
                
                all_fingerprint_profiles.append({
                    "ID": fingerprint_id,
                    "Group1": finger_info_node.get("group1"),
                    "Group2": finger_info_node.get("group2"),
                    "Device1": finger_info_node.get("device1"),
                    "Device2": finger_info_node.get("device2"),
                    "Device3": finger_info_node.get("device3"),
                    "GPU": finger_info_node.get("DanaFP.webgl.GPU"),
                    "R6408": finger_info_node.get("DanaFP.webgl.R6408"),
                    "R35661": finger_info_node.get("DanaFP.webgl.R35661"),
                    "R36349": finger_info_node.get("DanaFP.webgl.R36349"),
                    "Random": finger_info_node.get("DanaFP.webgl.Random"),
                })
            
            print(f"Đã xử lý batch {i//batch_size + 1}/{(len(data_import) + batch_size - 1)//batch_size}")
        
        # Write to database in parallel
        print("Đang ghi vào database...")
        await asyncio.gather(
            asyncio.to_thread(browser_model.writeBrowserDB, data=all_browser_profiles),
            asyncio.to_thread(fingerprint_model.writeFingerprintDB, data=all_fingerprint_profiles),
            asyncio.to_thread(account_model.writeAccount, data=all_account_profiles)
        )
        
        print("Ghi database hoàn thành!")
        return True
        
    except Exception as e:
        print(f"Error writing to database: {e}")
        return False

# Keep the original function for backward compatibility
async def write_sync_localdb_onlinedb(data_import):
    async def process(data_item):
        id = data_item['ID']
        profile_name = data_item['Profile_name']
        password = data_item['Password']
        proxy_ip = data_item['Proxy_ip']
        proxy_port = data_item['Proxy_port']
        proxy_username = data_item['Proxy_user']
        proxy_password = data_item['Proxy_pass']
        browser_type = data_item['Browser']

        hotmail_data, data_eoffice = await asyncio.gather(
            hotmail_api.get_hotmail_info_for_id(id),
            eoffice_api.get_profile_for_id(id)
        )

        access_token = hotmail_data.get("access_token", "null") if hotmail_data else "null"
        refresh_token = hotmail_data.get("refresh_token", "null") if hotmail_data else "null"
        error = hotmail_data.get("error", "null") if hotmail_data else "null"
        completed = hotmail_data.get("Completed", "null") if hotmail_data else "null"

        browser_id = data_eoffice.get("browser", {}).get("id") if data_eoffice else None
        fingerprint_id = data_eoffice.get("id") if data_eoffice else None

        finger_info_node = data_eoffice.get("browser", {}).get("finger_info") if data_eoffice else {}

        return {
            "account": {
                "ID": id,
                "Profile_name": profile_name,
                "Password": password,
                "Access_token": access_token,
                "Refresh_token": refresh_token,
                "error": error,
                "Completed": completed,
                "Browser_id": browser_id,
                "Fingerprint_id": fingerprint_id,
            },
            "browser": {
                "ID": browser_id,
                "Browser_type": browser_type,
                "Proxy_type": "HTTP",
                "Proxy_ip": proxy_ip,
                "Proxy_port": proxy_port,
                "Proxy_user": proxy_username,
                "Proxy_pass": proxy_password,
                "Profile_name": profile_name,
            },
            "fingerprint": {
                "ID": fingerprint_id,
                "Group1": finger_info_node.get("group1"),
                "Group2": finger_info_node.get("group2"),
                "Device1": finger_info_node.get("device1"),
                "Device2": finger_info_node.get("device2"),
                "Device3": finger_info_node.get("device3"),
                "GPU": finger_info_node.get("DanaFP.webgl.GPU"),
                "R6408": finger_info_node.get("DanaFP.webgl.R6408"),
                "R35661": finger_info_node.get("DanaFP.webgl.R35661"),
                "R36349": finger_info_node.get("DanaFP.webgl.R36349"),
                "Random": finger_info_node.get("DanaFP.webgl.Random"),
            }
        }

    try:
        tasks = [process(item) for item in data_import]
        results = await asyncio.gather(*tasks)

        account_profiles = [res["account"] for res in results]
        browser_profiles = [res["browser"] for res in results]
        fingerprint_profiles = [res["fingerprint"] for res in results]

        browser_model.writeBrowserDB(data=browser_profiles)
        fingerprint_model.writeFingerprintDB(data=fingerprint_profiles)
        account_model.writeAccount(data=account_profiles)
    except Exception as e:
        print(f"Error writing to database: {e}")
        return False

    return True

def render_template(table_data, context=None):
    html_template = """
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Profile name</th>
                    <th>Browser</th>
                    <th>Proxy</th>
                    <th>Token</th>
                    <th>Completed</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="table-body">
                {% for row in table_data %}
                <tr class="{{ loop.index0 }}">
                    <td id="idProfile" class="id">{{ row["ID"] }}</td>
                    <td>{{ row["Profile name"] }}</td>
                    <td>{{ row["Browser"] }}</td>
                    <td>Http|{{ row["Proxy IP"] }}:{{ row["Proxy Port"] }}</td>
                    <td>Null</td>
                    <td>Null</td>
                    <td>
                        <div class="action-column">
                            <div class="item-button start-button disabled" data-id="{{ row['ID'] }}" onclick="start_action_event(this)">
                                <img src="/static/publish/plus.png" alt="" style="max-width:12px">
                                <span>Start</span>
                            </div>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    """
    template = Template(html_template)
    return template.render(table_data=table_data)
