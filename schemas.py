from hdbcli import dbapi
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# SAP HANA connection credentials
host = os.getenv('HANA_HOST')
port = 30241  # You can also use os.getenv('HANA_PORT') if the port is dynamic
user = os.getenv('HANA_USER')
password = os.getenv('HANA_PASSWORD')

# Schema and tables
query = """
SELECT SCHEMA_NAME, TABLE_NAME 
FROM SYS.TABLES 
-- WHERE TABLE_NAME = 'T001L';
"""

# Initialize connection and cursor to None
connection = None
cursor = None

try:
    # Establish the connection to SAP HANA
    connection = dbapi.connect(
        address=host,
        port=port,
        user=user,
        password=password
    )

    # Create a cursor object using the connection
    cursor = connection.cursor()

    # Execute the SQL query to retrieve data from the IFLOT table
    cursor.execute(query2)

    # Fetch all results from the executed query
    sessions = cursor.fetchall()

    # Get column names for the result set (optional, depends on your cursor implementation)
    columns = [desc[0] for desc in cursor.description]

    # Convert the result set into a pandas DataFrame
    df = pd.DataFrame(sessions, columns=columns)

    # Export the DataFrame to an Excel file
    output_file = 'hana_schemas.xlsx'
    df.to_excel(output_file, index=False)  # Set index=False to avoid adding row indices

    print(f"Data has been exported to {output_file}")

except dbapi.Error as e:
    # Handle any errors that occur during the connection or query execution
    print(f"An error occurred: {e}")

finally:
    # Ensure the cursor and connection are closed, even if an error occurred
    if cursor:
        cursor.close()
    if connection:
        connection.close()
