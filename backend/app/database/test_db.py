from app.database.db import get_connection

try:
    with get_connection() as connection:
        result = connection.execute("SELECT version();").fetchone()

        print("DATABASE CONNECTION SUCCESSFUL!")
        print(result[0])

except Exception as error:
    print("DATABASE CONNECTION FAILED!")
    print(repr(error))