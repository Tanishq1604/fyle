from flask import Blueprint, request, jsonify
import json
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core.libs.exceptions import ResourceNotFoundException, InvalidRequestException
from core.apis.decorators import AuthPrincipal
from core import db

teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)

@teacher_assignments_resources.route('/assignments/grade', methods=['POST'])
def grade_assignment():
    data = request.get_json()
    principal = request.headers.get('X-Principal')
    principal_data = json.loads(principal)
    teacher_id = principal_data.get('teacher_id')
    
    assignment = Assignment.get_by_id(data.get('id'))
    if not assignment:
        return jsonify({
            'error': 'ResourceNotFoundError',
            'message': 'Assignment not found'
        }), 404
        
    # Validate teacher has permission to grade this assignment
    if assignment.teacher_id != teacher_id:
        return jsonify({
            'error': 'ValidationError',
            'message': 'Assignment not assigned to this teacher'
        }), 403

    # Validate assignment state
    if assignment.state != AssignmentStateEnum.SUBMITTED:
        return jsonify({
            'error': 'ValidationError',
            'message': 'Only submitted assignments can be graded'
        }), 400

    try:
        # Update assignment
        assignment.grade = GradeEnum(data.get('grade'))
        assignment.state = AssignmentStateEnum.GRADED
        db.session.commit()
        
        return jsonify({
            'data': assignment.to_dict()
        }), 200
    except ValueError:
        db.session.rollback()
        return jsonify({
            'error': 'ValidationError',
            'message': 'Invalid grade value'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': type(e).__name__,
            'message': str(e)
        }), 400

