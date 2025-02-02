from unittest.mock import patch
import json
import pytest
from tests.base import BaseTestCase
from core import db
from core.models.assignments import Assignment, GradeEnum, AssignmentStateEnum

class TestGradeAssignment(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Use assignment ID 30 which is in SUBMITTED state
        self.assignment = Assignment.get_by_id(30)
        if not self.assignment:
            self.assignment = Assignment(
                student_id=1,
                teacher_id=1,
                content="Test Assignment",
                state=AssignmentStateEnum.SUBMITTED
            )
            db.session.add(self.assignment)
            db.session.commit()

    def test_teacher_grade_assignment_success(self):
        """Test successful grading of assignment by teacher"""
        headers = {
            'X-Principal': json.dumps({
                'user_id': 3,  # teacher1 user_id
                'teacher_id': 1  # teacher1 id
            })
        }
        data = {
            'id': self.assignment.id,
            'grade': GradeEnum.A.value
        }
        
        response = self.client.post(
            '/teacher/assignments/grade',
            headers=headers,
            json=data
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)['data']
        assert response_data['grade'] == GradeEnum.A.value
        assert response_data['state'] == AssignmentStateEnum.GRADED.value

    def test_teacher_grade_unassigned_assignment(self):
        """Test grading of assignment not assigned to teacher"""
        headers = {
            'X-Principal': json.dumps({
                'user_id': 4,  # teacher2 user_id
                'teacher_id': 2  # teacher2 id
            })
        }
        data = {
            'id': self.assignment.id,
            'grade': GradeEnum.A.value
        }
        
        response = self.client.post(
            '/teacher/assignments/grade',
            headers=headers,
            json=data
        )
        
        assert response.status_code == 403
        response_data = json.loads(response.data)
        assert response_data['error'] == 'ValidationError'
        assert response_data['message'] == 'Assignment not assigned to this teacher'
        
        # Verify assignment wasn't modified
        db.session.refresh(self.assignment)
        assert self.assignment.grade is None
        assert self.assignment.state == AssignmentStateEnum.SUBMITTED
        assert self.assignment.teacher_id == 1

    def test_principal_grade_assignment_success(self):
        """Test successful grading of assignment by principal"""
        headers = {
            'X-Principal': json.dumps({
                'user_id': 5,
                'principal_id': 1
            })
        }
        data = {
            'id': self.assignment.id,
            'grade': GradeEnum.B.value
        }
        
        response = self.client.post(
            '/principal/assignments/grade',
            headers=headers,
            json=data
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)['data']
        assert response_data['grade'] == GradeEnum.B.value
        assert response_data['state'] == AssignmentStateEnum.GRADED.value

    def test_invalid_grade_value(self):
        """Test grading with invalid grade value"""
        headers = {
            'X-Principal': json.dumps({
                'user_id': 3,  # teacher1 user_id
                'teacher_id': 1  # teacher1 id
            })
        }
        data = {
            'id': self.assignment.id,
            'grade': 'X'  # Invalid grade
        }
        
        response = self.client.post(
            '/teacher/assignments/grade',
            headers=headers,
            json=data
        )
        
        assert response.status_code == 400

    def test_grade_non_submitted_assignment(self):
        """Test grading assignment that is not in draft state"""
        # Create a new draft assignment
        draft_assignment = Assignment(
            student_id=1,
            teacher_id=1,
            content="Test Draft Assignment",
            state=AssignmentStateEnum.DRAFT
        )
        db.session.add(draft_assignment)
        db.session.commit()
        
        # Ensure the assignment was created with an ID
        assert draft_assignment.id is not None
        
        headers = {
            'X-Principal': json.dumps({
                'user_id': 3,  # teacher1 user_id
                'teacher_id': 1  # teacher1 id
            })
        }
        data = {
            'id': draft_assignment.id,
            'grade': GradeEnum.A.value
        }
        
        response = self.client.post(
            '/teacher/assignments/grade',
            headers=headers,
            json=data
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['error'] == 'ValidationError'
        assert response_data['message'] == 'Only submitted assignments can be graded'
        
        # Verify no changes were made
        db.session.refresh(draft_assignment)
        assert draft_assignment.grade is None
        assert draft_assignment.state == AssignmentStateEnum.DRAFT
