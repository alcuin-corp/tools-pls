from server import Server
from pprint import pprint
import os.path as p

s = Server('localhost', 'C:/Program Files/Microsoft SQL Server/MSSQL14.MSSQLSERVER/MSSQL')

s.restore('20180123-1450-V9Talent_Recette.bak')