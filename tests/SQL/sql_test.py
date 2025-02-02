import random
import pytest
from sqlalchemy import text
from core import db, create_app
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum


class TestSQL:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def create_n_graded_assignments_for_teacher_and_student(self, number: int = 0, teacher_id: int = 1, student_id: int = 1) -> int:
        """
        Creates 'n' graded assignments for a specified teacher and returns the count of assignments with grade 'A'.

        Parameters:
        - number (int): The number of assignments to be created.
        - teacher_id (int): The ID of the teacher for whom the assignments are created.

        Returns:
        - int: Count of assignments with grade 'A'.
        """
        # Count the existing assignments with grade 'A' for the specified teacher
        grade_a_counter: int = Assignment.query.filter(
            Assignment.teacher_id == teacher_id,
            Assignment.grade == GradeEnum.A
        ).count()

        # Create 'n' graded assignments
        for _ in range(number):
            # Randomly select a grade from GradeEnum
            grade = random.choice(list(GradeEnum))

            # Create a new Assignment instance
            assignment = Assignment(
                teacher_id=teacher_id,
                student_id=student_id,
                grade=grade,
                content='test content',
                state=AssignmentStateEnum.GRADED
            )

            # Add the assignment to the database session
            db.session.add(assignment)

            # Update the grade_a_counter if the grade is 'A'
            if grade == GradeEnum.A:
                grade_a_counter += 1

        db.session.flush()

        # Return the count of assignments with grade 'A'
        return grade_a_counter

    def test_count_assignments_in_each_grade(self):
        """Test to get count of assignments for each grade"""
        # Create 25 graded assignments for student 1
        self.create_n_graded_assignments_for_teacher_and_student(25, student_id=1)
        
        # Create 20 graded assignments for student 2
        self.create_n_graded_assignments_for_teacher_and_student(20, student_id=2)

        # Get counts for each grade from database
        expected_result = []
        for grade in GradeEnum:
            count = Assignment.query.filter(
                Assignment.grade == grade,
                Assignment.state == AssignmentStateEnum.GRADED
            ).count()
            expected_result.append((grade.value, count))

        # Sort expected results by grade
        expected_result.sort(key=lambda x: x[0])

        # Execute the SQL query
        with open('tests/SQL/count_assignments_in_each_grade.sql', encoding='utf8') as fo:
            sql = fo.read()
        sql_result = db.session.execute(text(sql)).fetchall()

        # Compare results
        assert len(expected_result) == len(sql_result), "Number of grades doesn't match"
        for expected, actual in zip(expected_result, sql_result):
            assert expected[0] == actual[0], f"Grade mismatch: expected {expected[0]}, got {actual[0]}"
            assert expected[1] == actual[1], f"Count mismatch for grade {expected[0]}: expected {expected[1]}, got {actual[1]}"

    def test_get_grade_A_assignments_for_teacher_with_max_grading(self):
        """Test to get count of grade A assignments for teacher which has graded maximum assignments"""
        
        # Create assignments for first teacher (teacher_id=1)
        grade_a_count_1 = self.create_n_graded_assignments_for_teacher_and_student(5)
        
        # Create assignments for second teacher (teacher_id=2) with more assignments
        grade_a_count_2 = self.create_n_graded_assignments_for_teacher_and_student(10, teacher_id=2)
        
        # Read and execute the SQL query
        with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
            sql = fo.read()
        
        result = db.session.execute(text(sql)).scalar()
        
        # The result should match teacher 2's grade A count since they have more assignments
        assert result == grade_a_count_2, f"Expected {grade_a_count_2} A grades for teacher with most assignments, got {result}"

    def teardown_method(self) -> None:
        # Rollback the changes to the database after each test
        db.session.rollback()
