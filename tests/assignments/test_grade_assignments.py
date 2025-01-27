from unittest.mock import patch
import json
import pytest
from tests.base import BaseTestCase
from core import db
from core.models.assignments import Assignment, GradeEnum, AssignmentStateEnum

class TestGradeAssignment(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create test assignment explicitly assigned to teacher_id=1
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
                'user_id': 3,
                'teacher_id': 1
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
        # Create test data
        headers = {
            'X-Principal': json.dumps({
                'user_id': 2,
                'teacher_id': 5  # Different teacher
            })
        }
        data = {
            'id': self.assignment.id,
            'grade': GradeEnum.A.value
        }
        
        # Make the request
        response = self.client.post(
            '/teacher/assignments/grade',
            headers=headers,
            json=data
        )
        
        # Verify response
        assert response.status_code == 403
        response_data = json.loads(response.data)
        assert response_data['error'] == 'ValidationError'
        assert response_data['message'] == 'Assignment not assigned to this teacher'
        
        # Verify assignment wasn't modified
        db_assignment = Assignment.query.get(self.assignment.id)
        assert db_assignment.grade is None
        assert db_assignment.state == AssignmentStateEnum.SUBMITTED

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
                'user_id': 3,
                'teacher_id': 1
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
        """Test grading assignment that is not in submitted state"""
        # Change assignment state to draft
        self.assignment.state = AssignmentStateEnum.DRAFT
        db.session.commit()

        headers = {
            'X-Principal': json.dumps({
                'user_id': 3,
                'teacher_id': 1
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
        
        assert response.status_code == 400
        assert b'Only submitted assignments can be graded' in response.data
