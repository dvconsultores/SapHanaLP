# Developer: Andrés Dominguez
# GlobalDV C.A
# Date: 2021-09-15
# @AllRightsReserved

from hdbcli import dbapi
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
import time
import inserts_thread as it
import querysHana as qh
import psycopg2
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from sqlalchemy import create_engine, text
# Load environment variables from the .env file
load_dotenv()

# VPN connection name
vpn_name = os.getenv('VPN_NAME')

# SAP HANA connection credentials
hana_host = os.getenv('HANA_HOST')
hana_port = 30241
hana_user = os.getenv('HANA_USER')
hana_password = os.getenv('HANA_PASSWORD')

# PostgreSQL connection credentials
pg_host = os.getenv('APP_HOST')
pg_port = 25060
pg_user = os.getenv('APP_USER')
pg_password = os.getenv('APP_PASSWORD')
pg_database = os.getenv('APP_DATABASE')


# Function to check if VPN is already connected
def is_vpn_connected():
    vpn_status_command = f"nmcli con show --active | grep '{vpn_name}'"
    
    process = subprocess.Popen(vpn_status_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    # If stdout contains any output, the VPN is connected
    return process.returncode == 0

# Function to connect to VPN using nmcli
def connect_vpn():
    if is_vpn_connected():
        print(f"VPN {vpn_name} is already connected.")
        return True

    print(f"Connecting to VPN: {vpn_name}...")
    vpn_command = f"nmcli con up id '{vpn_name}'"
    
    process = subprocess.Popen(vpn_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # Wait a few seconds to establish the VPN connection
    
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(f"VPN {vpn_name} connected successfully.")
        return True
    else:
        print(f"Failed to connect to VPN: {stderr.decode()}")
        return False

# Function to disconnect VPN using nmcli
def disconnect_vpn():
    print(f"Disconnecting VPN: {vpn_name}...")
    vpn_command = f"nmcli con down id '{vpn_name}'"
    
    process = subprocess.Popen(vpn_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        print(f"VPN {vpn_name} disconnected successfully.")
    else:
        print(f"Failed to disconnect VPN: {stderr.decode()}")

# Function to query SAP HANA using an open connection and cursor
def query_hana(connection, cursor, query):
    try:
        # Execute the query
        cursor.execute(query)

        # Fetch all data
        data = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Convert to pandas DataFrame
        df = pd.DataFrame(data, columns=columns)

        return df

    except dbapi.Error as e:
        print(f"An error occurred while querying: {e}")
        return None


# Main function to handle VPN connection, query HANA, disconnect VPN, and insert into PostgreSQL
def main():
    time_start = time.time()
    # Step 1: Connect to VPN and SAP HANA
    if connect_vpn():
        time.sleep(1)  # wait 1 second
        print("Performing queries")
        hana_connection = None
        hana_cursor = None
        try:
            # Establish a single SAP HANA connection
            hana_connection = dbapi.connect(
                address=hana_host,
                port=hana_port,
                user=hana_user,
                password=hana_password
            )
            hana_cursor = hana_connection.cursor()

            # Query farms data
            df_farms = query_hana(hana_connection, hana_cursor, qh.query_farms)
            # Query warehouse data
            df_warehouse = query_hana(hana_connection, hana_cursor, qh.query_warehouse)
            # Query transport data
            df_transport = query_hana(hana_connection, hana_cursor, qh.query_transport)
            # Query purchase orders data
            df_purchase_orders = query_hana(hana_connection, hana_cursor, qh.query_purchase_orders)
            # Query query_transfer_food_farms
            df_transfer_food_farms = query_hana(hana_connection, hana_cursor, qh.query_transfer_food_farms)
            # Query incubator fattering orders
            df_incubator_fattering = query_hana(hana_connection, hana_cursor, qh.query_trasnfer_incubator_fattening)
        finally:
            # Step 2: Disconnect VPN and close SAP HANA connection after all queries
            if hana_cursor:
                hana_cursor.close()
            if hana_connection:
                hana_connection.close()
            # disconnect_vpn()
    else:
        print("Failed to connect to VPN. Exiting.")
        return  # or exit the script if this is the main function

    time.sleep(1)  # wait 1 second

    # Step 3: Connect to PostgreSQL
    print("Connecting to PostgreSQL...")
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            database=pg_database,
            user=pg_user,
            password=pg_password
        )
        cursor = conn.cursor()

        # Create PostgreSQL engine using SQLAlchemy
        pg_url = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}'
        engine = create_engine(pg_url)

        print("Performing Inserts in Sequence")
       
        it.insert_farm_data(conn, cursor, df_farms) #farms
        it.insert_transport_data(conn, cursor, df_transport) # vendors
        it.insert_vendors_data(conn, cursor, df_transport)  # vendors

        time.sleep(3)  # wait for 3 seconds before inserting the next table

        print("Performing Inserts in Parallel")
        
        # Use ThreadPoolExecutor to run inserts in parallel
        with ThreadPoolExecutor(max_workers=32) as executor:
            # Submit tasks to the executor
            futures = []
            time.sleep(1)  # wait for 3 seconds before inserting the next table
            futures.append(executor.submit(it.insert_warehouse_data, engine, conn, cursor, df_warehouse))  # warehouse
            time.sleep(1)  # wait for 3 seconds before inserting the next table
            futures.append(executor.submit(it.insert_crias_ordenes_recepcion_data, engine, conn, cursor, df_purchase_orders))  # purchase orders
            time.sleep(1)  # wait for 3 seconds before inserting the next table
            futures.append(executor.submit(it.insert_transfer_food_farms_data, engine, conn, cursor, df_transfer_food_farms))  # transfer food farms
            time.sleep(1)  # wait for 3 seconds before inserting the next table
            futures.append(executor.submit(it.insert_transfer_incubator_fattering_data, engine, conn, cursor, df_incubator_fattering))  # incubator fattering
            # Process the results as they complete
            for future in as_completed(futures):
                try:
                    future.result()  # This will raise an exception if the insert operation failed
                except Exception as e:
                    print(f"An error occurred during insert operation: {e}")

    except psycopg2.OperationalError as e:
        print(f"Connection error: {e}")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        # Step 4: Close the PostgreSQL connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("PostgreSQL connection closed.")
    print(f"Execution time: {time.time() - time_start:.2f} seconds.")        

def main1():
    # Connect to VPN
    connect_vpn()
    # Your main function logic here
    # For example, connecting to Hana and performing operations

    # Simulate some work with a sleep
    time.sleep(10)

    print("Finished work")

# Run the main function
if __name__ == "__main__":
    main()

    # print("Connecting to Hana...")
    # hana_connection = None
    # hana_cursor = None
    # try:
    #     # Establish a single SAP HANA connection
    #     hana_connection = dbapi.connect(
    #         address=hana_host,
    #         port=hana_port,
    #         user=hana_user,
    #         password=hana_password
    #     )
    #     hana_cursor = hana_connection.cursor()
    #     df = query_hana(hana_connection, hana_cursor, qh.query_inventories)
    #     print(df)
    #     if df is not None:
    #         # Convertir la columna 'CANTIDAD_EN_UM_ENTRADA' a numérico
    #         df['CANTIDAD_EN_UM_ENTRADA'] = pd.to_numeric(df['CANTIDAD_EN_UM_ENTRADA'], errors='coerce')
    #         df['CANTIDAD_EN_UM_PARALELA'] = pd.to_numeric(df['CANTIDAD_EN_UM_PARALELA'], errors='coerce')
    #         df.to_excel('query_inventories.xlsx', index=False)
    # except psycopg2.OperationalError as e:
    #     print(f"Connection error: {e}")    
