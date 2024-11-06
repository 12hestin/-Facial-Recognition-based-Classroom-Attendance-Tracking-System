import os
import cv2
import face_recognition
from attdatabase import initialize_subject_databases, insert_classes_taken, insert_attendance
from datetime import datetime

# Function to load known faces of both students and teachers
def load_known_faces(known_faces_dir):
    known_faces = []
    known_face_names = []

    for filename in os.listdir(known_faces_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            face_image = face_recognition.load_image_file(os.path.join(known_faces_dir, filename))
            face_encodings = face_recognition.face_encodings(face_image, model="large")

            if len(face_encodings) > 0:
                known_faces.extend(face_encodings)
                known_face_names.extend([os.path.splitext(filename)[0]] * len(face_encodings))
            else:
                print(f"No face found in {filename}")

    return known_faces, known_face_names

# Function to recognize both students and teachers
def recognize_faces(known_faces, known_face_names, test_image):
    face_locations = face_recognition.face_locations(test_image, number_of_times_to_upsample=2)
    face_encodings = face_recognition.face_encodings(test_image, face_locations, model="large")

    recognized_faces = set()

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.5)
        name = "Unknown"

        if any(matches):
            matched_names = [known_face_names[i] for i, match in enumerate(matches) if match]
            recognized_faces.update(matched_names)

    return recognized_faces

if __name__ == "__main__":
    known_faces_dir_students = "face/images/student_image"  # Directory containing known student faces
    known_faces_dir_teachers = "face/images/teacher_image"  # Directory containing known teacher faces
    known_faces_students, known_face_names_students = load_known_faces(known_faces_dir_students)
    known_faces_teachers, known_face_names_teachers = load_known_faces(known_faces_dir_teachers)

    # Map each teacher name to a subject and corresponding database name
    teacher_subject_map = {
        "teacher01": {"subject": "DCC", "database": "dcc_attendance.db"},
        "teacher02": {"subject": "IEFT", "database": "ieft_attendance.db"},
        "teacher03": {"subject": "CD", "database": "cd_attendance.db"},
        "teacher04": {"subject": "AAD", "database": "aad_attendance.db"},
        "teacher05": {"subject": "CGIP", "database": "cgip_attendance.db"},
        "teacher06": {"subject": "MP", "database": "mp_attendance.db"},
        "teacher07": {"subject": "NL", "database": "nl_attendance.db"},
        # Add more mappings as needed
    }

    # Create or initialize the database
    initialize_subject_databases(teacher_subject_map)

    # Define the schedule for each period
    period_schedule = [
        {"start_time": "09:20", "end_time": "10:20"},
        {"start_time": "10:21", "end_time": "11:15"},
        {"start_time": "11:25", "end_time": "13:09"},
        {"start_time": "13:10", "end_time": "14:10"},
        {"start_time": "14:11", "end_time": "15:10"},
        {"start_time": "15:11", "end_time": "22:10"},
    ]

    # Capture photos through webcam
    max_iterations = 5  # Define the maximum number of iterations
    iteration_count = 0  # Initialize the iteration count

    while iteration_count < max_iterations:
        current_time = datetime.now().strftime("%H:%M")

        # Check if it's within any of the scheduled periods
        current_period = None
        for i, period in enumerate(period_schedule):
            start_time = period["start_time"]
            end_time = period["end_time"]

            if start_time <= current_time <= end_time:
                current_period = i + 1  # Periods are 1-indexed
                break

        if current_period:
            print(f"Current period: {current_period}")

            cap = cv2.VideoCapture(0)  # 0 corresponds to the default webcam

            # Toggle camera on
            ret, frame = cap.read()

            if ret:
                recognized_faces = recognize_faces(known_faces_students + known_faces_teachers,
                                                    known_face_names_students + known_face_names_teachers,
                                                    frame)

                print("Recognized Faces:", recognized_faces)  # Debugging print statement

                # If a teacher is recognized, set the subject automatically and start the iteration loop
                for teacher_name in recognized_faces.intersection(known_face_names_teachers):
                    teacher_data = teacher_subject_map.get(teacher_name)
                    if teacher_data:
                        subject = teacher_data["subject"]
                        database_path = teacher_data["database"]

                        print("Teacher {} detected. Subject set to: {}".format(teacher_name, subject))  # Debugging print statement

                        # Insert classes taken by the teacher
                        insert_classes_taken(database_path, teacher_name, subject)

                        # Recognize students and insert attendance
                        recorded_students = set()  # Set to keep track of recorded students in the current iteration

                        while True:
                            # Capture photo
                            ret, frame = cap.read()

                            if ret:
                                recognized_faces = recognize_faces(known_faces_students, known_face_names_students, frame)

                                # Insert attendance for recognized students
                                for name in recognized_faces:
                                    if name in known_face_names_students and name not in recorded_students:
                                        try:
                                            # Record attendance with the current timestamp and period
                                            insert_attendance(database_path, name)
                                            print("Attendance recorded for student:", name)  # Debugging print statement
                                            recorded_students.add(name)  # Add the student to recorded students
                                        except Exception as e:
                                            print("Error inserting attendance for student:", name, "Error:", e)
                                    elif name in known_face_names_students:
                                        # Only print the recognized face if it's not a duplicate
                                        print("Attendance already recorded for student:", name)
                                    else:
                                        print("Unrecognized face:", name)  # Debugging print statement

                            else:
                                print("Failed to capture a frame from the webcam.")

                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

                        print("Exiting the iteration loop.")

                    # Release the webcam
                    cap.release()

                    iteration_count += 1  # Increment the iteration count

                else:
                    print("Failed to capture a frame from the webcam.")
        else:
            print("No scheduled period at the current time.")

        # Add a delay before checking the schedule again
        # Adjust the duration based on your specific needs
        cv2.waitKey(5000)  # Delay for 5 seconds
