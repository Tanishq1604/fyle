import enum
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum
from core.libs.exceptions import ResourceNotFoundException, InvalidRequestException
from core.models.base import BaseModel


class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    F = 'F'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(BaseModel):
    __tablename__ = 'assignments'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum), nullable=True)
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)

    # No need to define relationships here as they're handled by backref

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        if assignment_new.id is not None:
            assignment = Assignment.get_by_id(assignment_new.id)
            assertions.assert_found(assignment, 'No assignment with this id was found')
            assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'only assignment in draft state can be edited')

            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment_new)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = cls.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(assignment.student_id == auth_principal.student_id, 
                              'This assignment belongs to some other student')
        assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                              'Only draft assignments can be submitted')
        assertions.assert_valid(assignment.content is not None and assignment.content.strip(),
                              'Assignment content cannot be empty')

        assignment.teacher_id = teacher_id
        assignment.state = AssignmentStateEnum.SUBMITTED
        db.session.flush()
        return assignment

    @classmethod
    def mark_grade(cls, _id, grade, auth_principal):
        """Mark grade with simplified validation"""
        assignment = cls.get_by_id(_id)
        if not assignment:
            raise ResourceNotFoundException('No assignment with this id was found')
            
        if assignment.state not in {AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED}:
            raise InvalidRequestException('Only submitted assignments can be graded')

        try:
            if not isinstance(grade, GradeEnum):
                grade = GradeEnum(grade)
        except ValueError:
            raise InvalidRequestException('Invalid grade value')

        if assignment.grade == grade and assignment.state == AssignmentStateEnum.GRADED:
            return assignment  # No change needed
            
        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()
        return assignment

    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()

    @classmethod
    def get_assignments_by_teacher(cls, teacher_id):
        return cls.query.filter_by(teacher_id=teacher_id).all()

    @classmethod
    def get_assignments_by_principal(cls):
        return cls.filter(cls.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])).all()

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'grade': self.grade.value if self.grade else None,
            'content': self.content,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
