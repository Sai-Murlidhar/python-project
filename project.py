import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='student_report_card_system'
)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS marks (student_id INT, subject_id INT, marks INT,
                    FOREIGN KEY (student_id) REFERENCES students(id), FOREIGN KEY (subject_id) REFERENCES subjects(id), 
                    PRIMARY KEY (student_id, subject_id))''')
conn.commit()

def add_item(table, column, name):
    cursor.execute(f'SELECT id FROM {table} WHERE {column} = %s', (name,))
    result = cursor.fetchone()
    cursor.fetchall()  # Clear unread results
    if not result:
        cursor.execute(f'INSERT INTO {table} ({column}) VALUES (%s)', (name,))
        conn.commit()

def input_marks(student_name, subject_name, marks):
    cursor.execute('SELECT id FROM students WHERE name = %s', (student_name,))
    student_id = cursor.fetchone()
    cursor.fetchall()  # Clear unread results

    cursor.execute('SELECT id FROM subjects WHERE name = %s', (subject_name,))
    subject_id = cursor.fetchone()
    cursor.fetchall()  # Clear unread results

    if student_id and subject_id:
        student_id = student_id[0]
        subject_id = subject_id[0]
        cursor.execute('INSERT INTO marks (student_id, subject_id, marks) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE marks = %s',
                       (student_id, subject_id, marks, marks))
        conn.commit()

def generate_report(student_name):
    cursor.execute('SELECT id FROM students WHERE name = %s', (student_name,))
    student_id = cursor.fetchone()
    cursor.fetchall()  # Clear unread results

    if not student_id:
        print(f"Student '{student_name}' not found.")
        return

    student_id = student_id[0]
    cursor.execute('''SELECT subjects.name, marks.marks 
                      FROM marks JOIN subjects ON marks.subject_id = subjects.id 
                      WHERE marks.student_id = %s''', (student_id,))
    rows = cursor.fetchall()

    if rows:
        total_marks = sum(row[1] for row in rows)
        max_marks = len(rows) * 100
        print(f"\nReport Card for {student_name}:")
        for subject, marks in rows:
            print(f"{subject}: {marks} marks")
        print(f"\nTotal Marks: {total_marks}/{max_marks}\nGrade: {calculate_grade(total_marks, max_marks)}")
    else:
        print(f"No marks recorded for {student_name}.")

def calculate_grade(total_marks, max_marks):
    percentage = (total_marks / max_marks) * 100
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B"
    elif percentage >= 60: return "C"
    elif percentage >= 50: return "D"
    return "F"

def overall_class_performance():
    cursor.execute('''SELECT students.name, SUM(marks.marks) 
                      FROM marks JOIN students ON marks.student_id = students.id 
                      GROUP BY students.id''')
    rows = cursor.fetchall()
    for name, total_marks in rows:
        print(f"{name}: {total_marks} total marks")

def main():
    for subject in ["Mathematics 1", "Mathematics 2"]:
        add_item("subjects", "name", subject)

    for student in ["Durga", "Sai"]:
        add_item("students", "name", student)

    input_marks("Durga", "Mathematics 1", 85)
    input_marks("Durga", "Mathematics 2", 80)
    input_marks("Sai", "Mathematics 1", 92)
    input_marks("Sai", "Mathematics 2", 86)

    generate_report("Durga")
    generate_report("Sai")

    overall_class_performance()

if __name__ == '__main__':
    main()

conn.close()
