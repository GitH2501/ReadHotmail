from .model import Model
import sqlite3

class Fingerprint(Model):
    table = "fingerprint"


    def __init__(self):
        self.model = Model()

    def readFingerprintDB(self):
        return self.model.readDB(self.table)


    def writeFingerprintDB(self, data):
        self.model.writeDB(table=self.table,records=data)


    def readFingerprintForID(self, ID):
        conn = sqlite3.connect(self.model.database)
        cursor = conn.cursor()
        idProfile = int(ID)
        cursor.execute(f'SELECT * FROM {self.table} WHERE Id_profile=?',(idProfile,))
        row = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]

        row_dict = dict(zip(column_names, row))

        return row_dict
    
    def updateHotmail(self, ID, data:dict):
        check = self.model.updateDB(self.table,ID,data)