class Student:
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade

    def __repr__(self):
        return f'Student(name={self.name}, age={self.age}, grade={self.grade})'

class Class:
    def __init__(self):
        self.students = []

    def collect_student(self, name, age, grade):
        new_student = Student(name, age, grade)
        self.students.append(new_student)

# Create a Class instance
my_class = Class()

# Collecting students
my_class.collect_student('Alice', 23, 90)
my_class.collect_student('Bob', 22, 85)
my_class.collect_student('Charlie', 20, 95)
my_class.collect_student('Diana', 21, 80)
my_class.collect_student('Ethan', 24, 88)

# Sorting the students by their grades
sorted_students = sorted(my_class.students, key=lambda student: student.grade)

# Return the sorted list for output
for student in sorted_students:
    print(student)