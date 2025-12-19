import pyodbc

def get_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=LAPTOP-N5S9ML9B\\SQLEXPRESS;"
            "DATABASE=revenue_management_system;"
            "Trusted_Connection=yes;"
        )
        print("Database connected")
        return conn

    except pyodbc.Error as e:
        print("Database connection failed")
        print(e)
        return None