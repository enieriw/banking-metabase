import os
import time
import random
import json
import psycopg2
from psycopg2 import OperationalError

def connect():
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.environ.get('DB_NAME', 'cdc_db'),
                user=os.environ.get('DB_USER', 'cdc_user'),
                password=os.environ.get('DB_PASS', 'cdc_pass'),
                host=os.environ.get('DB_HOST', 'postgres-source'),
                port=os.environ.get('DB_PORT', '5432')
            )
            return conn
        except OperationalError:
            print("Database not ready yet, retrying in 5 seconds...")
            time.sleep(5)

def run():
    print("Starting data generator...")
    conn = connect()
    conn.autocommit = True
    cursor = conn.cursor()
    
    statuses = ['ACTIVE', 'ACTIVE', 'ACTIVE', 'INACTIVE', 'ARCHIVED'] # Weighted towards ACTIVE

    while True:
        action = random.choices(['insert', 'update', 'delete'], weights=[0.6, 0.3, 0.1])[0]
        
        if action == 'insert':
            name = f'Item {random.randint(100, 999)}'
            value = random.randint(10, 5000)
            category_id = random.randint(1, 3)
            status = random.choice(statuses)
            metadata = json.dumps({"source": "generator", "rating": random.randint(1, 5)})
            
            cursor.execute(
                """
                INSERT INTO source_data (name, value, category_id, status, metadata) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, value, category_id, status, metadata)
            )
            print(f"Inserted {name} with value {value}, category {category_id}, status {status}")
            
        elif action == 'update':
            # update a random existing row
            cursor.execute("SELECT id FROM source_data ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                row_id = row[0]
                new_value = random.randint(10, 5000)
                new_status = random.choice(statuses)
                cursor.execute(
                    """
                    UPDATE source_data 
                    SET value = %s, status = %s
                    WHERE id = %s
                    """,
                    (new_value, new_status, row_id)
                )
                print(f"Updated row {row_id} with new value {new_value}, status {new_status}")
                
        elif action == 'delete':
            # delete a random existing row
            cursor.execute("SELECT id FROM source_data ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                row_id = row[0]
                cursor.execute("DELETE FROM source_data WHERE id = %s", (row_id,))
                print(f"Deleted row {row_id}")
        
        # wait a bit before the next operation
        time.sleep(random.randint(2, 5))

if __name__ == '__main__':
    run()
