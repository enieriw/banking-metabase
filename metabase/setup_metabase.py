import requests
import time
import os

METABASE_URL = "http://localhost:3000"

def wait_for_metabase():
    print("Waiting for Metabase to start...")
    while True:
        try:
            r = requests.get(f"{METABASE_URL}/api/health")
            if r.status_code == 200:
                print("Metabase is up!")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(5)

def setup_metabase():
    # 1. Get Setup Token
    r = requests.get(f"{METABASE_URL}/api/session/properties")
    r.raise_for_status()
    properties = r.json()
    setup_token = properties.get("setup-token")
    
    if not setup_token:
        print("Metabase is already set up!")
        # We should just login then
        return login_metabase()

    print("Running initial setup...")
    setup_payload = {
        "token": setup_token,
        "prefs": {
            "site_name": "Airflow DBT Demo",
            "site_locale": "en",
            "allow_tracking": False
        },
        "database": {
            "engine": "postgres",
            "name": "Data Warehouse",
            "details": {
                "host": "postgres-dw",
                "port": 5432,
                "dbname": "datawarehouse",
                "user": "dw_user",
                "password": "dw_pass"
            },
            "is_full_sync": True,
            "is_on_demand": False,
            "auto_run_queries": True
        },
        "user": {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@example.com",
            "password": "Password123!"
        }
    }
    
    r = requests.post(f"{METABASE_URL}/api/setup", json=setup_payload)
    r.raise_for_status()
    print("Setup completed successfully!")
    return r.json().get("id") # Session ID

def login_metabase():
    r = requests.post(f"{METABASE_URL}/api/session", json={
        "username": "admin@example.com",
        "password": "Password123!"
    })
    r.raise_for_status()
    return r.json().get("id")

def create_dashboard(session_id):
    headers = {"X-Metabase-Session": session_id}
    
    # Get the database ID
    r = requests.get(f"{METABASE_URL}/api/database", headers=headers)
    db_id = next((db["id"] for db in r.json()["data"] if db["name"] == "Data Warehouse"), None)
    
    if not db_id:
        print("Data Warehouse not found. Creating database connection...")
        db_payload = {
            "name": "Data Warehouse",
            "engine": "postgres",
            "details": {
                "host": "postgres-dw",
                "port": 5432,
                "dbname": "datawarehouse",
                "user": "dw_user",
                "password": "dw_pass"
            }
        }
        r = requests.post(f"{METABASE_URL}/api/database", json=db_payload, headers=headers)
        if r.status_code == 200:
            db_id = r.json().get("id")
            print("Database connected successfully!")
        else:
            print("Failed to connect database:", r.text)
            return

    # Trigger a sync so Metabase sees the schemas
    print("Syncing database schema...")
    requests.post(f"{METABASE_URL}/api/database/{db_id}/sync_schema", headers=headers)
    time.sleep(5)
    
    # 1. Create Question 1 (Active Items by Category)
    q1_payload = {
        "name": "Active Items by Category",
        "description": "Count of active items grouped by category",
        "dataset_query": {
            "database": db_id,
            "type": "native",
            "native": {
                "query": "SELECT category_name, COUNT(*) as active_count FROM analytics.fact_items_history WHERE is_active = true GROUP BY category_name;",
                "template-tags": {}
            }
        },
        "display": "bar",
        "visualization_settings": {}
    }
    r = requests.post(f"{METABASE_URL}/api/card", json=q1_payload, headers=headers)
    card1_id = r.json().get("id") if r.status_code == 200 else None

    # Create Question 2 (Items by Status - Pie Chart)
    q2_payload = {
        "name": "Active Items by Status",
        "description": "Distribution of item statuses",
        "dataset_query": {
            "database": db_id,
            "type": "native",
            "native": {
                "query": "SELECT status, COUNT(*) as count FROM analytics.fact_items_history WHERE is_active = true GROUP BY status;",
                "template-tags": {}
            }
        },
        "display": "pie",
        "visualization_settings": {}
    }
    r = requests.post(f"{METABASE_URL}/api/card", json=q2_payload, headers=headers)
    card2_id = r.json().get("id") if r.status_code == 200 else None

    # Create Question 3 (Average Value by Category)
    q3_payload = {
        "name": "Average Item Value by Category",
        "description": "Average value of active items",
        "dataset_query": {
            "database": db_id,
            "type": "native",
            "native": {
                "query": "SELECT category_name, AVG(value) as avg_value FROM analytics.fact_items_history WHERE is_active = true GROUP BY category_name;",
                "template-tags": {}
            }
        },
        "display": "bar",
        "visualization_settings": {}
    }
    r = requests.post(f"{METABASE_URL}/api/card", json=q3_payload, headers=headers)
    card3_id = r.json().get("id") if r.status_code == 200 else None

    # 2. Create Dashboard
    dashboard_payload = {
        "name": "Data Engineering Demo Dashboard",
        "description": "Real-time updates from dbt models"
    }
    r = requests.post(f"{METABASE_URL}/api/dashboard", json=dashboard_payload, headers=headers)
    r.raise_for_status()
    dash_id = r.json().get("id")
    print(f"Created Dashboard ID: {dash_id}")

    # 3. Add Questions to Dashboard
    dashcards = []
    
    if card1_id:
        dashcards.append({
            "id": -1, "card_id": card1_id,
            "size_x": 12, "size_y": 8, "col": 0, "row": 0, "parameter_mappings": []
        })
    if card2_id:
        dashcards.append({
            "id": -2, "card_id": card2_id,
            "size_x": 12, "size_y": 8, "col": 12, "row": 0, "parameter_mappings": []
        })
    if card3_id:
        dashcards.append({
            "id": -3, "card_id": card3_id,
            "size_x": 24, "size_y": 8, "col": 0, "row": 8, "parameter_mappings": []
        })

    dashcard_payload = {
        "dashcards": dashcards
    }
    r = requests.put(f"{METABASE_URL}/api/dashboard/{dash_id}", json=dashcard_payload, headers=headers)
    if r.status_code != 200:
        print("Failed to add question to dashboard. Reason:", r.text)
        return
    print("Added question to dashboard!")
    print(f"\n---> Dashboard is ready at: {METABASE_URL}/dashboard/{dash_id}")
    print("Login with: admin@example.com / Password123!")

if __name__ == "__main__":
    wait_for_metabase()
    try:
        session = setup_metabase()
        if session:
            create_dashboard(session)
    except Exception as e:
        print(f"An error occurred: {e}")
