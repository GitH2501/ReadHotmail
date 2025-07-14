from .model import Model
import sqlite3

class Account(Model):
    table = 'account'
    def __init__(self):
        self.model = Model()
        self.model.__init__()
        self.cursor = self.model.cursor

    def readAccount(self):
        # return self.model.readDB(self.table)
        conn = sqlite3.connect(self.model.database)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table}")
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return data

    def writeAccount(self, data):
        self.model.writeDB(table=self.table,records=data)


    def readAccountForID(self, ID):
        conn = sqlite3.connect(self.model.database)
        cursor = conn.cursor()
        idProfile = int(ID)
        cursor.execute(f'SELECT * FROM {self.table} WHERE ID=?',(idProfile,))
        row = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]

        row_dict = dict(zip(column_names, row))

        return row_dict
    def readAccountForMultiID(self, ids):
        conn = sqlite3.connect(self.model.database)
        cursor = conn.cursor()
        placeholders = ','.join(['?' for _ in ids])
        cursor.execute(f'SELECT ID, Access_token, Refresh_token, Completed FROM {self.table} WHERE ID IN ({placeholders})', ids)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            row_dict = {
                'ID': row[0],
                'Access_token': row[1],
                'Refresh_token': row[2],
                # 'completed': row[3] == 1
                'completed': int(row[3]) == 1
            }
            result.append(row_dict)
        conn.close()
        return result
    # def readAccountForMultiID(self, ids):
    #     #  conn = sqlite3.connect(self.model.database)
    #     # cursor = conn.cursor()
    #     # id_array = ids
    #     # cursor.execute(f'SELECT * FROM {self.table} WHERE ID IN (?,?)',(id1,id2,id3,))
    #     # row = cursor.fetchall()
    #     # column_names = [desc[0] for desc in cursor.description]

    #     # row_dict = dict(zip(column_names, row))

    #     # return row_dict
    #     conn = sqlite3.connect(self.model.database)
    #     cursor = conn.cursor()
        
    #     # Tạo placeholders cho tất cả ID trong mảng
    #     placeholders = ','.join(['?' for _ in ids])
        
    #     # Chỉ select ID và Access_token
    #     cursor.execute(f'SELECT ID, Access_token FROM {self.table} WHERE ID IN ({placeholders})', ids)
    #     rows = cursor.fetchall()
        
    #     # Chuyển đổi kết quả thành list các dictionary
    #     result = []
    #     for row in rows:
    #         row_dict = {
    #             'ID': row[0],
    #             'Access_token': row[1]
    #         }
    #         result.append(row_dict)
        
    #     conn.close()
    #     return result
    def updateAccount(self, ID, data:dict):
        check = self.model.updateDB(table=self.table,ID=ID,data=data)