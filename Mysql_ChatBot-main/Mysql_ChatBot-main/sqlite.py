import sqlite3

# Step 1: Connect to the SQLite database
connection = sqlite3.connect("student.db")

# Step 2: Create a cursor object
cursor = connection.cursor()

# Step 3: Define and execute the SQL command to create the STUDENT table
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT(
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
)
"""
cursor.execute(table_info)

# Step 4: Insert records into the STUDENT table
students = [
    ('Krish', 'Data Science', 'A', 90),
    ('John', 'Data Science', 'B', 100),
    ('Mukesh', 'Data Science', 'A', 86),
    ('Jacob', 'DEVOPS', 'A', 50),
    ('Dipesh', 'DEVOPS', 'A', 35)
]
cursor.executemany("INSERT INTO STUDENT VALUES (?, ?, ?, ?)", students)

# Step 5: Display all the records
print("The inserted records are:")
data = cursor.execute("SELECT * FROM STUDENT")
for row in data:
    print(f"Name: {row[0]}, Class: {row[1]}, Section: {row[2]}, Marks: {row[3]}")

# Step 6: Display the length of each value in the columns
print("\nLength of each value in the columns:")
lengths = cursor.execute("""
SELECT 
    NAME, LENGTH(NAME) AS NAME_LENGTH,
    CLASS, LENGTH(CLASS) AS CLASS_LENGTH,
    SECTION, LENGTH(SECTION) AS SECTION_LENGTH,
    MARKS, LENGTH(CAST(MARKS AS TEXT)) AS MARKS_LENGTH
FROM STUDENT
""")

for row in lengths:
    print(f"Name: {row[0]} (Length: {row[1]}), Class: {row[2]} (Length: {row[3]}), Section: {row[4]} (Length: {row[5]}), Marks: {row[6]} (Length: {row[7]})")

# Step 7: Commit changes and close the connection
connection.commit()
connection.close()
