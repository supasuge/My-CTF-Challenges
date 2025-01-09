import os

class Config:
    SECRET_KEY = os.urandom(24)
    db = 'database.db'
    USERNAME = 'admin'
    PASSWORD = 'hidden_in_plain_sight'
    FLAG = 'GrizzCTF{wh4t_4_g1lly_s00se}'
    
    
    
    
