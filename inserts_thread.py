# Developer: Andrés Dominguez
# GlobalDV C.A
# Date: 2021-09-15
# @AllRightsReserved

import operations
import time
import querysHana as qh
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2 import sql, OperationalError, DatabaseError, ProgrammingError
import pandas as pd

# Function to query POSTGRES using an open connection and cursor
def query_postgres(connection, cursor, query):
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

    except (OperationalError, DatabaseError, ProgrammingError) as e:
        print(f"An error occurred while querying: {e}")
        return None

# Function to perform farm data insertion
def insert_farm_data(conn, cursor, df_farms):
    if df_farms is not None and not df_farms.empty:
        df_farms.rename(columns={'WERKS': 'id_sap', 'NAME1': 'name'}, inplace=True)
        operations.store_farm_data(conn, cursor, df_farms)
    else:
        print("No farm data to insert (either query returned None or DataFrame is empty).")

# Function to perform warehouse data insertion
def insert_warehouse_data(engine, conn, cursor, df_warehouse):
    if df_warehouse is not None and not df_warehouse.empty:
        df_warehouse.rename(columns={'WERKS': 'id_sap', 'NAME1': 'name'}, inplace=True)
        df_warehouse.to_sql('temp_warehouse', engine, if_exists='replace', index=False)
        print("Temporary table warehouse created")
        time.sleep(2)  # wait for two seconds before reading the temp table
        
        # Query from the temporary warehouse table
        df_warehouse_temp = query_postgres(conn, cursor, qh.query_warehouse_temp)
        print("Reading from temp...")
        operations.store_warehouse_data(conn, cursor, df_warehouse_temp)
    else:
        print("No farm data to insert (either query returned None or DataFrame is empty).")

# Function to perform warehouse data insertion
def insert_crias_ordenes_recepcion_data(engine, conn, cursor, df_crias_ordenes_recepcion):
    if df_crias_ordenes_recepcion is not None and not df_crias_ordenes_recepcion.empty:
        df_crias_ordenes_recepcion.to_sql('temp_crias_ordenes_recepcion', engine, if_exists='replace', index=False)
        print("Temporary table crias_ordenes_recepcion created")
        time.sleep(3)  # wait for 3 seconds before reading the temp table
        
        # Query from the temporary warehouse table
        df_crias_ordenes_recepcion_temp = query_postgres(conn, cursor, qh.query_purchase_orders_temp)
        print(df_crias_ordenes_recepcion_temp)
        print("Reading from temp_crias_ordenes_recepcion...")

        operations.store_crias_ordenes_recepcion(conn, cursor, df_crias_ordenes_recepcion_temp)
    else:
        print("No farm data to insert (either query returned None or DataFrame is empty).")        
       

# Function to perform transport data insertion
def insert_transport_data(conn, cursor, df_transport):
    if df_transport is not None and not df_transport.empty:
        df_transport.rename(columns={'LIFNR': 'id_sap', 'NAME1': 'name'}, inplace=True)
        operations.store_transports_data(conn, cursor, df_transport)
    else:
        print("No transport data to insert (either query returned None or DataFrame is empty).")

# Function to perform vendors data insertion
def insert_vendors_data(conn, cursor, df_vendors):
    if df_vendors is not None and not df_vendors.empty:
        df_vendors.rename(columns={'LIFNR': 'id_sap', 'NAME1': 'name'}, inplace=True)
        operations.store_vendors_data(conn, cursor, df_vendors)
    else:
        print("No vendors data to insert (either query returned None or DataFrame is empty).")

# Function to perform trasfer food to farm data insertion
def insert_transfer_food_farms_data(engine, conn, cursor, df_transfer_food_farms):
    if df_transfer_food_farms is not None and not df_transfer_food_farms.empty:
        df_transfer_food_farms.to_sql('temp_transf_alimento_granja', engine, if_exists='replace', index=False)
        print("Temporary table temp_transf_alimento_granja created")
        time.sleep(3)  # wait for 3 seconds before reading the temp table
        
        # Query from the temporary food transfer
        df_transfer_food_farms_temp = query_postgres(conn, cursor, qh.query_transfer_food_temp)
        print("Reading from temp_transf_alimento_granja...")

        operations.store_transferencias_alimento(conn, cursor, df_transfer_food_farms_temp)
    else:
        print("No transfer food data to insert (either query returned None or DataFrame is empty).")         