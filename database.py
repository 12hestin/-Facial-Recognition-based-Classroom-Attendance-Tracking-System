import sqlite3
import hashlib

TEACHERS_DATABASE = 'teachers.db'
STUDENTS_DATABASE = 'students.db'
SUBJECTS_DATABASE = 'subjects.db'
TEACHER_PASSWORDS_DATABASE = 'teacher_passwords.db'
STUDENT_PASSWORD_DATABASE = 'student_passwords.db'

def get_teachers_db():
    db = sqlite3.connect(TEACHERS_DATABASE)
    return db

def get_students_db():
    db = sqlite3.connect(STUDENTS_DATABASE)
    return db

def get_subjects_db():
    db = sqlite3.connect(SUBJECTS_DATABASE)
    return db

def get_teacher_passwords_db():
    db = sqlite3.connect(TEACHER_PASSWORDS_DATABASE)
    return db

def get_student_passwords_db():
    db = sqlite3.connect(STUDENT_PASSWORD_DATABASE)
    return db

def close_db(db):
    db.close()

def init_teachers_db():
    db = get_teachers_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL
                     )''')
    db.commit()
    close_db(db)

def init_students_db():
    db = get_students_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL,
                        semester TEXT NOT NULL,
                        department TEXT NOT NULL
                     )''')
    db.commit()
    close_db(db)

def init_subjects_db():
    db = get_subjects_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        teacher_username TEXT,
                        FOREIGN KEY (teacher_username) REFERENCES teachers(username)
                     )''')
    db.commit()
    close_db(db)
    
    
def init_teacher_passwords_db():
    db = get_teacher_passwords_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS teacher_passwords (
                        username TEXT PRIMARY KEY,
                        password_hash TEXT NOT NULL
                     )''')
    db.commit()
    close_db(db)    
    
def init_student_passwords_db():
    db = get_student_passwords_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_passwords (
                        username TEXT PRIMARY KEY,
                        password_hash TEXT NOT NULL
                     )''')
    db.commit()
    close_db(db) 
    

def insert_teacher(name, username):
    db = get_teachers_db()
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM teachers")
    max_id = cursor.fetchone()[0]
    new_id = max_id + 1 if max_id else 1 
    cursor.execute("INSERT INTO teachers (id, name, username) VALUES (?, ?, ?)", (new_id, name, username))
    db.commit()
    close_db(db)

def insert_student(name, username, semester, department):
    db = get_students_db()
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM students")
    max_id = cursor.fetchone()[0]
    new_id = max_id + 1 if max_id else 1
    cursor.execute("INSERT INTO students (id, name, username, semester, department) VALUES (?, ?, ?, ?, ?)",
                   (new_id, name, username, semester, department))
    db.commit()
    close_db(db)

def insert_subject(name, teacher_username):
    db = get_subjects_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO subjects (name, teacher_username) VALUES (?, ?)", (name, teacher_username))
    db.commit()
    close_db(db)

def is_username_assigned_to_teacher(username):
    db = get_teachers_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM teachers WHERE username = ?", (username,))
    data = cursor.fetchone()
    close_db(db)
    return data is not None

def is_username_assigned_to_student(username):
    db = get_students_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE username = ?", (username,))
    data = cursor.fetchone()
    close_db(db)
    return data is not None

def is_subject_assigned_to_other_teacher(subject_name, teacher_username):
    db = get_subjects_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM subjects WHERE name = ? AND teacher_username != ?", (subject_name, teacher_username))
    data = cursor.fetchone()
    close_db(db)
    return data is not None

def get_teacher_password(username):
    db = get_teacher_passwords_db()
    cursor = db.cursor()
    cursor.execute("SELECT password_hash FROM teacher_passwords WHERE username = ?", (username,))
    data = cursor.fetchone()
    close_db(db)
    if data:
        return data[0]
    else:
        return None

def set_teacher_password(username, password):
    db = get_teacher_passwords_db()
    cursor = db.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT OR REPLACE INTO teacher_passwords (username, password_hash) VALUES (?, ?)", (username, password_hash))
    db.commit()
    close_db(db)
    
def verify_teacher_password(username, password):
    stored_password_hash = get_teacher_password(username)
    if stored_password_hash:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == stored_password_hash
    else:
        return False
    
def get_student_password(username):
    db = get_student_passwords_db()
    cursor = db.cursor()
    cursor.execute("SELECT password_hash FROM student_passwords WHERE username = ?", (username,))
    data = cursor.fetchone()
    close_db(db)
    if data:
        return data[0]
    else:
        return None

def set_student_password(username, password):
    db = get_student_passwords_db()
    cursor = db.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT OR REPLACE INTO student_passwords (username, password_hash) VALUES (?, ?)", (username, password_hash))
    db.commit()
    close_db(db)
    
def verify_student_password(username, password):
    stored_password_hash = get_student_password(username)
    if stored_password_hash:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == stored_password_hash
    else:
        return False  
   
def get_all_students():
    db = get_students_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    close_db(db)
    return students

def delete_student_by_id(student_id):
    db = get_students_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    cursor.execute("UPDATE students SET id = id - 1 WHERE id > ?", (student_id,))
    db.commit()

    close_db(db)
   
def get_subjects_with_teachers():
    db = get_subjects_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, COALESCE(teacher_username, 'NO SUBJECT') FROM subjects")
    subjects = cursor.fetchall()
    close_db(db)
    return subjects

def delete_subject_from_db(subject_name, teacher_username):
    db = get_subjects_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM subjects WHERE name = ? AND teacher_username = ?", (subject_name, teacher_username))
    db.commit()
    close_db(db)

def get_all_teachers():
    db = get_teachers_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM teachers")
    teachers = cursor.fetchall()
    close_db(db)
    return teachers

def delete_teacher_by_id(teacher_id):
    db = get_teachers_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    db.commit()

    cursor.execute("UPDATE teachers SET id = id - 1 WHERE id > ?", (teacher_id,))
    db.commit()

    close_db(db)
    
def fetch_attendance_data(database_path, teacher_username):
    conn_attendance = sqlite3.connect(database_path)
    c_attendance = conn_attendance.cursor()
    c_attendance.execute('''SELECT student_id, classes_present, attendance_percentage FROM Attendance ORDER BY student_id ASC''')
    attendance_data = c_attendance.fetchall()

    # Close the attendance database connection
    conn_attendance.close()

    # Connect to the students database and fetch all students
    conn_students = sqlite3.connect('students.db')
    c_students = conn_students.cursor()
    c_students.execute('''SELECT username FROM students''')
    all_students = c_students.fetchall()

    # Close the students database connection
    conn_students.close()

    # Convert fetched attendance data to a set for efficient lookup
    present_students = set(row[0] for row in attendance_data)

    # Iterate over all students and add those not present in attendance data with default values
    for student_username in all_students:
        student_username = student_username[0]  # Extract the username from the tuple
        if student_username not in present_students:
            attendance_data.append((student_username, 0, 0))  # Add default values

    # Sort the attendance data by student_id (username)
    attendance_data.sort(key=lambda x: x[0])

    return attendance_data

def update_classes_present_in_database(database_path, student_id, classes_present):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Check if the student already exists in the Attendance table
    c.execute('''SELECT * FROM Attendance WHERE student_id = ?''', (student_id,))
    student_data = c.fetchone()

    if student_data:
        # Update classes_present for the student
        c.execute('''UPDATE Attendance SET classes_present = ? WHERE student_id = ?''',
                  (classes_present, student_id))
    else:
        # Insert the student with classes_present and attendance_percentage as 0
        c.execute('''INSERT INTO Attendance (student_id, classes_present, attendance_percentage)
                     VALUES (?, ?, 0)''', (student_id, classes_present))

    # Recalculate attendance percentage for all students
    total_classes_taken_query = '''SELECT SUM(classes_taken) FROM ClassesTaken'''
    c.execute(total_classes_taken_query)
    total_classes_taken = c.fetchone()[0] or 1  # Avoid division by zero

    update_attendance_query = '''UPDATE Attendance SET attendance_percentage = (classes_present / ?) * 100'''
    c.execute(update_attendance_query, (total_classes_taken,))

    conn.commit()
    conn.close()

def get_student_attendance(database_path, student_username):
    # Connect to the specified database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Retrieve the attendance percentage for the student from the Attendance table
    cursor.execute("SELECT attendance_percentage FROM Attendance WHERE student_id = ?", (student_username,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None
    
def get_total_classes_taken(database_path, teacher_username):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    c.execute('''SELECT classes_taken FROM ClassesTaken WHERE teacher_name = ?''', (teacher_username,))
    result = c.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return 0  # Return 0 if no classes taken yet


def get_teacher_subject_map():
    return {
        "teacher01": {"subject": "DCC", "database": "dcc_attendance.db"},
        "teacher02": {"subject": "IEFT", "database": "ieft_attendance.db"},
        "teacher03": {"subject": "CD", "database": "cd_attendance.db"},
        "teacher04": {"subject": "AAD", "database": "aad_attendance.db"},
        "teacher05": {"subject": "CGIP", "database": "cgip_attendance.db"},
    }

