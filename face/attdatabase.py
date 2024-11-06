import sqlite3

# Function to initialize subject databases
def initialize_subject_databases(teacher_subject_map):
    for teacher_name, data in teacher_subject_map.items():
        database_name = data["database"]
        conn = sqlite3.connect(database_name)
        c = conn.cursor()

        # Create a table to track teacher's classes taken
        c.execute('''CREATE TABLE IF NOT EXISTS ClassesTaken
                     (teacher_name TEXT, subject TEXT, classes_taken REAL)''')

        # Create a table to track student attendance
        c.execute('''CREATE TABLE IF NOT EXISTS Attendance
                     (student_id TEXT, classes_present REAL, attendance_percentage REAL)''')

        conn.commit()
        conn.close()

# Function to insert teacher's classes taken
def insert_classes_taken(database_path, teacher_name, subject):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Check if the teacher already exists in the table
    c.execute('''SELECT classes_taken FROM ClassesTaken WHERE teacher_name = ? AND subject = ?''', (teacher_name, subject))
    result = c.fetchone()

    if result:
        # If teacher exists, update the classes_taken count
        classes_taken = result[0] + 1
        c.execute('''UPDATE ClassesTaken SET classes_taken = ? WHERE teacher_name = ? AND subject = ?''',
                  (classes_taken, teacher_name, subject))
    else:
        # If teacher doesn't exist, insert a new row
        c.execute('''INSERT INTO ClassesTaken (teacher_name, subject, classes_taken) VALUES (?, ?, 1)''',
                  (teacher_name, subject))

    conn.commit()
    conn.close()

# Function to insert student attendance and update percentage
def insert_attendance(database_path, student_id):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Update classes_present for the student
    c.execute('''SELECT classes_present FROM Attendance WHERE student_id = ?''', (student_id,))
    result = c.fetchone()

    if result:
        classes_present = result[0] + 1
        c.execute('''UPDATE Attendance SET classes_present = ? WHERE student_id = ?''',
                  (classes_present, student_id))
    else:
        c.execute('''INSERT INTO Attendance (student_id, classes_present) VALUES (?, 1)''', (student_id,))

    # Calculate and update attendance percentage
    c.execute('''SELECT SUM(classes_taken) FROM ClassesTaken''')  # Sum of all classes taken by teachers
    total_classes_taken = c.fetchone()[0] or 1  # Avoid division by zero

    c.execute('''UPDATE Attendance SET attendance_percentage = (classes_present / ?) * 100''',
              (total_classes_taken,))

    conn.commit()
    conn.close()