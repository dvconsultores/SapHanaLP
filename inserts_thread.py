import operations

# Function to perform farm data insertion
def insert_farm_data(conn, cursor, df_farms):
    if df_farms is not None and not df_farms.empty:
        df_farms.rename(columns={'WERKS': 'id_sap', 'NAME1': 'name'}, inplace=True)
        operations.store_farm_data(conn, cursor, df_farms)
    else:
        print("No farm data to insert (either query returned None or DataFrame is empty).")

# Function to perform transport data insertion
def insert_transport_data(conn, cursor, df_transport):
    if df_transport is not None and not df_transport.empty:
        df_transport.rename(columns={'LIFNR': 'id_sap', 'NAME1': 'name'}, inplace=True)
        operations.store_transports_data(conn, cursor, df_transport)
    else:
        print("No transport data to insert (either query returned None or DataFrame is empty).")