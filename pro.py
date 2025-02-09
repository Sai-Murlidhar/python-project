import sqlite3

# Connect to SQLite database (this will create the file if it doesn't exist)
conn = sqlite3.connect('student_report_card_system.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS marks (student_id INTEGER, subject_id INTEGER, marks INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students(id), FOREIGN KEY (subject_id) REFERENCES subjects(id), 
                    PRIMARY KEY (student_id, subject_id))''')
conn.commit()

# Admin Panel Functions
def add_item(table, column, name):
    cursor.execute(f'INSERT INTO {table} ({column}) VALUES (?)', (name,))
    conn.commit()

# Marks Management
def input_marks(student_name, subject_name, marks):
    student_id = cursor.execute('SELECT id FROM students WHERE name = ?', (student_name,)).fetchone()[0]
    subject_id = cursor.execute('SELECT id FROM subjects WHERE name = ?', (subject_name,)).fetchone()[0]
    cursor.execute('REPLACE INTO marks (student_id, subject_id, marks) VALUES (?, ?, ?)', (student_id, subject_id, marks))
    conn.commit()

# Report Generation
def generate_report(student_name):
    student_id = cursor.execute('SELECT id FROM students WHERE name = ?', (student_name,)).fetchone()[0]
    rows = cursor.execute('''SELECT subjects.name, marks.marks 
                              FROM marks JOIN subjects ON marks.subject_id = subjects.id 
                              WHERE marks.student_id = ?''', (student_id,)).fetchall()
    
    if rows:
        total_marks = sum(row[1] for row in rows)
        max_marks = len(rows) * 100  # assuming each subject is out of 100
        print(f"\nReport Card for {student_name}:")
        for subject, marks in rows:
            print(f"{subject}: {marks} marks")
        print(f"\nTotal Marks: {total_marks}/{max_marks}\nGrade: {calculate_grade(total_marks, max_marks)}")
    else:
        print("No marks recorded.")

def calculate_grade(total_marks, max_marks):
    percentage = (total_marks / max_marks) * 100
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B"
    elif percentage >= 60: return "C"
    elif percentage >= 50: return "D"
    return "F"

def overall_class_performance():
    rows = cursor.execute('''SELECT students.name, SUM(marks.marks) 
                              FROM marks JOIN students ON marks.student_id = students.id 
                              GROUP BY students.id''').fetchall()
    for name, total_marks in rows:
        print(f"{name}: {total_marks} total marks")

# Example of managing the system:
def main():
    # Add subjects (Mathematics 1 and Mathematics 2)
    for subject in ["Mathematics 1", "Mathematics 2"]:
        add_item("subjects", "name", subject)
    
    # Add students
    for student in ["Durga", "Sai"]:
        add_item("students", "name", student)

    # Assign marks to students
    input_marks("Durga", "Mathematics 1", 75)
    input_marks("Durga", "Mathematics 2", 70)
    input_marks("Sai", "Mathematics 1", 78)
    input_marks("Sai", "Mathematics 2", 82)

    # Generate individual report cards
    generate_report("Durga")
    generate_report("Sai")

    # View overall class performance
    overall_class_performance()

if __name__ == '__main__':
    main()

# Close the database connection when done
conn.close()
