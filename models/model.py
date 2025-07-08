import sqlite3
import json


class Model:

    database = 'readhotmaildb.db'
    def __init__(self):
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        
        
    def createDB(self):
        

        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fingerprint (
                ID INTEGER PRIMARY KEY,
                Group1 TEXT,
                Group2 TEXT,
                Device1 TEXT,
                Device2 TEXT,
                Device3 TEXT,
                GPU TEXT,
                R6408 TEXT,
                R35661 TEXT,
                R36349 TEXT,
                Random TEXt
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browser (
                ID INTEGER PRIMARY KEY,
                Browser_type TEXT,
                Proxy_type TEXT,
                Proxy_ip TEXT,
                Proxy_port TEXT,
                Proxy_user TEXT,
                Proxy_pass TEXT,
                Profile_name TEXT
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account (
                ID INTEGER PRIMARY KEY,
                Profile_name TEXT,
                Password TEXT,
                Access_token TEXT,
                Refresh_token TEXT,
                Error TEXT,
                Status TEXT,
                Browser_id INTEGER,
                Fingerprint_id INTEGER ,
                FOREIGN KEY (Browser_id) REFERENCES browser(ID) ON DELETE CASCADE,
                FOREIGN KEY (Fingerprint_id) REFERENCES fingerprint(ID) ON DELETE CASCADE        
            )
            ''')
        # Bảng lưu dữ liệu gốc từ file Excel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS imported_excel_raw (
                ID TEXT PRIMARY KEY,
                raw_json TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    # def writeDB(self, table, data):
    #     records = [(item['id'], item['profile_name'], item['password'], item['browser'], item['proxy_host'], 
    #                 item['proxy_port'],item['proxy_username'],item['proxy_password'],
    #                 item['access_token'], item['refresh_token'], item['error'], item['status']) for item in data]
    #     self.cursor.executemany(f'''
    #         INSERT OR REPLACE INTO {table} 
    #         (ID,Profile_name, password, Browser, Proxy_host, Proxy_port, Proxy_username, Proxy_password, Access_token, Refresh_token, Error, Status)
    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #     ''', records)
    #     self.conn.commit()
    #     self.conn.close()
    def writeDB(self, table, records):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        # PRAGMA tối ưu tốc độ import
        cursor.execute("PRAGMA synchronous = OFF;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA cache_size = 100000;")
        try:
            cursor.execute("BEGIN TRANSACTION;")
            if records:
                keys = ', '.join(records[0].keys())
                placeholders = ', '.join(['?'] * len(records[0]))
                values_list = [tuple(record.values()) for record in records]
                cursor.executemany(f'''
                    INSERT OR REPLACE INTO {table} ({keys})
                    VALUES ({placeholders})
                ''', values_list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
        
    def updateDB(self,table,id,data:dict):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        fields = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(id)
        sql = f"UPDATE {table} SET {fields} WHERE ID = ?"
        cursor.execute(sql, values)
        conn.commit()

    def readDB(self,table):
        self.cursor.execute(f'SELECT * FROM {table}')
        rows = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]

        result = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            result.append(row_dict)
        return result
            
    def disconnectDB(self):
        self.conn.close()

    def getProfileID(self, id):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()       
        cursor.execute('''
            SELECT 
                account.*, browser.*,fingerprint.*
            FROM account
            JOIN browser ON account.Browser_id = browser.ID
            JOIN fingerprint ON account.Fingerprint_id = fingerprint.ID
            WHERE account.ID = ?
        ''', (id,)
        )
        row_tuple = cursor.fetchone()
        if row_tuple is None:
            row_dict = None
        else:
            column_names = [col[0] for col in cursor.description]
            row_dict = dict(zip(column_names, row_tuple))

        print(row_dict)

        return row_dict
        # if rows:
        #     result_dict = dict(rows)
        #     print(result_dict)
        # else:
        #     result_dict = None
        
        
    def getProfilePage(self, limit, offset):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()       
        cursor.execute('''
            SELECT 
                account.ID as Profile_id,account.*, browser.ID as Browser_id, browser.*
            FROM account
            JOIN browser ON account.Browser_id = browser.ID
            LIMIT ? OFFSET ?
        ''', (limit, offset)
        )

        rows = cursor.fetchall()
        


        column_names = [desc[0] for desc in cursor.description]
        print(column_names)
        result = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            result.append(row_dict)

        return result

    def writeRawExcel(self, data: list):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        # PRAGMA tối ưu tốc độ import
        cursor.execute("PRAGMA synchronous = OFF;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA cache_size = 100000;")
        try:
            cursor.execute("BEGIN TRANSACTION;")
            records = [(str(row.get('ID')), json.dumps(row, ensure_ascii=False)) for row in data]
            cursor.executemany('''
                INSERT OR REPLACE INTO imported_excel_raw (ID, raw_json)
                VALUES (?, ?)
            ''', records)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()