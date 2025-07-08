from .model import Model
import sqlite3


class Browser(Model):
    table = "browser"


    def __init__(self):
        self.model = Model()


    def readBrowserDB(self):
        return self.model.readDB(self.table)


    def writeBrowserDB(self, data):
        self.model.writeDB(table=self.table,records=data)


    def readBrowserForID(self, ID):
        conn = sqlite3.connect(self.model.database)
        cursor = conn.cursor()
        idProfile = int(ID)
        cursor.execute(f'SELECT * FROM {self.table} WHERE Id_profile=?',(idProfile,))
        row = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]

        row_dict = dict(zip(column_names, row))

        return row_dict

    def updateBrowser(self, ID, data:dict):
        check = self.model.updateDB(self.table,ID,data)