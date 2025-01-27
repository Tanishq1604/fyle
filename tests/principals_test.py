import json
from core.models.assignments import AssignmentStateEnum, GradeEnum


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'ValidationError'
    assert 'Only submitted assignments can be graded' in response_data['message']


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200
    response_data = json.loads(response.data)['data']
    assert response_data['grade'] == GradeEnum.C.value
    assert response_data['state'] == AssignmentStateEnum.GRADED.value


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200
    response_data = json.loads(response.data)['data']
    assert response_data['grade'] == GradeEnum.B.value
    assert response_data['state'] == AssignmentStateEnum.GRADED.value
