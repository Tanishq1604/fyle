from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from core import db
from core.models.assignments import Assignment
from core.models.teachers import Teacher
from core.models.students import Student

class AssignmentView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['content', 'state', 'grade']
    column_filters = ['teacher_id', 'student_id', 'state', 'grade']

class TeacherView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

class StudentView(ModelView):
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True

def init_admin(app):
    admin = Admin(app, name='Fyle School Admin', template_mode='bootstrap3')
    
    # Add model views
    admin.add_view(AssignmentView(Assignment, db.session))
    admin.add_view(TeacherView(Teacher, db.session))
    admin.add_view(StudentView(Student, db.session))
    
    return admin
