import psycopg2
import psycopg2.extras


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

# Function to store warehouse data
def store_warehouse_data(conn, cursor, df, batch_size=500):
    # Convert the DataFrame rows into a list of tuples for easy insertion
    data = [(record[0], record[1], record[2]) for record in df.itertuples(index=False, name=None)]

    try:
        # Query for updating
        sql_update = """
            UPDATE galpones
            SET id_sap = %s,
                galpon = %s
            WHERE "granjaIdId" = %s AND id_sap = %s;
        """

        # Query for inserting
        sql_insert = """
            INSERT INTO galpones (id_sap, galpon, "granjaIdId")
            VALUES (%s, %s, %s);
        """

        # Batch the inserts/updates for performance
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            for record in batch:
                # Attempt to update first
                cursor.execute(sql_update, (record[0], record[1], record[2], record[0]))
                if cursor.rowcount == 0:
                    # If no rows were updated, insert new record
                    cursor.execute(sql_insert, (record[0], record[1], record[2]))
            conn.commit()

        print(f"Upsert applied for {len(data)} records.")

    except psycopg2.Error as e:
        print(f"Error during upsert: {e}")
        conn.rollback()


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
