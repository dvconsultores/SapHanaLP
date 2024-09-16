import psycopg2
import psycopg2.extras
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# Function to store farm data with an UPSERT operation, using execute_values for bulk inserts
def store_farm_data(conn, cursor, df_farms, batch_size=500):
    # Convert the DataFrame rows into a list of tuples for easy insertion
    data = list(df_farms.itertuples(index=False, name=None))

    try:
        # Insert data with ON CONFLICT (UPSERT) using execute_values for speed
        sql = """
            INSERT INTO granjas (id_sap, name)
            VALUES %s
            ON CONFLICT (id_sap) DO UPDATE
            SET name = EXCLUDED.name;
        """

        # Batch the inserts for performance
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            psycopg2.extras.execute_values(
                cursor, sql, batch, template=None, page_size=batch_size
            )
            conn.commit()  # Commit after each batch

        print(f"UPSERT applied for {len(data)} records.")

    except psycopg2.Error as e:
        print(f"Error during UPSERT: {e}")
        conn.rollback()


# Function to store purchase orders crias
def store_warehouse_data(conn, cursor, df, batch_size=500, max_workers=8):
    # Convert the DataFrame rows into a list of tuples for easy insertion
    data = [(record[0], record[1], record[2]) for record in df.itertuples(index=False, name=None)]  # Access fields by index    
    
    try:
        # Prepare the list of ids for the query and avoid executing empty queries
        id_sap_list = df['id_sap'].tolist()
        if not id_sap_list:  # If the list is empty, skip the query
            print("No id_sap to process, skipping database operations.")
            return

        # Fetch existing id_sap from the database to determine which records to update or insert
        cursor.execute("SELECT id_sap FROM galpones WHERE id_sap IN %s", (tuple(id_sap_list),))
        existing_ids = set([row[0] for row in cursor.fetchall()])  # Use fetchall() to get the results

        update_data = []
        insert_data = []

        # Separate records into update and insert based on existing ids
        for record in data:
            if record[0] in existing_ids:
                update_data.append(record)  # Existing records will be updated
            else:
                insert_data.append(record)  # New records will be inserted

        # Check if there is any data to update or insert
        if not update_data and not insert_data:
            print("No data to update or insert.")
            return

        # Function to perform batch update
        def batch_update(batch):
            sql_update = """
                UPDATE galpones
                SET galpon = %s, "granjaIdId" = %s
                WHERE id_sap = %s;
            """
            update_records = [(r[1], r[2], r[0]) for r in batch]
            psycopg2.extras.execute_batch(cursor, sql_update, update_records)
            conn.commit()

        # Function to perform batch insert
        def batch_insert(batch):
            sql_insert = """
                INSERT INTO galpones (id_sap, galpon, "granjaIdId")
                VALUES (%s, %s, %s);
            """
            if not batch:  # Check if batch is empty before attempting to insert
                print("No data to insert")
                return
            psycopg2.extras.execute_batch(cursor, sql_insert, batch)
            conn.commit()

        # Create a ThreadPoolExecutor to process batches in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # Submit update tasks to the executor
            if update_data:
                for i in range(0, len(update_data), batch_size):
                    batch = update_data[i:i + batch_size]
                    futures.append(executor.submit(batch_update, batch))

            # Submit insert tasks to the executor
            if insert_data:
                for i in range(0, len(insert_data), batch_size):
                    batch = insert_data[i:i + batch_size]
                    futures.append(executor.submit(batch_insert, batch))

            # Wait for all tasks to complete
            for future in as_completed(futures):
                future.result()  # If any exception occurs in the thread, it will be raised here

        print(f"Upsert applied for {len(data)} records.")

    except psycopg2.Error as e:
        print(f"Error during upsert: {e}")
        print(traceback.format_exc())  # Print full traceback for more details
        conn.rollback()
    finally:
        # No need to return connection to pool since we're directly using the passed `conn`
        pass

# Function to store transports
def store_transports_data(conn, cursor, df_farms, batch_size=500):
    # Convert the DataFrame rows into a list of tuples for easy insertion
    data = list(df_farms.itertuples(index=False, name=None))

    try:
        # Insert data with ON CONFLICT (UPSERT) using execute_values for speed
        sql = """
            INSERT INTO transportes (id_sap, name)
            VALUES %s
            ON CONFLICT (id_sap) DO UPDATE
            SET name = EXCLUDED.name;
        """

        # Batch the inserts for performance
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            psycopg2.extras.execute_values(
                cursor, sql, batch, template=None, page_size=batch_size
            )
            conn.commit()  # Commit after each batch

        print(f"UPSERT applied for {len(data)} records.")

    except psycopg2.Error as e:
        print(f"Error during UPSERT: {e}")
        conn.rollback()

# Function to store vendors
def store_vendors_data(conn, cursor, df_vendors, batch_size=500):
    # Convert the DataFrame rows into a list of tuples for easy insertion
    data = list(df_vendors.itertuples(index=False, name=None))

    try:
        # Insert data with ON CONFLICT (UPSERT) using execute_values for speed
        sql = """
            INSERT INTO proveedores (id_sap, name)
            VALUES %s
            ON CONFLICT (id_sap) DO UPDATE
            SET name = EXCLUDED.name;
        """

        # Batch the inserts for performance
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            psycopg2.extras.execute_values(
                cursor, sql, batch, template=None, page_size=batch_size
            )
            conn.commit()  # Commit after each batch

        print(f"UPSERT applied for {len(data)} records.")

    except psycopg2.Error as e:
        print(f"Error during UPSERT: {e}")
        conn.rollback()        

# Function to store purchase orders crias
def store_crias_ordenes_recepcion(conn, cursor, df, batch_size=500, max_workers=8):
    # Convert the DataFrame rows into a list of tuples for easy insertion
    data = [(record[0], record[1], int(record[2] or 0), int(record[3] or 0),
            record[4], record[5]) 
            for record in df.itertuples(index=False, name=None)]  # Access fields by index    

    try:
        # Prepare the list of ids for the query and avoid executing empty queries
        id_sap_list = df['id_sap'].tolist()
        if not id_sap_list:  # If the list is empty, skip the query
            print("No id_sap to process, skipping database operations.")
            return

        # Fetch existing id_sap from the database to determine which records to update or insert
        cursor.execute("SELECT id_sap FROM crias_ordenes_recepcion WHERE id_sap IN %s", (tuple(id_sap_list),))
        existing_ids = set([row[0] for row in cursor.fetchall()])  # Use fetchall() to get the results

        update_data = []
        insert_data = []

        # Separate records into update and insert based on existing ids
        for record in data:
            if record[1] in existing_ids:
                update_data.append(record)  # Existing records will be updated
            else:
                insert_data.append(record)  # New records will be inserted

        # Check if there is any data to update or insert
        if not update_data and not insert_data:
            print("No data to update or insert.")
            return

        # Function to perform batch update
        def batch_update(batch):
            sql_update = """
                UPDATE crias_ordenes_recepcion
                SET cant_hembras = %s,
                    cant_machos = %s,
                    "proveedorIdId" = %s,
                    "granjaIdId" = %s,
                    status = 'ACTIVO',
                    creation_date = now()
                WHERE id_sap = %s;
            """
            update_records = [(r[2], r[3], r[4], r[5], r[1]) for r in batch]
            psycopg2.extras.execute_batch(cursor, sql_update, update_records)
            conn.commit()

        # Function to perform batch insert
        def batch_insert(batch):
            sql_insert = """
                INSERT INTO crias_ordenes_recepcion (orden_compra, id_sap, cant_hembras, cant_machos, "proveedorIdId", "granjaIdId", status, creation_date)
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO', now());
            """
            if not batch:  # Check if batch is empty before attempting to insert
                print("No data to insert")
                return
            psycopg2.extras.execute_batch(cursor, sql_insert, batch)
            conn.commit()

        # Create a ThreadPoolExecutor to process batches in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # Submit update tasks to the executor
            if update_data:
                for i in range(0, len(update_data), batch_size):
                    batch = update_data[i:i + batch_size]
                    futures.append(executor.submit(batch_update, batch))

            # Submit insert tasks to the executor
            if insert_data:
                for i in range(0, len(insert_data), batch_size):
                    batch = insert_data[i:i + batch_size]
                    futures.append(executor.submit(batch_insert, batch))

            # Wait for all tasks to complete
            for future in as_completed(futures):
                future.result()  # If any exception occurs in the thread, it will be raised here

        print(f"Upsert applied for {len(data)} records.")

    except psycopg2.Error as e:
        print(f"Error during upsert: {e}")
        print(traceback.format_exc())  # Print full traceback for more details
        conn.rollback()
    finally:
        # No need to return connection to pool since we're directly using the passed `conn`
        pass