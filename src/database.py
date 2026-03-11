"""
Database setup for CMMS - Based on Updated ER Diagram
"""
import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'cmms.db')
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Employee table (Entity)  
    cursor.execute('''  
        CREATE TABLE IF NOT EXISTS employee (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            employee_type VARCHAR(10) NOT NULL,
            supervisor_id INTEGER,
            FOREIGN KEY (supervisor_id) REFERENCES employee(employee_id) ON DELETE SET NULL,
            CHECK (employee_id != supervisor_id),  -- No self-supervision 
            CHECK(employee_type IN ('executive', 'manager', 'worker'))  -- Valid types of employees
        )
    ''')
    
    # Employee Contact table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_contact (
            employee_id INTEGER PRIMARY KEY,
            phone VARCHAR(20),
            email VARCHAR(50),
            emergency_contact VARCHAR(100),
            FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE
        )
    ''')
    
    # Building table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS building (
            building_id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_name VARCHAR(100) NOT NULL
        )
    ''')
    
    # Room table (Weak Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS room (
            building_id INTEGER,
            room_id INTEGER,
            room_type VARCHAR(50),
            PRIMARY KEY (building_id, room_id),
            FOREIGN KEY (building_id) REFERENCES building(building_id) ON DELETE CASCADE,
            CHECK(room_type IN ('classroom', 'office', 'laboratory', 'conference', 'storage', 'restroom'))
        )
    ''')
    
    # Outdoor Area table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outdoor_area (
            area_id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_name VARCHAR(100) NOT NULL,
            area_type VARCHAR(50),
            CHECK(area_type IN ('square', 'gate', 'path', 'parking_lot', 'garden', 'sports_field'))
        )
    ''')
    
    # Location table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_type VARCHAR(50) NOT NULL,
            building_id INTEGER NULL,
            room_building_id INTEGER NULL,
            room_id INTEGER NULL,
            outdoor_area_id INTEGER NULL,
            location_name VARCHAR(100) NOT NULL,
            CHECK(location_type IN ('building', 'room', 'outdoor_area')),
            CHECK(
                (location_type = 'building' AND building_id IS NOT NULL AND room_building_id IS NULL AND room_id IS NULL AND outdoor_area_id IS NULL) OR
                (location_type = 'room' AND building_id IS NULL AND room_building_id IS NOT NULL AND room_id IS NOT NULL AND outdoor_area_id IS NULL) OR
                (location_type = 'outdoor_area' AND building_id IS NULL AND room_building_id IS NULL AND room_id IS NULL AND outdoor_area_id IS NOT NULL)
            ),
            FOREIGN KEY (building_id) REFERENCES building(building_id) ON DELETE CASCADE,
            FOREIGN KEY (room_building_id, room_id) REFERENCES room(building_id, room_id) ON DELETE CASCADE,
            FOREIGN KEY (outdoor_area_id) REFERENCES outdoor_area(area_id) ON DELETE CASCADE
        )
    ''')
    
    # External Company table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_company (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100),
            contact_info VARCHAR(255)
        )
    ''')
    
    # Activity table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type VARCHAR(50),
            location_id INTEGER NOT NULL,
            description TEXT,
            start_date DATE,
            end_date DATE,
            status VARCHAR(20),
            manager_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES location(location_id) ON DELETE CASCADE,     
            FOREIGN KEY (manager_id) REFERENCES employee(employee_id) ON DELETE SET NULL,
            CHECK(start_date <= end_date),  -- Valid dates
            CHECK(activity_type IN ('cleaning', 'repair', 'renovation', 'weather-related', 'maintenance')),
            CHECK(status IN ('Scheduled', 'In Progress', 'Completed'))
        )
    ''')
    
    # Chemical table (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemical (
            chemical_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_name VARCHAR(100) NOT NULL,
            hazard_level INTEGER,
            CHECK(hazard_level BETWEEN 0 AND 4)
        )
    ''')
    
    # Chemical Usage table (Relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemical_usage (
            usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_id INTEGER,
            activity_id INTEGER,
            quantity_used INTEGER,
            usage_reasons TEXT,
            FOREIGN KEY (chemical_id) REFERENCES chemical(chemical_id) ON DELETE CASCADE,
            FOREIGN KEY (activity_id) REFERENCES activity(activity_id) ON DELETE CASCADE
        )
    ''')
    
    # Building Supervision table (Relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS building_supervision (
            manager_id INTEGER,
            building_id INTEGER,
            assigned_date DATE,
            PRIMARY KEY (manager_id, building_id, assigned_date),
            FOREIGN KEY (manager_id) REFERENCES employee(employee_id) ON DELETE CASCADE,
            FOREIGN KEY (building_id) REFERENCES building(building_id) ON DELETE CASCADE
        )
    ''')
    
    # Assignment table (Weak Relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignment (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            activity_id INTEGER,
            start_date DATE,
            due_date DATE,
            description TEXT,
            FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE,
            FOREIGN KEY (activity_id) REFERENCES activity(activity_id) ON DELETE CASCADE
        )
    ''')
    
    # Contract table (Weak Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contract (
            contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            activity_id INTEGER,
            contract_description TEXT,
            contract_date DATE,
            FOREIGN KEY (company_id) REFERENCES external_company(company_id) ON DELETE CASCADE,
            FOREIGN KEY (activity_id) REFERENCES activity(activity_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Updated database schema created successfully!")

if __name__ == "__main__":
    setup_database()
