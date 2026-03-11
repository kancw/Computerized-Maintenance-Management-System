"""
Comprehensive test suite for Campus Maintenance Management System (CMMS)
Tests all database operations, CRUD functions, and business logic
"""
import pytest
import sqlite3
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import setup_database, get_connection
import app


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database"""
    db_path = tmp_path / "test_cmms.db"
    
    # Patch the database path
    original_get_connection = app.get_connection
    
    def mock_get_connection():
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    app.get_connection = mock_get_connection
    
    # Setup database
    setup_database_temp(str(db_path))
    
    yield str(db_path)
    
    # Cleanup
    app.get_connection = original_get_connection
    if db_path.exists():
        db_path.unlink()


def setup_database_temp(db_path):
    """Setup test database with schema"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Employee table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            employee_type VARCHAR(10) NOT NULL,
            supervisor_id INTEGER,
            FOREIGN KEY (supervisor_id) REFERENCES employee(employee_id) ON DELETE SET NULL,
            CHECK (employee_id != supervisor_id),
            CHECK(employee_type IN ('executive', 'manager', 'worker'))
        )
    ''')
    
    # Employee Contact table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_contact (
            employee_id INTEGER PRIMARY KEY,
            phone VARCHAR(20),
            email VARCHAR(50),
            emergency_contact VARCHAR(100),
            FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE
        )
    ''')
    
    # Building table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS building (
            building_id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_name VARCHAR(100) NOT NULL
        )
    ''')
    
    # Room table
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
    
    # Outdoor Area table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outdoor_area (
            area_id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_name VARCHAR(100) NOT NULL,
            area_type VARCHAR(50),
            CHECK(area_type IN ('square', 'gate', 'path', 'parking_lot', 'garden', 'sports_field'))
        )
    ''')
    
    # Location table
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
    
    # External Company table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_company (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100),
            contact_info VARCHAR(255)
        )
    ''')
    
    # Activity table
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
            CHECK(start_date <= end_date),
            CHECK(activity_type IN ('cleaning', 'repair', 'renovation', 'weather-related', 'maintenance')),
            CHECK(status IN ('Scheduled', 'In Progress', 'Completed'))
        )
    ''')
    
    # Chemical table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemical (
            chemical_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_name VARCHAR(100) NOT NULL,
            hazard_level INTEGER,
            CHECK(hazard_level BETWEEN 0 AND 4)
        )
    ''')
    
    # Chemical Usage table
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
    
    # Building Supervision table
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
    
    # Assignment table
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
    
    # Contract table
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


class TestDatabaseSetup:
    """Test database setup and connection functions"""
    
    def test_database_connection(self, test_db):
        """Test that database connection works"""
        conn = app.get_connection()
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert len(tables) > 0
        conn.close()
    
    def test_foreign_keys_enabled(self, test_db):
        """Test that foreign key constraints are enabled"""
        conn = app.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1
        conn.close()
    
    def test_all_tables_created(self, test_db):
        """Test that all required tables are created"""
        conn = app.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        required_tables = [
            'employee', 'employee_contact', 'building', 'room', 'outdoor_area',
            'location', 'external_company', 'activity', 'chemical', 
            'chemical_usage', 'building_supervision', 'assignment', 'contract'
        ]
        
        for table in required_tables:
            assert table in tables
        
        conn.close()


class TestEmployeeOperations:
    """Test employee CRUD operations"""
    
    def test_add_employee(self, test_db):
        """Test adding an employee"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("John Doe", "manager", None)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM employee WHERE name = 'John Doe'")
        employee = cursor.fetchone()
        
        assert employee is not None
        assert employee[1] == "John Doe"
        assert employee[2] == "manager"
        conn.close()
    
    def test_add_employee_with_contact(self, test_db):
        """Test adding employee with contact information"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Jane Smith", "worker", None)
        )
        emp_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO employee_contact (employee_id, phone, email, emergency_contact) VALUES (?, ?, ?, ?)",
            (emp_id, "123-456-7890", "jane@example.com", "Emergency: 911")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM employee_contact WHERE employee_id = ?", (emp_id,))
        contact = cursor.fetchone()
        
        assert contact is not None
        assert contact[1] == "123-456-7890"
        assert contact[2] == "jane@example.com"
        conn.close()
    
    def test_employee_type_constraint(self, test_db):
        """Test that invalid employee types are rejected"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
                ("Invalid Employee", "invalid_type", None)
            )
            conn.commit()
        
        conn.close()
    
    def test_supervisor_hierarchy(self, test_db):
        """Test supervisor-subordinate relationship"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Add supervisor
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Manager One", "manager", None)
        )
        manager_id = cursor.lastrowid
        
        # Add subordinate
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Worker One", "worker", manager_id)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM employee WHERE supervisor_id = ?", (manager_id,))
        subordinate = cursor.fetchone()
        
        assert subordinate is not None
        assert subordinate[3] == manager_id
        conn.close()
    
    def test_delete_employee_cascade(self, test_db):
        """Test that deleting employee cascades to contact"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Temp Employee", "worker", None)
        )
        emp_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO employee_contact (employee_id, phone, email, emergency_contact) VALUES (?, ?, ?, ?)",
            (emp_id, "555-1234", "temp@example.com", "Emergency")
        )
        conn.commit()
        
        # Delete employee
        cursor.execute("DELETE FROM employee WHERE employee_id = ?", (emp_id,))
        conn.commit()
        
        # Check contact is also deleted
        cursor.execute("SELECT * FROM employee_contact WHERE employee_id = ?", (emp_id,))
        contact = cursor.fetchone()
        
        assert contact is None
        conn.close()


class TestBuildingOperations:
    """Test building and room CRUD operations"""
    
    def test_add_building(self, test_db):
        """Test adding a building"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Academic Building A",))
        building_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM building WHERE building_id = ?", (building_id,))
        building = cursor.fetchone()
        
        assert building is not None
        assert building[1] == "Academic Building A"
        conn.close()
    
    def test_add_room(self, test_db):
        """Test adding a room to a building"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Add building first
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Science Complex",))
        building_id = cursor.lastrowid
        
        # Add room
        cursor.execute(
            "INSERT INTO room (building_id, room_id, room_type) VALUES (?, ?, ?)",
            (building_id, 101, "laboratory")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM room WHERE building_id = ? AND room_id = ?", (building_id, 101))
        room = cursor.fetchone()
        
        assert room is not None
        assert room[2] == "laboratory"
        conn.close()
    
    def test_room_type_constraint(self, test_db):
        """Test that invalid room types are rejected"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO room (building_id, room_id, room_type) VALUES (?, ?, ?)",
                (building_id, 102, "invalid_type")
            )
            conn.commit()
        
        conn.close()
    
    def test_delete_building_cascade(self, test_db):
        """Test that deleting building cascades to rooms"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Temp Building",))
        building_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO room (building_id, room_id, room_type) VALUES (?, ?, ?)",
            (building_id, 201, "office")
        )
        conn.commit()
        
        # Delete building
        cursor.execute("DELETE FROM building WHERE building_id = ?", (building_id,))
        conn.commit()
        
        # Check room is also deleted
        cursor.execute("SELECT * FROM room WHERE building_id = ?", (building_id,))
        room = cursor.fetchone()
        
        assert room is None
        conn.close()


class TestLocationOperations:
    """Test location CRUD operations"""
    
    def test_add_building_location(self, test_db):
        """Test adding a building location"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Library",))
        building_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Library")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM location WHERE building_id = ?", (building_id,))
        location = cursor.fetchone()
        
        assert location is not None
        assert location[1] == "building"
        conn.close()
    
    def test_add_outdoor_area_location(self, test_db):
        """Test adding an outdoor area location"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO outdoor_area (area_name, area_type) VALUES (?, ?)", ("Main Plaza", "square"))
        area_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO location (location_type, outdoor_area_id, location_name) VALUES (?, ?, ?)",
            ("outdoor_area", area_id, "Main Plaza")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM location WHERE outdoor_area_id = ?", (area_id,))
        location = cursor.fetchone()
        
        assert location is not None
        assert location[1] == "outdoor_area"
        conn.close()


class TestActivityOperations:
    """Test activity CRUD operations"""
    
    def test_add_activity(self, test_db):
        """Test adding an activity"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Setup location first
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Test Building")
        )
        location_id = cursor.lastrowid
        
        # Add activity
        cursor.execute(
            """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("cleaning", location_id, "Daily cleaning", "2025-01-01", "2025-01-01", "Scheduled", None)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM activity WHERE location_id = ?", (location_id,))
        activity = cursor.fetchone()
        
        assert activity is not None
        assert activity[1] == "cleaning"
        assert activity[6] == "Scheduled"
        conn.close()
    
    def test_activity_date_constraint(self, test_db):
        """Test that end_date must be >= start_date"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Test Building")
        )
        location_id = cursor.lastrowid
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("cleaning", location_id, "Invalid dates", "2025-01-10", "2025-01-01", "Scheduled", None)
            )
            conn.commit()
        
        conn.close()
    
    def test_activity_type_constraint(self, test_db):
        """Test that only valid activity types are accepted"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Test Building")
        )
        location_id = cursor.lastrowid
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("invalid_type", location_id, "Invalid", "2025-01-01", "2025-01-01", "Scheduled", None)
            )
            conn.commit()
        
        conn.close()


class TestChemicalOperations:
    """Test chemical and chemical usage operations"""
    
    def test_add_chemical(self, test_db):
        """Test adding a chemical"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO chemical (chemical_name, hazard_level) VALUES (?, ?)",
            ("Bleach", 2)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM chemical WHERE chemical_name = 'Bleach'")
        chemical = cursor.fetchone()
        
        assert chemical is not None
        assert chemical[2] == 2
        conn.close()
    
    def test_chemical_hazard_constraint(self, test_db):
        """Test that hazard level must be between 0 and 4"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO chemical (chemical_name, hazard_level) VALUES (?, ?)",
                ("Invalid Chemical", 5)
            )
            conn.commit()
        
        conn.close()
    
    def test_chemical_usage(self, test_db):
        """Test recording chemical usage in activities"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Setup chemical
        cursor.execute("INSERT INTO chemical (chemical_name, hazard_level) VALUES (?, ?)", ("Cleaner", 1))
        chemical_id = cursor.lastrowid
        
        # Setup activity
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Test Building")
        )
        location_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("cleaning", location_id, "Cleaning", "2025-01-01", "2025-01-01", "Scheduled", None)
        )
        activity_id = cursor.lastrowid
        
        # Add chemical usage
        cursor.execute(
            """INSERT INTO chemical_usage (chemical_id, activity_id, quantity_used, usage_reasons)
               VALUES (?, ?, ?, ?)""",
            (chemical_id, activity_id, 5, "Floor cleaning")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM chemical_usage WHERE chemical_id = ? AND activity_id = ?", 
                      (chemical_id, activity_id))
        usage = cursor.fetchone()
        
        assert usage is not None
        assert usage[3] == 5
        conn.close()


class TestAssignmentOperations:
    """Test assignment operations"""
    
    def test_add_assignment(self, test_db):
        """Test adding an assignment"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Setup employee
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Worker", "worker", None)
        )
        employee_id = cursor.lastrowid
        
        # Setup activity
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Test Building")
        )
        location_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("cleaning", location_id, "Cleaning", "2025-01-01", "2025-01-01", "Scheduled", None)
        )
        activity_id = cursor.lastrowid
        
        # Add assignment
        cursor.execute(
            """INSERT INTO assignment (employee_id, activity_id, start_date, due_date, description)
               VALUES (?, ?, ?, ?, ?)""",
            (employee_id, activity_id, "2025-01-01", "2025-01-01", "Clean the building")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM assignment WHERE employee_id = ?", (employee_id,))
        assignment = cursor.fetchone()
        
        assert assignment is not None
        assert assignment[1] == employee_id
        assert assignment[2] == activity_id
        conn.close()


class TestContractOperations:
    """Test contract operations with external companies"""
    
    def test_add_contract(self, test_db):
        """Test adding a contract"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Setup external company
        cursor.execute(
            "INSERT INTO external_company (company_name, specialization, contact_info) VALUES (?, ?, ?)",
            ("CleanCo", "Cleaning", "contact@cleanco.com")
        )
        company_id = cursor.lastrowid
        
        # Setup activity
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Test Building",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Test Building")
        )
        location_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("cleaning", location_id, "Cleaning", "2025-01-01", "2025-01-01", "Scheduled", None)
        )
        activity_id = cursor.lastrowid
        
        # Add contract
        cursor.execute(
            """INSERT INTO contract (company_id, activity_id, contract_description, contract_date)
               VALUES (?, ?, ?, ?)""",
            (company_id, activity_id, "Cleaning service contract", "2025-01-01")
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM contract WHERE company_id = ?", (company_id,))
        contract = cursor.fetchone()
        
        assert contract is not None
        assert contract[1] == company_id
        conn.close()


class TestHelperFunctions:
    """Test helper functions from app.py"""
    
    @patch('builtins.input', return_value='test input')
    def test_get_input_normal(self, mock_input):
        """Test get_input with normal input"""
        result = app.get_input("Enter something: ")
        assert result == 'test input'
    
    @patch('builtins.input', return_value='menu')
    def test_get_input_menu(self, mock_input):
        """Test get_input with 'menu' keyword"""
        result = app.get_input("Enter something: ")
        assert result is None
    
    @patch('builtins.input', return_value='MENU')
    def test_get_input_menu_case_insensitive(self, mock_input):
        """Test get_input with 'MENU' (case insensitive)"""
        result = app.get_input("Enter something: ")
        assert result is None
    
    @patch('builtins.input', side_effect=['confirm'])
    def test_strong_confirm_confirmed(self, mock_input):
        """Test strong_confirm when user types 'confirm'"""
        result = app.strong_confirm("This is a warning")
        assert result is True
    
    @patch('builtins.input', side_effect=['cancel'])
    def test_strong_confirm_cancelled(self, mock_input):
        """Test strong_confirm when user types something else"""
        result = app.strong_confirm("This is a warning")
        assert result is False
    
    @patch('app.get_input', return_value=None)
    def test_strong_confirm_menu(self, mock_get_input):
        """Test strong_confirm when user types 'menu'"""
        result = app.strong_confirm("This is a warning")
        assert result is False


class TestComplexScenarios:
    """Test complex scenarios involving multiple operations"""
    
    def test_full_employee_workflow(self, test_db):
        """Test complete employee workflow: add, update, query, delete"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Add employee
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Test Worker", "worker", None)
        )
        emp_id = cursor.lastrowid
        
        # Add contact
        cursor.execute(
            "INSERT INTO employee_contact (employee_id, phone, email, emergency_contact) VALUES (?, ?, ?, ?)",
            (emp_id, "555-0000", "test@test.com", "911")
        )
        conn.commit()
        
        # Update employee
        cursor.execute(
            "UPDATE employee SET name = ? WHERE employee_id = ?",
            ("Updated Worker", emp_id)
        )
        conn.commit()
        
        # Query
        cursor.execute("SELECT name FROM employee WHERE employee_id = ?", (emp_id,))
        result = cursor.fetchone()
        assert result[0] == "Updated Worker"
        
        # Delete
        cursor.execute("DELETE FROM employee WHERE employee_id = ?", (emp_id,))
        conn.commit()
        
        # Verify deletion
        cursor.execute("SELECT * FROM employee WHERE employee_id = ?", (emp_id,))
        result = cursor.fetchone()
        assert result is None
        
        conn.close()
    
    def test_activity_with_assignments_and_chemicals(self, test_db):
        """Test activity with multiple assignments and chemical usage"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # Setup
        cursor.execute("INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)", 
                      ("Worker1", "worker", None))
        emp1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)", 
                      ("Worker2", "worker", None))
        emp2_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO chemical (chemical_name, hazard_level) VALUES (?, ?)", ("Chemical A", 1))
        chem_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO building (building_name) VALUES (?)", ("Building A",))
        building_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO location (location_type, building_id, location_name) VALUES (?, ?, ?)",
            ("building", building_id, "Building A")
        )
        location_id = cursor.lastrowid
        
        cursor.execute(
            """INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("cleaning", location_id, "Deep clean", "2025-01-01", "2025-01-02", "In Progress", None)
        )
        activity_id = cursor.lastrowid
        
        # Add assignments
        cursor.execute(
            """INSERT INTO assignment (employee_id, activity_id, start_date, due_date, description)
               VALUES (?, ?, ?, ?, ?)""",
            (emp1_id, activity_id, "2025-01-01", "2025-01-02", "Clean floors")
        )
        
        cursor.execute(
            """INSERT INTO assignment (employee_id, activity_id, start_date, due_date, description)
               VALUES (?, ?, ?, ?, ?)""",
            (emp2_id, activity_id, "2025-01-01", "2025-01-02", "Clean windows")
        )
        
        # Add chemical usage
        cursor.execute(
            """INSERT INTO chemical_usage (chemical_id, activity_id, quantity_used, usage_reasons)
               VALUES (?, ?, ?, ?)""",
            (chem_id, activity_id, 10, "General cleaning")
        )
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM assignment WHERE activity_id = ?", (activity_id,))
        assert cursor.fetchone()[0] == 2
        
        cursor.execute("SELECT COUNT(*) FROM chemical_usage WHERE activity_id = ?", (activity_id,))
        assert cursor.fetchone()[0] == 1
        
        conn.close()


class TestDataIntegrity:
    """Test data integrity constraints"""
    
    def test_foreign_key_violation_on_delete(self, test_db):
        """Test that foreign key constraints prevent orphaned records"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        # This should work because CASCADE is set
        cursor.execute("INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)", 
                      ("Employee", "worker", None))
        emp_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO employee_contact (employee_id, phone, email, emergency_contact) VALUES (?, ?, ?, ?)",
            (emp_id, "555-0000", "test@test.com", "911")
        )
        conn.commit()
        
        # Delete employee
        cursor.execute("DELETE FROM employee WHERE employee_id = ?", (emp_id,))
        conn.commit()
        
        # Contact should be deleted due to CASCADE
        cursor.execute("SELECT * FROM employee_contact WHERE employee_id = ?", (emp_id,))
        assert cursor.fetchone() is None
        
        conn.close()
    
    def test_self_supervision_prevention(self, test_db):
        """Test that an employee cannot supervise themselves"""
        conn = app.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
            ("Self Supervisor", "manager", None)
        )
        emp_id = cursor.lastrowid
        conn.commit()
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "UPDATE employee SET supervisor_id = ? WHERE employee_id = ?",
                (emp_id, emp_id)
            )
            conn.commit()
        
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
