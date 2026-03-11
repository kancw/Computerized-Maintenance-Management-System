from database import setup_database, get_connection
import sqlite3
from datetime import datetime
import getpass
import os
import insert_data

def main():
    print("Campus Maintenance System")
    setup_database()
    
    while True:
        print("\n== Main Menu ==")
        print("1. Add data")
        print("2. Delete data")
        print("3. Update data")
        print("4. View data")
        print("5. Run SQL")
        print("6. Generate reports") 
        print("7. Exit")
        print("8. Restart Database (DBA only)")
        
        choice = input("Choose: ").strip()
        
        if choice == '1':
            add_data()
        elif choice == '2':
            delete_data()
        elif choice == '3':
            update_data()
        elif choice == '4':
            search_activities()
        elif choice == '5':
            run_sql()
        elif choice == '6':
            generate_reports()
        elif choice == '7':
            print("Bye!")
            break
        elif choice == '8':
            restart_database()
        else:
            print("Invalid choice. Please select a number from 1 to 8.")
            

def restart_database():
    print("\nDatabase Restart - DBA Access Required")
    print("WARNING: This will DELETE ALL DATA and recreate the database!")
    print("All activities, employees, buildings, and other data will be PERMANENTLY lost!")

    # First authentication
    firstConfirm = get_input("Type I UNDERSTAND to continue: ")
    if firstConfirm != 'I UNDERSTAND':
        print("Restart cancelled.")
        return
    
    # Second authentication
    DBA_password = getpass.getpass("Enter DBA password: ")  
    if DBA_password != 'DBA2411':
        print("Invalid DBA code. Access denied.")
        return
    
    print("\nCorrect Password")
    print("WARNING: This action cannot be undone!")

    # Third authentication
    secondConfirm = get_input("Type COMFIRM RESTART to confirm database restart: ")
    if secondConfirm != 'COMFIRM RESTART':
        print("Restart cancelled.")
        return

    try:
        # Get database path
        db_path = os.path.join(os.path.dirname(__file__), 'cmms.db')
        
        # Check if database exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Old database deleted.")
        else:
            print("No existing database found.")
        
        # Recreate database
        print("Restarting the database...")
        setup_database()
        
        print("Verifying foreign key enforcement...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        if result and result[0]:
            print("Foreign key enforcement enabled successfully")
        else:
            print("WARNING: Foreign keys are NOT enabled!")
            print("Data integrity may be compromised.")
        conn.close()

        # Reinsert sample data
        print("Inserting sample data...")
        insert_data.insert_data()
        
        print("Database restart completed successfully!")
        print("Please restart the application to use the new database.")
        
    except Exception as e:
        print(f"Unexpected error during database restart: {e}")

# Helper function to get input with 'menu' option
def get_input(prompt):
    user_input = input(prompt).strip()
    if user_input.lower() == 'menu':
        print("Returning to main menu...")
        return None
    return user_input

def add_data():
    while True:
        print("\nAdd Data Menu")
        print("1. Add Activity")
        print("2. Add Employee")
        print("3. Add Assignment")
        print("4. Add Building")
        print("5. Add Room")
        print("6. Add Outdoor Area")
        print("7. Add External Company")
        print("8. Add Contract")
        print("9. Add Chemical")
        print("10. Add Chemical Usage")

        choice = get_input("Choose: ")

        if choice is None:
            return

        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            print("Invalid choice. Please select 1-10.")
            continue
        
        conn = get_connection() 
        cursor = conn.cursor()

        try:
            if choice == '1':
                print("\nAdd Activity")
                activities = []

                while True:
                    # Activity type validation
                    valid_activity_types = ['cleaning', 'repair', 'renovation', 'weather-related', 'maintenance']
                    while True:
                        atype = get_input("Activity type (cleaning/repair/renovation/weather-related/maintenance): ")
                        if atype is None: return
                        atype = atype.lower()
                        if atype in valid_activity_types:
                            break
                        print("Invalid activity type. Please choose from: cleaning, repair, renovation, weather-related, maintenance")

                    # Location ID validation
                    while True:
                        location_id = get_input("Location ID: ")
                        cursor.execute("SELECT location_id FROM location WHERE location_id = ?", (location_id,))
                        if not cursor.fetchone():
                            print("Location ID not found in database.")
                            continue
                        if location_id is None: return
                        if location_id:
                            break
                        print("Location ID cannot be empty")

                    # Description
                    desc = get_input("Description: ")
                    if desc is None: return

                    # Start date validation
                    while True:
                        start_date = get_input("Start date (YYYY-MM-DD): ")
                        if start_date is None: return
                        try:
                            sd = datetime.strptime(start_date, "%Y-%m-%d")
                            break
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD.")

                    # End date validation
                    while True:
                        end_date = get_input("End date (YYYY-MM-DD): ")
                        if end_date is None: return
                        try:
                            ed = datetime.strptime(end_date, "%Y-%m-%d")
                            if ed >= sd:
                                break
                            else:
                                print("End date must be after start date.")
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD.")

                    # Status validation
                    valid_status = ['scheduled', 'in-progress', 'completed']
                    while True:
                        status = get_input("Status (Scheduled/In-Progress/Completed): ")
                        if status is None: return
                        status = status.lower()
                        if status in valid_status:
                            break
                        print("Invalid status. Please choose from: Scheduled, In-Progress, Completed")

                    # Manager ID
                    manager_id = get_input("Manager ID (or leave blank): ")
                    if manager_id is None: return
                    manager_id = manager_id or None

                    activities.append((atype, location_id, desc, start_date, end_date, status, manager_id))
                    
                    another = get_input("Add another activity? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if activities:
                    cursor.executemany("""
                        INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, activities)
                    conn.commit()
                    print(f"{len(activities)} activity(ies) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '2':
                print("\nAdd Employee")
                
                # Check current employee count before allowing addition
                cursor.execute("SELECT COUNT(*) FROM employee")
                current_count = cursor.fetchone()[0]
                
                if current_count >= 1000:
                    print("Maximum number of employees reached (1000). Cannot add more employees.")
                    return
                
                employees = []
                contacts = []
                
                remaining = 1000 - current_count
                print(f"You can add up to {remaining} more employee(s)")

                while True:
                    # Check if the limit is reached during batch addition
                    if len(employees) >= remaining:
                        print(f"Reached maximum employee limit ({current_count + len(employees)}/1000)")
                        break
                        
                    # Employee name
                    name = get_input("Employee name: ")
                    if name is None: 
                        return

                    # Employee type validation
                    valid_employee_types = ['executive', 'manager', 'worker']
                    while True:
                        etype = get_input("Employee type (executive/manager/worker): ")
                        if etype is None: return
                        etype = etype.lower()
                        if etype in valid_employee_types:
                            break
                        print("Invalid employee type. Please choose from: executive, manager, worker")

                    # Supervisor ID handling
                    supervisor_input = get_input("Supervisor ID (or leave blank): ")
                    if supervisor_input is None: return
                    
                    supervisor_id = None
                    if supervisor_input.strip():  # If not empty after stripping whitespace
                        try:
                            supervisor_id = int(supervisor_input)
                            
                            # Validate supervisor exists and has appropriate permissions
                            cursor.execute("SELECT employee_id, employee_type FROM employee WHERE employee_id = ?", (supervisor_id,))
                            supervisor = cursor.fetchone()
                            if not supervisor:
                                print("Supervisor ID not found in database.")
                                continue
                            
                            supervisor_type = supervisor[1]
                            
                            # Check supervision hierarchy rules
                            if supervisor_type == 'manager' and etype == 'executive':
                                print("Manager cannot supervise executives")
                                continue
                                
                            if supervisor_type == 'worker':
                                print("Workers cannot supervise anyone")
                                continue
                                
                        except ValueError:
                            print("Supervisor ID must be a valid number")
                            continue

                    # Add to batch
                    employees.append((name, etype, supervisor_id))
                    
                    # Contact information
                    phone = get_input("Phone: ")
                    if phone is None: return
                    
                    email = get_input("Email: ")
                    if email is None: return
                    
                    emergency_contact = get_input("Emergency contact: ")
                    if emergency_contact is None: return
                    
                    contacts.append((phone, email, emergency_contact))
                    
                    # If this addition would exceed the limit, stop here
                    if current_count + len(employees) >= 1000:
                        print(f"This will reach the maximum employee limit ({current_count + len(employees)}/1000)")
                        another = 'n'
                    else:
                        another = get_input("Add another employee? (y/n): ")
                        
                    if another is None or another.lower() != 'y':
                        break

                if employees:
                    try:
                        inserted_employee_ids = []
                        
                        # Insert employees one by one to get proper IDs
                        for i, (name, etype, supervisor_id) in enumerate(employees):
                            cursor.execute(
                                "INSERT INTO employee (name, employee_type, supervisor_id) VALUES (?, ?, ?)",
                                (name, etype, supervisor_id)
                            )
                            employee_id = cursor.lastrowid
                            inserted_employee_ids.append(employee_id)
                            print(f"DEBUG: Inserted employee with ID: {employee_id}")
                        
                        # Add corresponding contact entries
                        for i in range(len(contacts)):
                            employee_id = inserted_employee_ids[i]
                            phone, email, emergency_contact = contacts[i]
                            print(f"DEBUG: Adding contact for employee {employee_id}")
                            cursor.execute(
                                "INSERT INTO employee_contact (employee_id, phone, email, emergency_contact) VALUES (?, ?, ?, ?)",
                                (employee_id, phone, email, emergency_contact)
                            )
                        
                        conn.commit()
                        print(f"{len(employees)} employee(s) added. Total employees: {current_count + len(employees)}/1000")
                    except sqlite3.Error as e:
                        conn.rollback()
                        print(f"Unexpected error occurred: {e}")
                        print("This might be a database constraint issue. Please check your input.")
                else:
                    print("No employees were added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '3':
                print("\nAdd Assignment")
                
                assignments = []

                while True:
                    # Employee ID
                    emp_id = get_input("Employee ID: ")
                    if emp_id is None: return

                    # Employee ID validation
                    cursor.execute("SELECT employee_id FROM employee WHERE employee_id = ?", (emp_id,))
                    if not cursor.fetchone():
                        print("Employee ID not found in database.")
                        continue

                    # Activity ID
                    act_id = get_input("Activity ID: ")
                    if act_id is None: return
                    
                    # Activity ID validation
                    cursor.execute("SELECT activity_id FROM activity WHERE activity_id = ?", (act_id,))
                    if not cursor.fetchone():
                        print("Activity ID not found in database.")
                        continue

                    # Start date validation
                    while True:
                        start_date = get_input("Start date (YYYY-MM-DD): ")
                        if start_date is None: return
                        try:
                            sd = datetime.strptime(start_date, "%Y-%m-%d")
                            break
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD.")

                    # Due date validation
                    while True:
                        due_date = get_input("Due date (YYYY-MM-DD): ")
                        if due_date is None: return
                        try:
                            ed = datetime.strptime(due_date, "%Y-%m-%d")
                            if ed >= sd:  # Check if due date is after start date
                                break
                            else:
                                print("Due date must be after start date.")
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD.")

                    # Description
                    desc = get_input("Description: ")
                    if desc is None: return

                    assignments.append((emp_id, act_id, start_date, due_date, desc))
                    
                    another = get_input("Add another assignment? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if assignments:
                    cursor.executemany("""
                        INSERT INTO assignment (employee_id, activity_id, start_date, due_date, description)
                        VALUES (?, ?, ?, ?, ?)
                    """, assignments)
                    conn.commit()
                    print(f"{len(assignments)} assignment(s) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '4':
                print("\nAdd Building")
                
                # Check current building count before allowing addition
                cursor.execute("SELECT COUNT(*) FROM building")
                current_count = cursor.fetchone()[0]
                
                if current_count >= 99:
                    print("Maximum number of buildings reached (99). Cannot add more buildings.")
                    return
                
                buildings = []
                
                remaining = 99 - current_count
                print(f"You can add up to {remaining} more building(s)")

                while True:
                    # Check if we've reached the limit during batch addition
                    if len(buildings) >= remaining:
                        print(f"Reached maximum building limit ({current_count + len(buildings)}/99)")
                        break
                        
                    # Building name
                    name = get_input("Building name: ")
                    if name is None: 
                        return
                    
                    buildings.append((name,))
                    
                    # If this addition would exceed the limit, stop here
                    if current_count + len(buildings) >= 99:
                        print(f"This will reach the maximum building limit ({current_count + len(buildings)}/99)")
                        another = 'n'
                    else:
                        another = get_input("Add another building? (y/n): ")
                        
                    if another is None or another.lower() != 'y':
                        break

                if buildings:
                    # Insert buildings
                    cursor.executemany("INSERT INTO building (building_name) VALUES (?)", buildings)
                    
                    # Get the first building ID from this batch
                    first_id = cursor.lastrowid - len(buildings) + 1
                    
                    # Add corresponding location entries
                    for i in range(len(buildings)):
                        building_id = first_id + i
                        cursor.execute(
                            "INSERT INTO location (location_type, building_id, location_name) VALUES ('building', ?, ?)",
                            (building_id, buildings[i][0])
                        )
                    
                    conn.commit()
                    print(f"{len(buildings)} building(s) added. Total buildings: {current_count + len(buildings)}/99")
                else:
                    print("No buildings were added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '5':
                print("\nAdd Room")
                rooms = []
                room_locations = []
                valid_types = ['classroom','office','laboratory','conference','storage','restroom']

                while True:
                    # Building ID
                    bid_input = get_input("Building ID: ")
                    if bid_input is None: return
                    try:
                        bid = int(bid_input)
                    except ValueError:
                        print("Building ID must be a number")
                        continue

                    # Add validation after getting bid
                    cursor.execute("SELECT building_id FROM building WHERE building_id = ?", (bid,))
                    if not cursor.fetchone():
                        print("Building ID not found in database.")
                        continue

                    # Floor and Room Number (for encoded ID)
                    floor_input = get_input("Floor (0-99): ")
                    if floor_input is None: return
                    try:
                        floor = int(floor_input)
                        if floor < 0 or floor > 99:
                            print("Floor must be between 0 and 99")
                            continue
                    except ValueError:
                        print("Floor must be a number")
                        continue

                    room_num_input = get_input("Room number (0-99): ")
                    if room_num_input is None: return
                    try:
                        room_num = int(room_num_input)
                        if room_num < 0 or room_num > 99:
                            print("Room number must be between 0 and 99")
                            continue
                    except ValueError:
                        print("Room number must be a number")
                        continue

                    # Room type validation
                    while True:
                        rtype = get_input("Room type (classroom/office/laboratory/conference/storage/restroom): ")
                        if rtype is None: return
                        rtype = rtype.lower()
                        if rtype in valid_types:
                            break
                        print("Invalid room type. Please choose from: classroom, office, laboratory, conference, storage, restroom")
                    
                    # Room name for location table
                    room_name = get_input("Room name: ")
                    if room_name is None: return
                    
                    # Encode room ID (floor + room number)
                    encoded_room_id = int(f"{floor:02d}{room_num:02d}")
                    
                    rooms.append((bid, encoded_room_id, rtype))
                    room_locations.append(('room', bid, encoded_room_id, room_name))
                    
                    another = get_input("Add another room? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if rooms:
                    # Insert into room table
                    cursor.executemany("INSERT INTO room (building_id, room_id, room_type) VALUES (?, ?, ?)", rooms)
                    
                    # Insert into location table
                    cursor.executemany('''
                        INSERT INTO location (location_type, room_building_id, room_id, location_name) 
                        VALUES (?, ?, ?, ?)
                    ''', room_locations)
                    
                    conn.commit()
                    print(f"{len(rooms)} room(s) added with encoded IDs.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '6':
                print("\nAdd Outdoor Area")
                areas = []
                area_locations = []
                valid_types = ['square', 'gate', 'path', 'parking_lot', 'garden', 'sports_field']

                while True:
                    # Outdoor area name
                    name = get_input("Outdoor area name: ")
                    if name is None: return

                    # Outdoor area type validation
                    while True:
                        atype = get_input("Outdoor area type (square/gate/path/parking_lot/garden/sports_field): ")
                        if atype is None: return
                        atype = atype.lower()
                        if atype in valid_types:
                            break
                        print("Invalid outdoor area type. Please choose from: square, gate, path, parking_lot, garden, sports_field")

                    areas.append((name, atype))
                    
                    another = get_input("Add another area? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if areas:
                    # Insert into outdoor_area table
                    cursor.executemany("INSERT INTO outdoor_area (area_name, area_type) VALUES (?, ?)", areas)
                    
                    # Get the first area ID from this batch
                    first_id = cursor.lastrowid - len(areas) + 1
                    
                    # Insert into location table
                    for i in range(len(areas)):
                        area_id = first_id + i
                        area_name, area_type = areas[i]
                        cursor.execute(
                            "INSERT INTO location (location_type, outdoor_area_id, location_name) VALUES ('outdoor_area', ?, ?)",
                            (area_id, area_name)
                        )
                    
                    conn.commit()
                    print(f"{len(areas)} outdoor area(s) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '7':
                print("\nAdd External Company")
                companies = []

                while True:
                    # Company name
                    cname = get_input("Company name: ")
                    if cname is None: return

                    # Specialization
                    spec = get_input("Specialization: ")
                    if spec is None: return

                    # Contact info
                    contact = get_input("Contact info: ")
                    if contact is None: return

                    companies.append((cname, spec, contact))
                    
                    another = get_input("Add another company? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                cursor.executemany("INSERT INTO external_company (company_name, specialization, contact_info) VALUES (?, ?, ?)", companies)
                conn.commit()
                print(f"{len(companies)} company(ies) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '8':
                print("\nAdd Contract")
                contracts = []

                while True:
                    # Company ID
                    cid = get_input("Company ID: ")
                    if cid is None: return
                    
                    # Company ID validation
                    cursor.execute("SELECT company_id FROM external_company WHERE company_id = ?", (cid,))
                    if not cursor.fetchone():
                        print("Company ID not found in database.")
                        continue

                    # Activity ID
                    aid = get_input("Activity ID: ")
                    if aid is None: return
                    
                    # Activity ID validation
                    cursor.execute("SELECT activity_id FROM activity WHERE activity_id = ?", (aid,))
                    if not cursor.fetchone():
                        print("Activity ID not found in database.")
                        continue

                    # Contract description
                    desc = get_input("Contract description: ")
                    if desc is None: return

                    # Contract date validation
                    while True:
                        date = get_input("Contract date (YYYY-MM-DD): ")
                        if date is None: return
                        try:
                            contract_date = datetime.strptime(date, "%Y-%m-%d")
                            break
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD.")

                    contracts.append((cid, aid, desc, date))
                    
                    another = get_input("Add another contract? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                cursor.executemany("INSERT INTO contract (company_id, activity_id, contract_description, contract_date) VALUES (?, ?, ?, ?)", contracts)
                conn.commit()
                print(f"{len(contracts)} contract(s) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '9':
                print("\nAdd Chemical")
                chemicals = []

                while True:
                    # Chemical name
                    cname = get_input("Chemical name: ")
                    if cname is None: return

                    # Hazard level validation
                    while True:
                        hazard_input = get_input("Hazard level (0-4): ")
                        if hazard_input is None: return
                        
                        try:
                            hazard = int(hazard_input)
                            if 0 <= hazard <= 4:
                                break
                            else:
                                print("Invalid hazard level. Must be between 0 and 4.")
                        except ValueError:
                            print("Invalid input. Please enter a number between 0 and 4.")

                    chemicals.append((cname, hazard))
                    
                    another = get_input("Add another chemical? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if chemicals:
                    cursor.executemany("INSERT INTO chemical (chemical_name, hazard_level) VALUES (?, ?)", chemicals)
                    conn.commit()
                    print(f"{len(chemicals)} chemical(s) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '10':
                print("\nAdd Chemical Usage")
                usages = []

                while True:
                    # Activity ID
                    aid = get_input("Activity ID: ")
                    if aid is None: return

                    # Activity ID validation
                    cursor.execute("SELECT activity_id FROM activity WHERE activity_id = ?", (aid,))
                    if not cursor.fetchone():
                        print("Activity ID not found in database.")
                        continue

                    # Chemical ID
                    cid = get_input("Chemical ID: ")
                    if cid is None: return

                    # Chemical ID validation
                    cursor.execute("SELECT chemical_id FROM chemical WHERE chemical_id = ?", (cid,))
                    if not cursor.fetchone():
                        print("Chemical ID not found in database.")
                        continue

                    # Quantity validation
                    while True:
                        qty_input = get_input("Quantity used: ")
                        if qty_input is None: return
                        
                        try:
                            qty = int(qty_input)
                            if qty >= 0:
                                break
                            else:
                                print("Quantity must be a positive number.")
                        except ValueError:
                            print("Invalid input. Please enter a valid number for quantity.")

                    # Usage reason
                    reason = get_input("Usage reason: ")
                    if reason is None: return

                    usages.append((cid, aid, qty, reason))
                    
                    another = get_input("Add another usage record? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if usages:
                    cursor.executemany("""
                        INSERT INTO chemical_usage (chemical_id, activity_id, quantity_used, usage_reasons)
                        VALUES (?, ?, ?, ?)
                    """, usages)
                    conn.commit()
                    print(f"{len(usages)} chemical usage record(s) added.")

                exit_choice = get_input("Do you want to quit add menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

        except sqlite3.Error as e:
            conn.rollback()
            print("Unexpected error occurred:", e)

        finally:
            conn.close()

def strong_confirm(message):
    """
    warning message and require user to type 'confirm'.
    Returns True if confirmed, False otherwise.
    """
    print("\nWARNING")
    print(message)
    choice = get_input("Type 'confirm' to proceed, or anything else to cancel: ")
    if choice is None:
        return False
    return choice.lower() == "confirm"

def delete_data():
    while True:
        print("\n== Delete Menu ==")
        print("1. Delete Activity")
        print("2. Delete Employee")
        print("3. Delete Assignment")
        print("4. Delete Building")
        print("5. Delete Room")
        print("6. Delete Outdoor Area")
        print("7. Delete External Company")
        print("8. Delete Contract")
        print("9. Delete Chemical")
        print("10. Delete Chemical Usage")

        choice = get_input("Choose: ")

        if choice is None:
            return

        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            print("Invalid choice. Please select 1-10.")
            continue

        conn = get_connection()
        cursor = conn.cursor()

        try:
            if choice == '1':
                print("\nDelete Activity")
                ids = []
                while True:
                    aid = get_input("Activity ID to delete: ")
                    if aid is None: return

                    cursor.execute("SELECT activity_id FROM activity WHERE activity_id = ?", (aid,))
                    if not cursor.fetchone():
                        print("Activity ID not found.")
                        continue

                    if not strong_confirm(f"Deleting activity {aid} will also remove all assignments linked to it."):
                        print("Cancelled.")
                        continue

                    ids.append((aid,))
                    another = get_input("Delete another activity? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM activity WHERE activity_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} activity(ies) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '2':
                print("\nDelete Employee")
                ids = []
                while True:
                    eid = get_input("Employee ID to delete: ")
                    if eid is None: return

                    cursor.execute("SELECT employee_id FROM employee WHERE employee_id = ?", (eid,))
                    if not cursor.fetchone():
                        print("Employee ID not found.")
                        continue

                    if not strong_confirm(f"Deleting employee {eid} will also remove all assignments linked to this employee."):
                        print("Cancelled.")
                        continue

                    ids.append((eid,))
                    another = get_input("Delete another employee? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM employee WHERE employee_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} employee(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '3':
                print("\nDelete Assignment")
                ids = []
                while True:
                    assid = get_input("Assignment ID to delete: ")
                    if assid is None: return

                    cursor.execute("SELECT assignment_id FROM assignment WHERE assignment_id = ?", (assid,))
                    if not cursor.fetchone():
                        print("Assignment ID not found.")
                        continue

                    if not strong_confirm(f"Deleting assignment {assid} will unlink employees and activities tied to it."):
                        print("Cancelled.")
                        continue

                    ids.append((assid,))
                    another = get_input("Delete another assignment? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM assignment WHERE assignment_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} assignment(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '4':
                print("\nDelete Building")
                ids = []
                while True:
                    bid = get_input("Building ID to delete: ")
                    if bid is None: return

                    cursor.execute("SELECT building_id FROM building WHERE building_id = ?", (bid,))
                    if not cursor.fetchone():
                        print("Building ID not found.")
                        continue

                    if not strong_confirm(f"Deleting building {bid} will also remove all rooms and assignments linked to it."):
                        print("Cancelled.")
                        continue

                    ids.append((bid,))
                    another = get_input("Delete another building? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM building WHERE building_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} building(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '5':
                print("\nDelete Room")
                rooms = []
                while True:
                    bid = get_input("Building ID: ")
                    if bid is None: return
                    try:
                        bid = int(bid)
                    except:
                        print("Building ID must be a number.")
                        continue

                    rid = get_input("Room ID (encoded, e.g. 0105): ")
                    if rid is None: return
                    try:
                        rid = int(rid)
                    except:
                        print("Room ID must be a number.")
                        continue

                    cursor.execute("SELECT room_id FROM room WHERE building_id = ? AND room_id = ?", (bid, rid))
                    if not cursor.fetchone():
                        print("Room not found.")
                        continue

                    if not strong_confirm(f"Deleting room {rid} in building {bid} will remove all usage records tied to it."):
                        print("Cancelled.")
                        continue

                    rooms.append((bid, rid))
                    another = get_input("Delete another room? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if rooms:
                    cursor.executemany("DELETE FROM room WHERE building_id = ? AND room_id = ?", rooms)
                    conn.commit()
                    print(f"{len(rooms)} room(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '6':
                print("\nDelete Outdoor Area")
                ids = []
                while True:
                    oid = get_input("Outdoor Area ID to delete: ")
                    if oid is None: return

                    cursor.execute("SELECT area_id FROM outdoor_area WHERE area_id = ?", (oid,))
                    if not cursor.fetchone():
                        print("Outdoor Area ID not found.")
                        continue

                    if not strong_confirm(f"Deleting outdoor area {oid} will remove all linked contracts or usage records."):
                        print("Cancelled.")
                        continue

                    ids.append((oid,))
                    another = get_input("Delete another outdoor area? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM outdoor_area WHERE area_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} outdoor area(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '7':
                print("\nDelete External Company")
                ids = []
                while True:
                    cid = get_input("Company ID to delete: ")
                    if cid is None: return

                    cursor.execute("SELECT company_id FROM external_company WHERE company_id = ?", (cid,))
                    if not cursor.fetchone():
                        print("Company ID not found.")
                        continue

                    if not strong_confirm(f"Deleting company {cid} will also remove all contracts tied to it."):
                        print("Cancelled.")
                        continue

                    ids.append((cid,))
                    another = get_input("Delete another company? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM external_company WHERE company_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} company(ies) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '8':
                print("\nDelete Contract")
                ids = []
                while True:
                    cid = get_input("Contract ID to delete: ")
                    if cid is None: return

                    cursor.execute("SELECT contract_id FROM contract WHERE contract_id = ?", (cid,))
                    if not cursor.fetchone():
                        print("Contract ID not found.")
                        continue

                    if not strong_confirm(f"Deleting contract {cid} will unlink external companies and areas tied to it."):
                        print("Cancelled.")
                        continue

                    ids.append((cid,))
                    another = get_input("Delete another contract? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM contract WHERE contract_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} contract(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '9':
                print("\nDelete Chemical")
                ids = []
                while True:
                    chemid = get_input("Chemical ID to delete: ")
                    if chemid is None: return

                    cursor.execute("SELECT chemical_id FROM chemical WHERE chemical_id = ?", (chemid,))
                    if not cursor.fetchone():
                        print("Chemical ID not found.")
                        continue

                    if not strong_confirm(f"Deleting contract {chemid} will unlink external companies and areas tied to it."):
                        print("Cancelled.")
                        continue

                    ids.append((chemid,))
                    another = get_input("Delete another chemical? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM chemical WHERE chemical_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} chemical(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

            elif choice == '10':
                print("\nDelete Chemical Usage")
                ids = []
                while True:
                    uid = get_input("Chemical Usage ID to delete: ")
                    if uid is None: return

                    cursor.execute("SELECT usage_id FROM chemical_usage WHERE usage_id = ?", (uid,))
                    if not cursor.fetchone():
                        print("Usage record not found.")
                        continue

                    if not strong_confirm(f"Deleting contract {uid} will unlink external companies and areas tied to it."):
                        print("Cancelled.")
                        continue

                    ids.append((uid,))
                    another = get_input("Delete another usage record? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                if ids:
                    cursor.executemany("DELETE FROM chemical_usage WHERE usage_id = ?", ids)
                    conn.commit()
                    print(f"{len(ids)} chemical usage record(s) deleted.")

                    exit_choice = get_input("Do you want to quit delete menu? (y/n): ")
                    if exit_choice and exit_choice.lower() == 'y':
                        return

        except sqlite3.Error as e:
            conn.rollback()
            print("Error occurred:", e)
        finally:
            conn.close()

def update_data():
    while True:
        print("\n== Update Data Menu ==")
        print("1. Update Activity")
        print("2. Update Employee")
        print("3. Update Assignment")
        print("4. Update Building")
        print("5. Update Room")
        print("6. Update Outdoor Area")
        print("7. Update External Company")
        print("8. Update Contract")
        print("9. Update Chemical")
        print("10. Update Chemical Usage")
        
        choice = get_input("Choose: ")

        if choice is None:
            return

        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            print("Invalid choice. Please select 1-10.")
            continue

        conn = get_connection()
        cursor = conn.cursor()

        try:
            if choice == '1':
                print("\nUpdate Activity")
                while True:
                    aid = get_input("Activity ID to update: ")
                    if aid is None: return

                    cursor.execute("SELECT * FROM activity WHERE activity_id = ?", (aid,))
                    if not cursor.fetchone():
                        print("Activity ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    desc = get_input("New description (blank to keep): ")
                    if desc:
                        updates.append("description = ?")
                        params.append(desc)

                    start_date = get_input("New start date (YYYY-MM-DD, blank to keep): ")
                    if start_date:
                        try:
                            sd = datetime.strptime(start_date, "%Y-%m-%d")
                            updates.append("start_date = ?")
                            params.append(start_date)
                        except ValueError:
                            print("Invalid date format. Skipped.")

                    end_date = get_input("New end date (YYYY-MM-DD, blank to keep): ")
                    if end_date:
                        try:
                            ed = datetime.strptime(end_date, "%Y-%m-%d")
                            if start_date and ed < sd:
                                print("End date cannot be before start date. Skipped.")
                            else:
                                updates.append("end_date = ?")
                                params.append(end_date)
                        except ValueError:
                            print("Invalid date format. Skipped.")

                    status = get_input("New status (scheduled/in progress/completed, blank to keep): ")
                    if status:
                        status = status.lower()
                        if status in ['scheduled', 'in progress', 'completed']:
                            updates.append("status = ?")
                            params.append(status)
                        else:
                            print("Invalid status. Must be: scheduled, in progress, completed")

                    manager_id = get_input("New manager ID (blank to keep or clear): ")
                    if manager_id == "":
                        updates.append("manager_id = NULL")
                    elif manager_id:
                        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = ?", (manager_id,))
                        if cursor.fetchone():
                            updates.append("manager_id = ?")
                            params.append(manager_id)
                        else:
                            print("Manager ID not found. Skipped.")

                    if updates:
                        params.append(aid)
                        sql = f"UPDATE activity SET {', '.join(updates)} WHERE activity_id = ?"
                        cursor.execute(sql, params)
                        conn.commit()
                        print("Activity updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another activity? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

            elif choice == '2':
                print("\nUpdate Employee")
                while True:
                    eid = get_input("Employee ID to update: ")
                    if eid is None: return

                    cursor.execute("SELECT * FROM employee WHERE employee_id = ?", (eid,))
                    if not cursor.fetchone():
                        print("Employee ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    name = get_input("New name (blank to keep): ")
                    if name:
                        updates.append("name = ?")
                        params.append(name)

                    etype = get_input("New employee type (executive/manager/worker, blank to keep): ").lower()
                    if etype:
                        if etype in ['executive', 'manager', 'worker']:
                            updates.append("employee_type = ?")
                            params.append(etype)
                        else:
                            print("Invalid type. Must be executive, manager, or worker.")

                    sup_id = get_input("New supervisor ID (blank to keep, or type 'none' to clear): ")
                    if sup_id == 'none':
                        updates.append("supervisor_id = NULL")
                    elif sup_id:
                        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = ?", (sup_id,))
                        if cursor.fetchone():
                            updates.append("supervisor_id = ?")
                            params.append(sup_id)
                        else:
                            print("Supervisor ID not found. Skipped.")

                    if updates:
                        params.append(eid)
                        cursor.execute(f"UPDATE employee SET {', '.join(updates)} WHERE employee_id = ?", params)
                        conn.commit()
                        print("Employee updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another employee? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '3':
                print("\nUpdate Assignment")
                while True:
                    assid = get_input("Assignment ID to update: ")
                    if assid is None: return

                    cursor.execute("SELECT * FROM assignment WHERE assignment_id = ?", (assid,))
                    if not cursor.fetchone():
                        print("Assignment ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    desc = get_input("New description (blank to keep): ")
                    if desc:
                        updates.append("description = ?")
                        params.append(desc)

                    start = get_input("New start date (YYYY-MM-DD, blank to keep): ")
                    if start:
                        try:
                            datetime.strptime(start, "%Y-%m-%d")
                            updates.append("start_date = ?")
                            params.append(start)
                        except ValueError:
                            print("Invalid date. Skipped.")

                    due = get_input("New due date (YYYY-MM-DD, blank to keep): ")
                    if due:
                        try:
                            dd = datetime.strptime(due, "%Y-%m-%d")
                            if start and dd < datetime.strptime(start, "%Y-%m-%d"):
                                print("Due date cannot be before start date.")
                            else:
                                updates.append("due_date = ?")
                                params.append(due)
                        except ValueError:
                            print("Invalid date. Skipped.")

                    if updates:
                        params.append(assid)
                        cursor.execute(f"UPDATE assignment SET {', '.join(updates)} WHERE assignment_id = ?", params)
                        conn.commit()
                        print("Assignment updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another assignment? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '4':
                print("\nUpdate Building")
                while True:
                    bid = get_input("Building ID to update: ")
                    if bid is None: return

                    cursor.execute("SELECT building_id FROM building WHERE building_id = ?", (bid,))
                    if not cursor.fetchone():
                        print("Building ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    new_name = get_input("New building name (blank to keep): ")
                    if new_name:
                        cursor.execute("UPDATE building SET building_name = ? WHERE building_id = ?", (new_name, bid))
                        cursor.execute("UPDATE location SET location_name = ? WHERE location_type = 'building' AND building_id = ?", (new_name, bid))
                        conn.commit()
                        print("Building name updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another building? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '5':
                print("\nUpdate Room")
                while True:
                    bid_input = get_input("Building ID: ")
                    if bid_input is None: return
                    try:
                        bid = int(bid_input)
                    except:
                        print("Building ID must be a number.")
                        continue

                    rid_input = get_input("Room ID (encoded, e.g. 0105): ")
                    if rid_input is None: return
                    try:
                        rid = int(rid_input)
                    except:
                        print("Room ID must be a number.")
                        continue

                    cursor.execute("SELECT room_id FROM room WHERE building_id = ? AND room_id = ?", (bid, rid))
                    if not cursor.fetchone():
                        print("Room not found.")
                        if get_input("Try another room? (y/n): ").lower() != 'y':
                            break
                        continue

                    updated = False

                    rtype = get_input("New room type (classroom/office/laboratory/conference/storage/restroom, blank to keep): ").lower()
                    if rtype:
                        valid = ['classroom','office','laboratory','conference','storage','restroom']
                        if rtype in valid:
                            cursor.execute("UPDATE room SET room_type = ? WHERE building_id = ? AND room_id = ?", (rtype, bid, rid))
                            updated = True
                        else:
                            print("Invalid room type.")

                    room_name = get_input("New room name (blank to keep): ")
                    if room_name:
                        cursor.execute("UPDATE location SET location_name = ? WHERE location_type = 'room' AND room_building_id = ? AND room_id = ?", (room_name, bid, rid))
                        updated = True

                    if updated:
                        conn.commit()
                        print(f"Room {rid} in building {bid} updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another room? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '6':
                print("\nUpdate Outdoor Area")
                while True:
                    oid = get_input("Outdoor Area ID to update: ")
                    if oid is None: return

                    cursor.execute("SELECT area_id FROM outdoor_area WHERE area_id = ?", (oid,))
                    if not cursor.fetchone():
                        print("Outdoor Area ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    name = get_input("New area name (blank to keep): ")
                    if name:
                        updates.append("area_name = ?")
                        params.append(name)
                        cursor.execute("UPDATE location SET location_name = ? WHERE location_type = 'outdoor_area' AND outdoor_area_id = ?", (name, oid))

                    atype = get_input("New area type (square/gate/path/parking_lot/garden/sports_field, blank to keep): ").lower()
                    if atype:
                        valid = ['square','gate','path','parking_lot','garden','sports_field']
                        if atype in valid:
                            updates.append("area_type = ?")
                            params.append(atype)
                        else:
                            print("Invalid area type.")

                    if updates:
                        params.append(oid)
                        cursor.execute(f"UPDATE outdoor_area SET {', '.join(updates)} WHERE area_id = ?", params)
                        conn.commit()
                        print("Outdoor area updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another outdoor area? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '7':
                print("\nUpdate External Company")
                while True:
                    cid = get_input("Company ID to update: ")
                    if cid is None: return

                    cursor.execute("SELECT company_id FROM external_company WHERE company_id = ?", (cid,))
                    if not cursor.fetchone():
                        print("Company ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    cname = get_input("New company name (blank to keep): ")
                    if cname: updates.append("company_name = ?"); params.append(cname)

                    spec = get_input("New specialization (blank to keep): ")
                    if spec: updates.append("specialization = ?"); params.append(spec)

                    contact = get_input("New contact info (blank to keep): ")
                    if contact: updates.append("contact_info = ?"); params.append(contact)

                    if updates:
                        params.append(cid)
                        cursor.execute(f"UPDATE external_company SET {', '.join(updates)} WHERE company_id = ?", params)
                        conn.commit()
                        print("External company updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another company? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '8':
                print("\nUpdate Contract")
                while True:
                    conid = get_input("Contract ID to update: ")
                    if conid is None: return

                    cursor.execute("SELECT contract_id FROM contract WHERE contract_id = ?", (conid,))
                    if not cursor.fetchone():
                        print("Contract ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    desc = get_input("New contract description (blank to keep): ")
                    if desc: updates.append("contract_description = ?"); params.append(desc)

                    cdate = get_input("New contract date (YYYY-MM-DD, blank to keep): ")
                    if cdate:
                        try:
                            datetime.strptime(cdate, "%Y-%m-%d")
                            updates.append("contract_date = ?")
                            params.append(cdate)
                        except ValueError:
                            print("Invalid date format.")

                    if updates:
                        params.append(conid)
                        cursor.execute(f"UPDATE contract SET {', '.join(updates)} WHERE contract_id = ?", params)
                        conn.commit()
                        print("Contract updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another contract? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '9':
                print("\nUpdate Chemical")
                while True:
                    chemid = get_input("Chemical ID to update: ")
                    if chemid is None: return

                    cursor.execute("SELECT chemical_id FROM chemical WHERE chemical_id = ?", (chemid,))
                    if not cursor.fetchone():
                        print("Chemical ID not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    cname = get_input("New chemical name (blank to keep): ")
                    if cname: updates.append("chemical_name = ?"); params.append(cname)

                    hazard = get_input("New hazard level (0-4, blank to keep): ")
                    if hazard:
                        try:
                            h = int(hazard)
                            if 0 <= h <= 4:
                                updates.append("hazard_level = ?")
                                params.append(h)
                            else:
                                print("Hazard level must be 0–4.")
                        except ValueError:
                            print("Must be a number.")

                    if updates:
                        params.append(chemid)
                        cursor.execute(f"UPDATE chemical SET {', '.join(updates)} WHERE chemical_id = ?", params)
                        conn.commit()
                        print("Chemical updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another chemical? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return


            elif choice == '10':
                print("\nUpdate Chemical Usage")
                while True:
                    uid = get_input("Chemical Usage ID to update: ")
                    if uid is None: return

                    cursor.execute("SELECT usage_id FROM chemical_usage WHERE usage_id = ?", (uid,))
                    if not cursor.fetchone():
                        print("Usage record not found.")
                        if get_input("Try another? (y/n): ").lower() != 'y':
                            break
                        continue

                    updates = []
                    params = []

                    qty = get_input("New quantity used (blank to keep): ")
                    if qty:
                        try:
                            q = int(qty)
                            if q >= 0:
                                updates.append("quantity_used = ?")
                                params.append(q)
                            else:
                                print("Quantity cannot be negative.")
                        except ValueError:
                            print("Must be a valid number.")

                    reason = get_input("New usage reason (blank to keep): ")
                    if reason: updates.append("usage_reasons = ?"); params.append(reason)

                    if updates:
                        params.append(uid)
                        cursor.execute(f"UPDATE chemical_usage SET {', '.join(updates)} WHERE usage_id = ?", params)
                        conn.commit()
                        print("Chemical usage record updated successfully.")
                    else:
                        print("No changes made.")

                    another = get_input("Update another usage record? (y/n): ")
                    if another is None or another.lower() != 'y':
                        break

                exit_choice = get_input("Do you want to quit update menu? (y/n): ")
                if exit_choice and exit_choice.lower() == 'y':
                    return

        except sqlite3.Error as e:
            conn.rollback()
            print("Database error occurred:", e)
        finally:
            conn.close()

def search_activities():
    while True:
        print("\nView Menu")
        print("1. View Activities")
        print("2. View Employees")
        print("3. View Assignments")
        print("4. View Buildings")
        print("5. View Rooms")
        print("6. View Outdoor Areas")
        print("7. View External Companies")
        print("8. View Contracts")
        print("9. View Chemicals")
        print("10. View Chemical Usage")
        print("11. View scheduled cleaning activities")

        choice = get_input("Choose: ")

        if choice is None:
            return

        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
            print("Invalid choice. Please select 1-11.")
            continue
        
        
        conn = get_connection()
        cursor = conn.cursor()

        if choice == '1':
            print()
            print("1. Search by Activity ID")
            print("2. Search by Activity location ID")
            print("3. Search by Activity status")
            print("4. View all Activities")

            choice1 =  get_input("Choose: ")

            if choice1 is None:
                return

            if choice1 not in ['1', '2', '3', '4']:
                print("Invalid choice. Please select 1-4.")
                continue

            if choice1 == '1':
                cursor.execute("SELECT * FROM Activity WHERE activity_id = ?", (get_input("Enter activity ID to search: "),))
                print("\n{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                    "ID", "Type", "location_id", "description", "Start Date", "End date", "Status", "Manager"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                        row[0], row[1], str(row[2])[:15], row[3], row[4], row[5], row[6], row[7]))
                    
            elif choice1 == '2':
                cursor.execute("SELECT * FROM Activity WHERE location_id = ?", (get_input("Enter location ID to search: "),))
                print("\n{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                    "ID", "Type", "location_id", "description", "Start Date", "End date", "Status", "Manager"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                        row[0], row[1], str(row[2])[:15], row[3], row[4], row[5], row[6], row[7]))
                    
            elif choice1 == '3':
                cursor.execute("SELECT * FROM Activity WHERE status = ?", (get_input("Enter status to search (Scheduled/In Progress/Completed): "),))
                print("\n{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                    "ID", "Type", "location_id", "description", "Start Date", "End date", "Status", "Manager"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                        row[0], row[1], str(row[2])[:15], row[3], row[4], row[5], row[6], row[7]))
                    
            elif choice1 == '4':
                cursor.execute("SELECT * FROM Activity")
                print("\n{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                    "ID", "Type", "location_id", "description", "Start Date", "End date", "Status", "Manager"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<50} {:<15} {:<15} {:<15} {:<10}".format(
                        row[0], row[1], str(row[2])[:15], row[3], row[4], row[5], row[6], row[7]))
                
        elif choice == '2':
            print()
            print("1. Search by Employee Name")
            print("2. Search by Employee ID")
            print("3. Search by Supervisor ID")
            print("4. View all Employees")

            choice2 =  get_input("Choose: ")

            if choice2 is None:
                return

            if choice2 not in ['1', '2', '3', '4']:
                print("Invalid choice. Please select 1-4.")
                continue

            if choice2 == '1':
                cursor.execute("SELECT * FROM Employee WHERE name = ?", ( get_input("Enter name to search: "),))
                print("\n{:<4} {:<25} {:<10} {:<10}".format("ID", "Name", "Type", "Supervisor"))
                print()
                for row in cursor.fetchall():
                    supervisor = str(row[3]) if row[3] else "None"
                    print("{:<4} {:<25} {:<10} {:<10}".format(row[0], row[1], row[2], supervisor))
                    
            elif choice2 == '2':
                cursor.execute("SELECT * FROM Employee WHERE employee_id = ?", (get_input("Enter employee ID to search: "),))
                print("\n{:<4} {:<25} {:<10} {:<10}".format("ID", "Name", "Type", "Supervisor"))
                print()
                for row in cursor.fetchall():
                    supervisor = str(row[3]) if row[3] else "None"
                    print("{:<4} {:<25} {:<10} {:<10}".format(row[0], row[1], row[2], supervisor))
            
            elif choice2 == '3':
                cursor.execute("SELECT * FROM Employee WHERE supervisor_id = ?", (get_input("Enter supervisor ID to search: "),))
                print("\n{:<4} {:<25} {:<10} {:<10}".format("ID", "Name", "Type", "Supervisor"))
                print()
                for row in cursor.fetchall():
                    supervisor = str(row[3]) if row[3] else "None"
                    print("{:<4} {:<25} {:<10} {:<10}".format(row[0], row[1], row[2], supervisor))
            elif choice2 == '4':
                cursor.execute("SELECT * FROM Employee")
                print("\n{:<4} {:<25} {:<10} {:<10}".format("ID", "Name", "Type", "Supervisor"))
                print()
                for row in cursor.fetchall():
                    supervisor = str(row[3]) if row[3] else "None"
                    print("{:<4} {:<25} {:<10} {:<10}".format(row[0], row[1], row[2], supervisor))

        elif choice == '3':
            print()
            print("1.Search by Assignment ID")
            print("2.Search by Employee ID")
            print("3.Search by Activity ID")
            print("4.Search by due date")
            print("5.View all Assignments")
            
            choice3 =  get_input("Choose: ")

            if choice3 is None:
                return

            if choice3 not in ['1', '2', '3', '4', '5']:
                print("Invalid choice. Please select 1-5.")
                continue

            if choice3 == '1':
                cursor.execute("""
                    SELECT 
                        a1.assignment_id, e.name, a.activity_type, a.description, a1.start_date, a1.due_date, a.status, a.manager_id
                    FROM assignment a1
                    JOIN employee e ON a1.employee_id = e.employee_id
                    JOIN activity a ON a1.activity_id = a.activity_id
                    WHERE a1.assignment_id = ?
                """, (get_input("Enter assignment ID to search: "),))
                print("\n{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format("ID", "Employee", "Activity Type", "Description", "Start Date", "Due Date", "Status", "Manager ID"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format(row[0], row[1], row[2], row[3][:29], row[4], row[5], row[6], row[7]))
                    
            elif choice3 == '2':
                cursor.execute("""
                    SELECT 
                        a1.assignment_id, e.name, a.activity_type, a.description, a1.start_date, a1.due_date, a.status, a.manager_id
                    FROM assignment a1
                    JOIN employee e ON a1.employee_id = e.employee_id
                    JOIN activity a ON a1.activity_id = a.activity_id
                    WHERE a1.employee_id = ?
                """, (get_input("Enter employee ID to search: "),))
                print("\n{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format("ID", "Employee", "Activity Type", "Description", "Start Date", "Due Date", "Status", "Manager ID"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format(row[0], row[1], row[2], row[3][:29], row[4], row[5], row[6], row[7]))
                    
            elif choice3 == '3':
                cursor.execute("""
                    SELECT 
                        a1.assignment_id, e.name, a.activity_type, a.description, a1.start_date, a1.due_date, a.status, a.manager_id
                    FROM assignment a1
                    JOIN employee e ON a1.employee_id = e.employee_id
                    JOIN activity a ON a1.activity_id = a.activity_id
                    WHERE a1.activity_id = ?
                """, (get_input("Enter activity ID to search: "),))
                print("\n{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format("ID", "Employee", "Activity Type", "Description", "Start Date", "Due Date", "Status", "Manager ID"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format(row[0], row[1], row[2], row[3][:29], row[4], row[5], row[6], row[7]))
                    
            elif choice3 == '4':
                cursor.execute("""
                    SELECT 
                        a1.assignment_id, e.name, a.activity_type, a.description, a1.start_date, a1.due_date, a.status, a.manager_id
                    FROM assignment a1
                    JOIN employee e ON a1.employee_id = e.employee_id
                    JOIN activity a ON a1.activity_id = a.activity_id
                    WHERE a1.due_date = ?
                """, (get_input("Enter due date to search: "),))
                print("\n{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format("ID", "Employee", "Activity Type", "Description", "Start Date", "Due Date", "Status", "Manager ID"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format(row[0], row[1], row[2], row[3][:29], row[4], row[5], row[6], row[7]))
                    
            elif choice3 == '5':
                cursor.execute("""
                    SELECT 
                        a1.assignment_id, e.name, a.activity_type, a.description, a1.start_date, a1.due_date, a.status, a.manager_id
                    FROM assignment a1
                    JOIN employee e ON a1.employee_id = e.employee_id
                    JOIN activity a ON a1.activity_id = a.activity_id
                """)
                print("\n{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format("ID", "Employee", "Activity Type", "Description", "Start Date", "Due Date", "Status", "Manager ID"))
                print()
                for row in cursor.fetchall():
                    print("{:<6} {:<20} {:<15} {:<30} {:<15} {:<15} {:<15} {:<20}".format(row[0], row[1], row[2], row[3][:29], row[4], row[5], row[6], row[7]))

        elif choice == '4':
            cursor.execute("SELECT * FROM building")
            print("\n{:<15} {:<30}".format("Building ID", "Building Name"))
            print()
            for row in cursor.fetchall():
                print("{:<15} {:<30}".format(row[0], row[1]))

        elif choice == '5':
            cursor.execute("SELECT * FROM room")
            print("\n{:<10} {:<15} {:<15}".format("Room ID", "Room Type", "Building ID"))
            print()
            for row in cursor.fetchall():
                print("{:<10} {:<15} {:<15}".format(row[1], row[2], row[0]))

        elif choice == '6':
            cursor.execute("SELECT * FROM outdoor_area")
            print("\n{:<4} {:<30} {:<15}".format("ID", "Name", "Type"))
            print()
            for row in cursor.fetchall():
                print("{:<4} {:<30} {:<15}".format(row[0], row[1], row[2]))

        elif choice == '7':
            cursor.execute("SELECT company_id, company_name, specialization FROM external_company")
            print("\n{:<4} {:<25} {:<20}".format("ID", "Company Name", "Specialization"))
            print()
            for row in cursor.fetchall():
                print("{:<4} {:<25} {:<20}".format(row[0], row[1], row[2]))

        elif choice == '8':
            cursor.execute("SELECT * FROM Contract")
            print("\n{:<15} {:<15} {:<50} {:<15}".format("Contract ID", "Company ID", "Description", "Date"))
            print()
            for row in cursor.fetchall():
                print("{:<15} {:<15} {:<50} {:<15}".format(row[0], row[1], row[3], row[4]))

        elif choice == '9':
            cursor.execute("SELECT * FROM Chemical")
            print("\n{:<4} {:<30} {:<8}".format("ID", "Chemical Name", "Hazard"))
            print()
            for row in cursor.fetchall():
                status = "HARMFUL" if row[2] > 0 else "Safe"
                print("{:<4} {:<30} {:<8}".format(row[0], row[1], row[2]))
                
        elif choice == '10':
            cursor.execute("""
                SELECT cu.usage_id, c.chemical_name, a.description, cu.quantity_used
                FROM chemical_usage cu
                JOIN chemical c ON cu.chemical_id = c.chemical_id
                JOIN activity a ON cu.activity_id = a.activity_id
            """)
            print("\n{:<4} {:<20} {:<35} {:<8}".format("ID", "Chemical", "Used In Activity", "Quantity"))
            print()
            for row in cursor.fetchall():
                print("{:<4} {:<20} {:<35} {:<8}".format(row[0], row[1][:19], row[2][:34], row[3]))
                
        elif choice == '11':
            searchCleaningActivities()

        print()
        quit = input("Quit? (y/n): ").strip().lower()
        if quit == 'y':
            break
        
        conn.close()

def run_sql():
    while True:
        print()
        print("Input SQL queries in one line only to run.")
        query = get_input("Input SQL: ")

        if query is None:
            return
        
        elif not query.lstrip().upper().startswith("SELECT"):
            print("Invalid query")
            continue
        
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            title = [description[0] for description in cursor.description]
            print()
            print("\t".join(title))
            print()
            for row in rows:
                for data in row:
                    value = str(data)
                    print(f"{value:20}", end=" ")
                print()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            connect.close()
        
        exit_choice = get_input("\nExit to main menu? (y/n): ")
        if exit_choice and exit_choice.lower() == 'y':
            return
             
def searchCleaningActivities():
    startDate = get_input("Enter start date (YYYY-MM-DD): ")
    if startDate is None: return
    startDate = startDate.strip()
    
    endDate = get_input("Enter end date (YYYY-MM-DD): ")
    if endDate is None: return
    endDate = endDate.strip()
    
    building = get_input("Enter building name: ")
    if building is None: return
    building = building.strip()
    
    if startDate > endDate or not startDate or not endDate or not building:
        print("Invalid date")
        return
    
    connect = get_connection()
    cursor = connect.cursor()

    sql = """
    SELECT 
        a.description,
        a.start_date,
        MAX(COALESCE(c.hazard_level, 0)) AS max_hazard
    FROM activity a
    JOIN location l ON a.location_id = l.location_id
    LEFT JOIN chemical_usage cu ON a.activity_id = cu.activity_id
    LEFT JOIN chemical c ON cu.chemical_id = c.chemical_id
    WHERE LOWER(a.activity_type) = 'cleaning'
    AND l.location_name = ?
    AND a.start_date BETWEEN ? AND ?
    GROUP BY a.activity_id, a.description, a.start_date
    ORDER BY a.start_date
    """
    cursor.execute(sql, (building, startDate, endDate))
    rows = cursor.fetchall()
    if not rows:
        print()
        print("No cleaning activities found in the given period.")
        connect.close()
        return
        
    print()
    print(f"Found {len(rows)} cleaning activities for {building}:")
    print("-" * 70)
    for description, start_date, max_hazard in rows:
        hazard = int(max_hazard) if max_hazard else 0
        print()
        print(f"Description: {description}")
        print(f"Start Date: {start_date}")
        if hazard > 0:
            print("⚠ Warning: Harmful chemicals used!")
        else:
            print("✓ No harmful chemicals used.")
                
    connect.close()

def generate_reports():
    print("\n=== Generate Reports ===")
    print("1. Worker Activity Summary")
    print("2. Activity Type Distribution by Location")
    print("3. Chemical Usage Report")
    print("4. Building Maintenance Overview")
    print("5. Employee Workload Analysis")
    print("6. Activity Status Summary")
    print("7. External Company Contract Report")
    print("8. Manager Supervision Overview")
    print("9. Hazardous Chemical Activities Report")
    print("10. Monthly Activity Trends")

    choice = get_input("Choose report: ")
    
    if choice is None:
        return

    # Validate choice
    valid_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    if choice not in valid_choices:
        print("Invalid choice. Please select 1-10.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if choice == '1':
        # Report 1: Worker Activity Summary - Number of workers performing various types of activities
        print("\n=== Worker Activity Summary ===")
        cursor.execute("""
            SELECT 
                a.activity_type,
                COUNT(DISTINCT ass.employee_id) as worker_count,
                COUNT(ass.assignment_id) as total_assignments
            FROM activity a
            LEFT JOIN assignment ass ON a.activity_id = ass.activity_id
            LEFT JOIN employee e ON ass.employee_id = e.employee_id
            WHERE e.employee_type = 'worker' OR e.employee_type IS NULL
            GROUP BY a.activity_type
            ORDER BY worker_count DESC
        """)
        
        print(f"\n{'Activity Type':<20} {'Workers':<15} {'Assignments':<15}")
        print("-" * 50)
        for row in cursor.fetchall():
            activity_type, worker_count, assignments = row
            print(f"{activity_type:<20} {worker_count:<15} {assignments:<15}")
    
    elif choice == '2':
        # Report 2: Activity Type Distribution by Location
        print("\n=== Activity Type Distribution by Location ===")
        cursor.execute("""
            SELECT 
                l.location_type,
                l.location_name,
                a.activity_type,
                COUNT(*) as activity_count
            FROM activity a
            JOIN location l ON a.location_id = l.location_id
            GROUP BY l.location_type, l.location_name, a.activity_type
            ORDER BY l.location_type, activity_count DESC
        """)
        
        print(f"\n{'Location Type':<15} {'Location Name':<25} {'Activity Type':<15} {'Count':<10}")
        print("-" * 70)
        for row in cursor.fetchall():
            loc_type, loc_name, act_type, count = row
            print(f"{loc_type:<15} {loc_name:<25} {act_type:<15} {count:<10}")
    
    elif choice == '3':
        # Report 3: Chemical Usage Report
        print("\n=== Chemical Usage Report ===")
        cursor.execute("""
            SELECT 
                c.chemical_name,
                c.hazard_level,
                COUNT(cu.usage_id) as usage_count,
                SUM(cu.quantity_used) as total_quantity
            FROM chemical c
            LEFT JOIN chemical_usage cu ON c.chemical_id = cu.chemical_id
            GROUP BY c.chemical_id, c.chemical_name, c.hazard_level
            ORDER BY c.hazard_level DESC, total_quantity DESC
        """)
        
        print(f"\n{'Chemical Name':<30} {'Hazard Level':<15} {'Times Used':<15} {'Total Qty':<15}")
        print("-" * 80)
        for row in cursor.fetchall():
            chem_name, hazard, usage_count, total_qty = row
            total_qty = total_qty if total_qty else 0
            print(f"{chem_name:<30} {hazard:<15} {usage_count:<15} {total_qty:<15}")
    
    elif choice == '4':
        # Report 4: Building Maintenance Overview
        print("\n=== Building Maintenance Overview ===")
        cursor.execute("""
            SELECT 
                b.building_name,
                COUNT(DISTINCT a.activity_id) as total_activities,
                COUNT(DISTINCT CASE WHEN a.activity_type = 'cleaning' THEN a.activity_id END) as cleaning_count,
                COUNT(DISTINCT CASE WHEN a.activity_type = 'maintenance' THEN a.activity_id END) as maintenance_count,
                COUNT(DISTINCT CASE WHEN a.activity_type = 'renovation' THEN a.activity_id END) as renovation_count,
                COUNT(DISTINCT bs.manager_id) as assigned_managers
            FROM building b
            LEFT JOIN location l ON b.building_name = l.location_name AND l.location_type = 'building'
            LEFT JOIN activity a ON l.location_id = a.location_id
            LEFT JOIN building_supervision bs ON b.building_id = bs.building_id
            GROUP BY b.building_id, b.building_name
            ORDER BY total_activities DESC
        """)
        
        print(f"\n{'Building':<25} {'Total':<10} {'Cleaning':<12} {'Maintenance':<14} {'Renovation':<12} {'Managers':<10}")
        print("-" * 90)
        for row in cursor.fetchall():
            building, total, cleaning, maintenance, renovation, managers = row
            print(f"{building:<25} {total:<10} {cleaning:<12} {maintenance:<14} {renovation:<12} {managers:<10}")
    
    elif choice == '5':
        # Report 5: Employee Workload Analysis
        print("\n=== Employee Workload Analysis ===")
        cursor.execute("""
            SELECT 
                e.employee_id,
                e.name,
                e.employee_type,
                COUNT(ass.assignment_id) as assignment_count,
                COUNT(DISTINCT ass.activity_id) as unique_activities
            FROM employee e
            LEFT JOIN assignment ass ON e.employee_id = ass.employee_id
            GROUP BY e.employee_id, e.name, e.employee_type
            HAVING assignment_count > 0
            ORDER BY assignment_count DESC, e.employee_type
        """)
        
        print(f"\n{'ID':<5} {'Name':<25} {'Type':<12} {'Assignments':<15} {'Unique Activities':<20}")
        print("-" * 80)
        for row in cursor.fetchall():
            emp_id, name, emp_type, assign_count, unique_act = row
            print(f"{emp_id:<5} {name:<25} {emp_type:<12} {assign_count:<15} {unique_act:<20}")
    
    elif choice == '6':
        # Report 6: Activity Status Summary
        print("\n=== Activity Status Summary ===")
        cursor.execute("""
            SELECT 
                a.status,
                a.activity_type,
                COUNT(*) as count
            FROM activity a
            GROUP BY a.status, a.activity_type
            ORDER BY a.status, count DESC
        """)
        
        print(f"\n{'Status':<20} {'Activity Type':<20} {'Count':<10}")
        print("-" * 50)
        for row in cursor.fetchall():
            status, act_type, count = row
            print(f"{status:<20} {act_type:<20} {count:<10}")
        
        # Overall summary
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as total
            FROM activity
            GROUP BY status
        """)
        print(f"\n{'Status':<20} {'Total':<10}")
        print("-" * 30)
        for row in cursor.fetchall():
            status, total = row
            print(f"{status:<20} {total:<10}")
    
    elif choice == '7':
        # Report 7: External Company Contract Report
        print("\n=== External Company Contract Report ===")
        cursor.execute("""
            SELECT 
                ec.company_name,
                ec.specialization,
                COUNT(c.contract_id) as contract_count,
                COUNT(DISTINCT a.activity_type) as activity_types
            FROM external_company ec
            LEFT JOIN contract c ON ec.company_id = c.company_id
            LEFT JOIN activity a ON c.activity_id = a.activity_id
            GROUP BY ec.company_id, ec.company_name, ec.specialization
            ORDER BY contract_count DESC
        """)
        
        print(f"\n{'Company Name':<30} {'Specialization':<30} {'Contracts':<12} {'Activity Types':<15}")
        print("-" * 90)
        for row in cursor.fetchall():
            company, spec, contracts, act_types = row
            print(f"{company:<30} {spec:<30} {contracts:<12} {act_types:<15}")
    
    elif choice == '8':
        # Report 8: Manager Supervision Overview
        print("\n=== Manager Supervision Overview ===")
        cursor.execute("""
            SELECT 
                e.employee_id,
                e.name,
                COUNT(DISTINCT bs.building_id) as buildings_supervised,
                COUNT(DISTINCT a.activity_id) as activities_managed,
                COUNT(DISTINCT sub.employee_id) as subordinates
            FROM employee e
            LEFT JOIN building_supervision bs ON e.employee_id = bs.manager_id
            LEFT JOIN activity a ON e.employee_id = a.manager_id
            LEFT JOIN employee sub ON e.employee_id = sub.supervisor_id
            WHERE e.employee_type = 'manager'
            GROUP BY e.employee_id, e.name
            ORDER BY activities_managed DESC
        """)
        
        print(f"\n{'ID':<5} {'Manager Name':<25} {'Buildings':<12} {'Activities':<12} {'Subordinates':<15}")
        print("-" * 70)
        for row in cursor.fetchall():
            mgr_id, name, buildings, activities, subs = row
            print(f"{mgr_id:<5} {name:<25} {buildings:<12} {activities:<12} {subs:<15}")
    
    elif choice == '9':
        # Report 9: Hazardous Chemical Activities Report
        print("\n=== Hazardous Chemical Activities Report ===")
        cursor.execute("""
            SELECT 
                a.activity_id,
                a.activity_type,
                a.description,
                l.location_name,
                c.chemical_name,
                c.hazard_level,
                cu.quantity_used
            FROM activity a
            JOIN chemical_usage cu ON a.activity_id = cu.activity_id
            JOIN chemical c ON cu.chemical_id = c.chemical_id
            JOIN location l ON a.location_id = l.location_id
            WHERE c.hazard_level >= 2
            ORDER BY c.hazard_level DESC, a.start_date
        """)
        
        print(f"\n{'Act ID':<8} {'Type':<15} {'Location':<20} {'Chemical':<25} {'Hazard':<10} {'Qty':<10}")
        print("-" * 95)
        for row in cursor.fetchall():
            act_id, act_type, desc, location, chem, hazard, qty = row
            print(f"{act_id:<8} {act_type:<15} {location:<20} {chem:<25} {hazard:<10} {qty:<10}")
    
    elif choice == '10':
        # Report 10: Monthly Activity Trends
        print("\n=== Monthly Activity Trends ===")
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', a.start_date) as month,
                a.activity_type,
                COUNT(*) as activity_count
            FROM activity a
            WHERE a.start_date IS NOT NULL
            GROUP BY month, a.activity_type
            ORDER BY month DESC, activity_count DESC
        """)
        
        print(f"\n{'Month':<15} {'Activity Type':<20} {'Count':<10}")
        print("-" * 50)
        for row in cursor.fetchall():
            month, act_type, count = row
            print(f"{month:<15} {act_type:<20} {count:<10}")
    
    else:
        print("Invalid choice.")
    
    conn.close()
    print("\n" + "="*50)
    
    # Ask if user wants to generate another report
    exit_choice = get_input("\nExit to main menu? (y/n): ")
    if exit_choice and exit_choice.lower() != 'y':
        generate_reports()

if __name__ == "__main__":
    main()