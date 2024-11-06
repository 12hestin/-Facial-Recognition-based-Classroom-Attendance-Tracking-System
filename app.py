import os
from flask import Flask, flash, render_template, request, redirect, url_for, session
from database import *

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Predefined admin username and password
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"
ADMIN_ASSIGNED_USERNAME = "admin"


# Initialize databases
init_teachers_db()
init_students_db()
init_subjects_db()
init_teacher_passwords_db()
init_student_passwords_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']
        if user_type == 'Admin':
            return redirect(url_for('admin_login'))
        elif user_type == 'Student':
            return redirect(url_for('student_login'))
        elif user_type == 'Teacher':
            return redirect(url_for('teacher_login'))
    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Redirect to admin dashboard upon successful login
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid username or password"
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')


@app.route('/assign_teacher', methods=['GET', 'POST'])
def assign_teacher():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Check if the form is submitted for registering a new teacher
        if request.form.get('name') and request.form.get('username'):
            name = request.form['name']
            username = request.form['username']
            if not is_username_assigned_to_teacher(username):
                insert_teacher(name, username)
                flash("Teacher registered successfully", "success")
            else:
                flash("Username already exists and is assigned to a teacher. Please choose a different username.",
                      "error")

        # Check if the form is submitted for deleting a teacher
        elif request.form.get('delete_teacher_id'):
            teacher_id_to_delete = request.form['delete_teacher_id']
            delete_teacher_by_id(teacher_id_to_delete)
            flash('Teacher deleted successfully', 'success')

    # Get all teachers for displaying in the form
    teachers = get_all_teachers()
    return render_template('assign_teacher.html', teachers=teachers)


@app.route('/assign_student', methods=['GET', 'POST'])
def assign_student():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Check if the form is submitted for assigning a new student
        if request.form.get('name') and request.form.get('username') and request.form.get('semester') and request.form.get('department'):
            name = request.form['name']
            username = request.form['username']
            semester = request.form['semester']
            department = request.form['department']

            # Check if the username is already assigned to a student
            if is_username_assigned_to_student(username):
                flash("Username already exists. Please choose a different username.", "error")
            else:
                insert_student(name, username, semester, department)
                flash("Student assigned successfully", "success")

        # Check if the form is submitted for deleting a student
        elif request.form.get('delete_student_id'):
            student_id_to_delete = request.form['delete_student_id']
            delete_student_by_id(student_id_to_delete)
            flash('Student deleted successfully', 'success')

    # Get all students for displaying in the form
    students = get_all_students()
    return render_template('assign_student.html', students=students)


@app.route('/assign_subject', methods=['GET', 'POST'])
def assign_subject():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        subject_name = request.form['subject_name']
        teacher_username = request.form['teacher_username']
        if subject_name and teacher_username:
            if is_subject_assigned_to_other_teacher(subject_name, teacher_username):
                flash("Subject already assigned to a different teacher", "error")
            else:
                insert_subject(subject_name, teacher_username)
                flash("Subject assigned successfully", "success")
    subjects = get_subjects_with_teachers()
    teachers = get_all_teachers()
    return render_template('assign_subject.html', subjects=subjects, teachers=teachers)


@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists in the teachers' database
        if not is_username_assigned_to_teacher(username):
            return "Teacher username not found. Please contact the admin."

        # Check if the entered password matches the stored password for the teacher
        if not verify_teacher_password(username, password):
            return "Invalid password. Please try again."

        # Set the 'username' key in the session upon successful login
        session['username'] = username

        # Redirect to teacher dashboard upon successful login
        return redirect(url_for('teacher_dashboard'))

    # If the request method is GET, render the teacher login page
    return render_template('teacher_login.html')


@app.route('/teacher/dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'username' in session:
        teacher_username = session['username']

        teacher_subject_map = get_teacher_subject_map()

        teacher_data = teacher_subject_map.get(teacher_username)
        if teacher_data:
            subject = teacher_data["subject"]
            database_path = teacher_data["database"]

            # Get the total classes taken by the teacher
            total_classes_taken = get_total_classes_taken(database_path, teacher_username)

            # Assuming you have a function to fetch attendance data from the database
            attendance_data = fetch_attendance_data(database_path, teacher_username)

            # Handle POST request for updating classes present
            if request.method == 'POST':
                student_id = request.form.get('student_id')
                classes_present = int(request.form.get('classes_present'))

                # Update the classes present in the corresponding subject's database
                update_classes_present_in_database(database_path, student_id, classes_present)

                # Redirect to avoid form resubmission
                return redirect('/teacher/dashboard')

            return render_template('teacher_dashboard.html', teacher_username=teacher_username, subject=subject,
                                   total_classes_taken=total_classes_taken, attendance_data=attendance_data)
        else:
            return "Subject not found for this teacher."
    else:
        return redirect(url_for('teacher_login'))


@app.route('/teacher/set_password', methods=['GET', 'POST'])
def teacher_set_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        # Check if the username exists in the teachers' database
        if not is_username_assigned_to_teacher(username):
            return "Teacher username not found. Please contact the admin."
        # Set the password for the teacher
        set_teacher_password(username, new_password)
        return redirect(url_for('teacher_login'))
    return render_template('teacher_set_password.html')


@app.route('/delete_subject', methods=['POST'])
def delete_subject():
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        teacher_username = request.form['teacher_username']
        delete_subject_from_db(subject_name, teacher_username)
        return redirect(url_for('assign_subject'))


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists in the students' database
        if not is_username_assigned_to_student(username):
            return "Student username not found. Please contact the admin."

        # Check if the entered password matches the stored password for the student
        if not verify_student_password(username, password):
            return "Invalid password. Please try again."

        # Set the 'username' key in the session upon successful login
        session['username'] = username

        # Redirect to student dashboard upon successful login
        return redirect(url_for('student_dashboard'))

    # If the request method is GET, render the student login page
    return render_template('student_login.html')


@app.route('/student/dashboard')
def student_dashboard():
    # Assuming the username is stored in the session
    student_username = session.get('username')

    if not student_username:
        return redirect(url_for('student_login'))

    # Get the attendance data for each subject
    teacher_subject_map = get_teacher_subject_map()
    attendance_data = {}

    for teacher, subject_info in teacher_subject_map.items():
        database_path = subject_info['database']
        attendance_percentage = get_student_attendance(database_path, student_username)
        attendance_data[subject_info['subject']] = attendance_percentage

    return render_template('student_dashboard.html', student_username=student_username, attendance_data=attendance_data)


@app.route('/student/set_password', methods=['GET', 'POST'])
def student_set_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']

        # Check if the username exists in the students' database
        if not is_username_assigned_to_student(username):
            return "Student username not found. Please contact the admin."

        # Set the password for the student
        set_student_password(username, new_password)
        return redirect(url_for('student_login'))

    return render_template('student_set_password.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
