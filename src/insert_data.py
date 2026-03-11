"""
Template for inserting data - ADD YOUR OWN DATA HERE
"""
from database import get_connection, setup_database

def insert_data():
    setup_database()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert Employees (Executives first, then Managers, then Workers)
    print("Inserting employees...")
    
    # Executives (no supervisor)
    cursor.execute("""
        INSERT INTO employee (name, employee_type, supervisor_id)
        VALUES 
            ('John Smith', 'executive', NULL),
            ('Sarah Johnson', 'executive', NULL)
    """)
    
    # Managers (supervised by executives)
    cursor.execute("""
        INSERT INTO employee (name, employee_type, supervisor_id)
        VALUES 
            ('Michael Chen', 'manager', 1),
            ('Emily Davis', 'manager', 1),
            ('Robert Wilson', 'manager', 2),
            ('Lisa Anderson', 'manager', 2),
            ('David Martinez', 'manager', 1)
    """)
    
    # Workers (supervised by managers)
    cursor.execute("""
        INSERT INTO employee (name, employee_type, supervisor_id)
        VALUES 
            ('James Brown', 'worker', 3),
            ('Maria Garcia', 'worker', 3),
            ('William Taylor', 'worker', 4),
            ('Jennifer Thomas', 'worker', 4),
            ('Richard Moore', 'worker', 5),
            ('Patricia Jackson', 'worker', 5),
            ('Charles White', 'worker', 6),
            ('Linda Harris', 'worker', 6),
            ('Joseph Martin', 'worker', 7),
            ('Barbara Thompson', 'worker', 7),
            ('Thomas Garcia', 'worker', 3),
            ('Susan Martinez', 'worker', 4),
            ('Daniel Robinson', 'worker', 5),
            ('Jessica Clark', 'worker', 6),
            ('Matthew Rodriguez', 'worker', 7)
    """)
    
    # Insert Employee Contacts
    print("Inserting employee contacts...")
    cursor.execute("""
        INSERT INTO employee_contact (employee_id, phone, email, emergency_contact)
        VALUES 
            (1, '852-9123-4567', 'john.smith@campus.edu', '852-9123-9999'),
            (2, '852-9123-4568', 'sarah.johnson@campus.edu', '852-9123-9998'),
            (3, '852-9123-4569', 'michael.chen@campus.edu', '852-9123-9997'),
            (4, '852-9123-4570', 'emily.davis@campus.edu', '852-9123-9996'),
            (5, '852-9123-4571', 'robert.wilson@campus.edu', '852-9123-9995'),
            (6, '852-9123-4572', 'lisa.anderson@campus.edu', '852-9123-9994'),
            (7, '852-9123-4573', 'david.martinez@campus.edu', '852-9123-9993'),
            (8, '852-9234-5678', 'james.brown@campus.edu', '852-9234-9999'),
            (9, '852-9234-5679', 'maria.garcia@campus.edu', '852-9234-9998'),
            (10, '852-9234-5680', 'william.taylor@campus.edu', '852-9234-9997'),
            (11, '852-9234-5681', 'jennifer.thomas@campus.edu', '852-9234-9996'),
            (12, '852-9234-5682', 'richard.moore@campus.edu', '852-9234-9995'),
            (13, '852-9234-5683', 'patricia.jackson@campus.edu', '852-9234-9994'),
            (14, '852-9234-5684', 'charles.white@campus.edu', '852-9234-9993'),
            (15, '852-9234-5685', 'linda.harris@campus.edu', '852-9234-9992')
    """)
    
    # Insert Buildings
    print("Inserting buildings...")
    cursor.execute("""
        INSERT INTO building (building_name)
        VALUES 
            ('Academic Building A'),
            ('Academic Building B'),
            ('Science Complex'),
            ('Engineering Hall'),
            ('Student Center'),
            ('Library Tower'),
            ('Administration Building')
    """)
    
    # Insert Rooms
    print("Inserting rooms...")
    cursor.execute("""
        INSERT INTO room (building_id, room_id, room_type)
        VALUES 
            (1, 101, 'classroom'),
            (1, 102, 'classroom'),
            (1, 201, 'office'),
            (1, 202, 'conference'),
            (2, 101, 'classroom'),
            (2, 102, 'laboratory'),
            (2, 201, 'office'),
            (3, 101, 'laboratory'),
            (3, 102, 'laboratory'),
            (3, 103, 'laboratory'),
            (3, 201, 'storage'),
            (4, 101, 'classroom'),
            (4, 102, 'laboratory'),
            (4, 201, 'office'),
            (5, 101, 'conference'),
            (5, 102, 'restroom'),
            (6, 101, 'office'),
            (6, 201, 'storage'),
            (7, 101, 'office'),
            (7, 102, 'conference')
    """)
    
    # Insert Outdoor Areas
    print("Inserting outdoor areas...")
    cursor.execute("""
        INSERT INTO outdoor_area (area_name, area_type)
        VALUES 
            ('Main Gate', 'gate'),
            ('Central Plaza', 'square'),
            ('East Parking', 'parking_lot'),
            ('West Parking', 'parking_lot'),
            ('Rose Garden', 'garden'),
            ('Football Field', 'sports_field'),
            ('Basketball Court', 'sports_field')
    """)
    
    # Insert Building into Locations
    cursor.execute("""
        INSERT INTO location (location_type, building_id, location_name)
        VALUES 
            ('building', 1, 'Academic Building A'),
            ('building', 2, 'Academic Building B'),
            ('building', 3, 'Science Complex'),
            ('building', 4, 'Engineering Hall'),
            ('building', 5, 'Student Center')
    """)

    # Insert Outdoor Area into Locations
    cursor.execute("""
        INSERT INTO location (location_type, outdoor_area_id, location_name)
        VALUES 
            ('outdoor_area', 1, 'Main Gate'),
            ('outdoor_area', 2, 'Central Plaza'),
            ('outdoor_area', 3, 'East Parking'),
            ('outdoor_area', 4, 'Rose Garden'),
            ('outdoor_area', 5, 'Football Field')
    """)
    
    # Insert Room into Locations
    cursor.execute("""
        INSERT INTO location (location_type, room_building_id, room_id, location_name)
        VALUES 
            ('room', 1, 101, 'Room A-101'),
            ('room', 1, 102, 'Room A-102'),
            ('room', 3, 101, 'Lab S-101'),
            ('room', 3, 102, 'Lab S-102')
    """)

    # Insert External Companies
    print("Inserting external companies...")
    cursor.execute("""
        INSERT INTO external_company (company_name, specialization, contact_info)
        VALUES 
            ('CleanPro Services', 'Industrial Cleaning', 'cleanpro@service.com, 852-8888-1111'),
            ('BuildTech Construction', 'Renovation & Construction', 'info@buildtech.com, 852-8888-2222'),
            ('GreenScape Landscaping', 'Garden Maintenance', 'contact@greenscape.com, 852-8888-3333'),
            ('TechFix Solutions', 'Equipment Repair', 'support@techfix.com, 852-8888-4444'),
            ('SafeChem Suppliers', 'Chemical Supply & Management', 'sales@safechem.com, 852-8888-5555')
    """)
    
    # Insert Chemicals
    print("Inserting chemicals...")
    cursor.execute("""
        INSERT INTO chemical (chemical_name, hazard_level)
        VALUES 
            ('Multi-Surface Cleaner', 0),
            ('Glass Cleaner', 0),
            ('Floor Wax', 1),
            ('Disinfectant Spray', 1),
            ('Bleach Solution', 2),
            ('Industrial Degreaser', 2),
            ('Paint Thinner', 3),
            ('Pesticide', 3)
    """)
    
    # Insert Activities
    print("Inserting activities...")
    cursor.execute("""
        INSERT INTO activity (activity_type, location_id, description, start_date, end_date, status, manager_id)
        VALUES 
            ('cleaning', 11, 'Daily classroom cleaning', '2025-01-05', '2025-01-05', 'Completed', 3),
            ('cleaning', 13, 'Deep cleaning of lecture hall', '2025-01-10', '2025-01-11', 'Completed', 3),
            ('cleaning', 9, 'Plaza power washing', '2025-01-15', '2025-01-16', 'Completed', 4),
            ('maintenance', 12, 'Laboratory equipment check', '2025-02-01', '2025-02-03', 'Completed', 5),
            ('repair', 14, 'Fix broken lab equipment', '2025-02-10', '2025-02-12', 'In Progress', 5),
            ('renovation', 1, 'Building A renovation', '2025-03-01', '2025-05-30', 'Scheduled', 6),
            ('cleaning', 8, 'Parking lot maintenance', '2025-02-20', '2025-02-21', 'Completed', 4),
            ('maintenance', 10, 'Garden trimming and care', '2025-02-15', '2025-02-16', 'Completed', 7),
            ('cleaning', 6, 'Sports field cleaning', '2025-02-25', '2025-02-25', 'Scheduled', 4),
            ('weather-related', 6, 'Gate repair after storm', '2025-01-20', '2025-01-22', 'Completed', 6),
            ('cleaning', 1, 'Regular building cleaning', '2025-01-05', '2025-01-05', 'Completed', 3),
            ('cleaning', 1, 'Scheduled maintenance cleaning Academic Building A', '2025-01-08', '2025-01-08', 'Scheduled', 3),
            ('cleaning', 2, 'Scheduled cleaning Academic Building B', '2025-01-10', '2025-01-10', 'Scheduled', 3),
            ('cleaning', 3, 'Science Complex deep cleaning', '2025-03-01', '2025-03-02', 'Scheduled', 4),
            ('cleaning', 4, 'Engineering Hall scheduled cleaning', '2025-01-06', '2025-01-06', 'Scheduled', 4)
    """)
    
    # Insert Chemical Usage
    print("Inserting chemical usage...")
    cursor.execute("""
        INSERT INTO chemical_usage (chemical_id, activity_id, quantity_used, usage_reasons)
        VALUES 
            (1, 1, 2, 'Surface cleaning of desks and chairs'),
            (2, 1, 1, 'Window cleaning'),
            (4, 2, 3, 'Disinfection of high-touch surfaces'),
            (5, 2, 2, 'Deep sanitization'),
            (6, 3, 5, 'Heavy-duty plaza cleaning'),
            (1, 7, 3, 'General parking lot cleaning'),
            (4, 9, 2, 'Sanitization of sports equipment'),
            (8, 8, 1, 'Pest control in garden area')
    """)
    
    # Insert Building Supervision
    print("Inserting building supervision...")
    cursor.execute("""
        INSERT INTO building_supervision (manager_id, building_id, assigned_date)
        VALUES 
            (3, 1, '2025-01-01'),
            (3, 2, '2025-01-01'),
            (4, 3, '2025-01-01'),
            (5, 4, '2025-01-01'),
            (6, 5, '2025-01-01'),
            (7, 6, '2025-01-01'),
            (7, 7, '2025-01-01')
    """)
    
    # Insert Assignments
    print("Inserting assignments...")
    cursor.execute("""
        INSERT INTO assignment (employee_id, activity_id, start_date, due_date, description)
        VALUES 
            (8, 1, '2025-01-05', '2025-01-05', 'Clean classroom A-101'),
            (9, 1, '2025-01-05', '2025-01-05', 'Assist with classroom cleaning'),
            (8, 2, '2025-01-10', '2025-01-11', 'Deep clean lecture hall'),
            (9, 2, '2025-01-10', '2025-01-11', 'Assist with deep cleaning'),
            (10, 3, '2025-01-15', '2025-01-16', 'Power wash central plaza'),
            (11, 3, '2025-01-15', '2025-01-16', 'Assist with plaza cleaning'),
            (12, 4, '2025-02-01', '2025-02-03', 'Check laboratory equipment'),
            (13, 4, '2025-02-01', '2025-02-03', 'Document equipment status'),
            (12, 5, '2025-02-10', '2025-02-12', 'Repair lab equipment'),
            (14, 7, '2025-02-20', '2025-02-21', 'Clean parking lot'),
            (15, 8, '2025-02-15', '2025-02-16', 'Garden maintenance work'),
            (16, 9, '2025-02-25', '2025-02-25', 'Prepare sports field'),
            (17, 10, '2025-01-20', '2025-01-22', 'Repair main gate')
    """)
    
    # Insert Contracts
    print("Inserting contracts...")
    cursor.execute("""
        INSERT INTO contract (company_id, activity_id, contract_description, contract_date)
        VALUES 
            (1, 2, 'Deep cleaning service contract for lecture halls', '2025-01-08'),
            (2, 6, 'Major renovation contract for Academic Building A', '2025-02-25'),
            (3, 8, 'Garden maintenance and landscaping contract', '2025-02-10'),
            (4, 5, 'Laboratory equipment repair service', '2025-02-08'),
            (5, 2, 'Chemical supply for deep cleaning', '2025-01-08')
    """)
    
    conn.commit()
    conn.close()
    print("Data insertion complete! Database populated with test data.")
    print("\nData Summary:")
    print("- 22 Employees (2 Executives, 5 Managers, 15 Workers)")
    print("- 7 Buildings with 20 Rooms")
    print("- 7 Outdoor Areas")
    print("- 14 Locations")
    print("- 5 External Companies")
    print("- 8 Chemicals")
    print("- 10 Activities")
    print("- 8 Chemical Usage Records")
    print("- 7 Building Supervision Assignments")
    print("- 13 Worker Assignments")
    print("- 5 Contracts")

if __name__ == "__main__":
    insert_data()
