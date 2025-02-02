from core import db, create_app
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core.models.teachers import Teacher
from core.models.students import Student
from core.models.principals import Principal
from core.models.users import User
from datetime import datetime

def seed_database():
    try:
        # Clean existing data first
        print("Cleaning existing data...")
        for table in [Assignment, Teacher, Student, Principal, User]:
            table.query.delete()
        db.session.commit()

        # Create all users first
        print("Creating users...")
        users_data = [
            {'username': 'student1', 'email': 'student1@fylebe.com'},
            {'username': 'student2', 'email': 'student2@fylebe.com'},
            {'username': 'teacher1', 'email': 'teacher1@fylebe.com'},
            {'username': 'teacher2', 'email': 'teacher2@fylebe.com'},
            {'username': 'principal', 'email': 'principal@fylebe.com'}
        ]

        created_users = {}
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
            db.session.flush()
            created_users[user.username] = user.id

        # Create roles data using created user IDs
        students_data = [
            {'user_id': created_users['student1']},
            {'user_id': created_users['student2']}
        ]
        
        teachers_data = [
            {'user_id': created_users['teacher1']},
            {'user_id': created_users['teacher2']}
        ]

        principal_data = {'user_id': created_users['principal']}
        
        assignments_data = [
            {
                'student_id': 1,
                'teacher_id': 1,
                'content': 'ESSAY T1',
                'grade': GradeEnum.A,
                'state': AssignmentStateEnum.GRADED
            },
            {
                'student_id': 1,
                'teacher_id': 2,
                'content': 'THESIS T1',
                'grade': GradeEnum.A,
                'state': AssignmentStateEnum.GRADED
            },
            {
                'student_id': 2,
                'teacher_id': 2,
                'content': 'ESSAY T2',
                'state': AssignmentStateEnum.DRAFT
            },
            {
                'student_id': 2,
                'teacher_id': 2,
                'content': 'THESIS T2',
                'grade': GradeEnum.B,
                'state': AssignmentStateEnum.GRADED
            },
            {
                'student_id': 1,
                'teacher_id': 1,
                'content': 'Test Assignment',
                'state': AssignmentStateEnum.SUBMITTED
            }
        ]

        # Add students
        for student_data in students_data:
            student = Student(**student_data)
            db.session.add(student)

        # Add teachers
        for teacher_data in teachers_data:
            teacher = Teacher(**teacher_data)
            db.session.add(teacher)

        # Add principal
        principal = Principal(**principal_data)
        db.session.add(principal)

        # Add assignments
        for assignment_data in assignments_data:
            assignment = Assignment(**assignment_data)
            db.session.add(assignment)

        db.session.commit()
        print("Database seeded successfully!")
        
        # Print summary
        print("\nSeeded data summary:")
        print(f"Users created: {len(users_data)}")
        print(f"Students created: {len(students_data)}")
        print(f"Teachers created: {len(teachers_data)}")
        print(f"Principal created: 1")
        print(f"Assignments created: {len(assignments_data)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")
        raise

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Clean existing data
        db.drop_all()
        db.create_all()
        seed_database()
