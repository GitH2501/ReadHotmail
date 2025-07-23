
from fastapi import UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
import io
from fastapi.responses import JSONResponse
from jinja2 import Template
from models.account import Account
from models.fingerprint import Fingerprint
from models.browser import Browser
from models.model import Model
from api.EofficeAPI import EofficeAPI
from api.HotmailAPI import HotmailAPI

account_model = Account()
fingerprint_model = Fingerprint()
browser_model = Browser()
eoffice_api = EofficeAPI()
model = Model()
data_profile = []
hotmail_api = HotmailAPI()

page = 1
limit = 20

async def import_profile_task(file: UploadFile = File(...)):
    try:
        model.createDB()
        content = await file.read()
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
            table_data = df.where(pd.notnull(df), None).to_dict('records')
            print(f"df {df}")
            print(f"table data {table_data}")
            # check_write_db = await write_db_local(table_data)
            try:
                check_write_db = await write_sync_localdb_onlinedb(table_data)
            except Exception as e:
                print(e)
            if not check_write_db:
                print("status: 5000")
                return HTMLResponse(
                    content=f"<tr><td colspan='7' style='color: red;'>Error: Failed to write data to the database.</td></tr>",
                    status_code=500
                )
                
            else:
                # create pagination page
                return JSONResponse(
                    content={
                        "total":len(table_data),
                        "page":page,
                        "limit":limit,
                        "data":table_data[0:limit]
                    }
                )
        else:   
            return HTMLResponse(
            content=f"<tr><td colspan='7' style='color: red;'>Error: Unsupported file format. Please upload an Excel file.</td></tr>",
            status_code=400
        )
    except Exception as e:
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

async def write_sync_localdb_onlinedb(data_import):
    '''
        Account profile will be taken excel file and database online
        Browser profile and Fingerprint will be taken eoffice database
    '''

    account_profiles = []
    fingerprint_profiles = []
    browser_profiles = []       

    
    for data_import_item in data_import:
        id = data_import_item['ID']
        hotmail_data = await hotmail_api.get_hotmail_info_for_id(id)
        data_eoffice = await eoffice_api.get_profile_for_id(id)


        if data_eoffice:
            profile_name = data_eoffice.get("username") 
            passowrd = data_eoffice.get("password")
            proxy_ip = data_eoffice.get("browser").get("proxy_ip")
            proxy_port = data_eoffice.get("browser").get("proxy_port")
            proxy_username = data_eoffice.get("browser").get("proxy_user")
            proxy_password = data_eoffice.get("browser").get("proxy_pass")
            proxy_type = data_eoffice.get("browser").get("proxy_type")
            browser_type = data_eoffice.get("browser").get("browser_type")
            browser_id = data_eoffice.get("browser").get("id")
            fingerprint_id =data_eoffice.get("id")
        else:
            return False,id
            

        if hotmail_data:
            access_token =  hotmail_data.get("access_token", "") if hotmail_data else None
            refresh_token = hotmail_data.get("refresh_token", "") if hotmail_data else None
            error = hotmail_data.get("error", "") if hotmail_data else None
            status = hotmail_data.get("status", "") if hotmail_data else None
        else:
            return False,id

        

        account_profiles.append({
            "ID": id,
            "Profile_name":profile_name,
            "Password": passowrd,
            "Access_token": access_token,
            "Refresh_token": refresh_token,
            "error": error,
            "Status": status,
            "Browser_id": browser_id,
            "Fingerprint_id": fingerprint_id,
        })
        browser_profiles.append({
            "ID": browser_id,
            "Browser_type": browser_type,
            "Proxy_type": proxy_type,
            "Proxy_ip": proxy_ip,
            "Proxy_port": proxy_port,
            "Proxy_user": proxy_username,
            "Proxy_pass": proxy_password,
            "Profile_name": profile_name,

        })


        finger_info__node = data_eoffice.get("browser").get("finger_info")
        fingerprint_profiles.append(
            {
            "ID": fingerprint_id,
            "Group1":finger_info__node.get("group1"),
            "Group2": finger_info__node.get("group2"),
            "Device1":finger_info__node.get("device1"),
            "Device2":finger_info__node.get("device2"),
            "Device3":finger_info__node.get("device3"),
            "GPU":finger_info__node.get("DanaFP.webgl.GPU"),
            "R6408":finger_info__node.get("DanaFP.webgl.R6408"),
            "R35661":finger_info__node.get("DanaFP.webgl.R35661"),
            "R36349":finger_info__node.get("DanaFP.webgl.R36349"),
            "Random":finger_info__node.get("DanaFP.webgl.Random"),
            },
        )
        


    try:
        account_model.writeAccount(data=account_profiles)
        browser_model.writeBrowserDB(data=browser_profiles)
        fingerprint_model.writeFingerprintDB(data= fingerprint_profiles)
        
    except Exception as e:
        print(f"Error writing to database: {e}")
        return False
    
    return True

def render_template(table_data,context=None):
    html_template = """
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Profile name</th>
                        <th>Browser</th>
                        <th>Proxy</th>
                        <th>Token</th>
                        <th>Status</th>
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
            
            # Render template
    template = Template(html_template)
    html_rows = template.render(table_data=table_data)

    return html_rows