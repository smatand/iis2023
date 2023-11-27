from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import (BooleanField, DateTimeField, IntegerField, SelectField,
                     SelectMultipleField, StringField, SubmitField,
                     TextAreaField, widgets)
from wtforms.validators import DataRequired, Length, Optional

from models import Category, Place, RoleEnum, Admission
from utils import get_category_choices, validate_date


class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    start_datetime = DateTimeField(
        'Start Date and Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()],
        default=datetime.now() + timedelta(minutes=30)
    )
    end_datetime = DateTimeField(
        'End Date and Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), validate_date],
        default=datetime.now() + timedelta(hours=1)
    )
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    description = StringField('Description')
    image = StringField('Image URL')
    place_id = SelectField('Place', validators=[DataRequired()], coerce=int)
    category_ids = SelectMultipleField('Category',
                                       validators=[Optional()],
                                       coerce=int,
                                       option_widget=widgets.CheckboxInput(),
                                       widget=widgets.ListWidget(
                                           prefix_label=False
                                           ))
    admission_ids = SelectMultipleField('Admission',
                                        validators=[Optional()],
                                        coerce=int,
                                        option_widget=widgets.CheckboxInput(),
                                        widget=widgets.ListWidget(
                                            prefix_label=False
                                        ))
    submit = SubmitField('Create Event')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.place_id.choices = [(p.id, p.name) for p in Place.query.filter_by(
            approved=True
        )]
        self.category_ids.choices = [
            (c.id, c.name) for c in Category.query.all()
            ]
        self.admission_ids.choices = [
            (c.id, c.name) for c in Admission.query.all()
            ]


class EditEventForm(FlaskForm):
    start_datetime = DateTimeField(
        'Start Date and Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()],
        default=datetime.now() + timedelta(minutes=30)
    )
    end_datetime = DateTimeField(
        'End Date and Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), validate_date],
        default=datetime.now() + timedelta(hours=1)
    )
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    description = StringField('Description')
    image = StringField('Image URL')
    place_id = SelectField('Place', validators=[DataRequired()], coerce=int)
    category_ids = SelectMultipleField('Category',
                                       validators=[Optional()],
                                       coerce=int,
                                       option_widget=widgets.CheckboxInput(),
                                       widget=widgets.ListWidget(
                                           prefix_label=False
                                           ))
    admission_ids = SelectMultipleField('Admission',
                                        validators=[Optional()],
                                        coerce=int,
                                        option_widget=widgets.CheckboxInput(),
                                        widget=widgets.ListWidget(
                                            prefix_label=False
                                        ))

    submit = SubmitField('Submit changes')

    def __init__(self, *args, **kwargs):
        super(EditEventForm, self).__init__(*args, **kwargs)
        self.place_id.choices = [(p.id, p.name) for p in Place.query.filter_by(
            approved=True
            ).all()]
        self.category_ids.choices = [
            (c.id, c.name) for c in Category.query.all()
            ]
        self.admission_ids.choices = [
            (c.id, c.name) for c in Admission.query.all()
            ]


class PlaceForm(FlaskForm):
    name = StringField('Place Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Create Place')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    parent_id = SelectField('Parent ID')
    submit = SubmitField('Propose')


class ReviewForm(FlaskForm):
    comment = TextAreaField('Comment',
                            validators=[DataRequired(),
                                        Length(min=2, max=200)]
                            )
    rating = SelectField('Rating',
                         choices=[(i, i) for i in range(1, 11)],
                         default=10,
                         coerce=int
                         )
    submit = SubmitField('Submit Review')


class EventAttendanceForm(FlaskForm):
    submit = SubmitField('Attend')


class EventAttendanceCancelForm(FlaskForm):
    submit = SubmitField('Cancel attend')


class EventCancelRequestForm(FlaskForm):
    submit = SubmitField('Cancel request')


class EventApproveRequestForm(FlaskForm):
    submit = SubmitField('Approve request')


class EventApprovalForm(FlaskForm):
    submit = SubmitField('Approve')


class DeleteReviewForm(FlaskForm):
    submit = SubmitField('Delete review')


class FilterForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    category = SelectMultipleField(
        'Category',
        validators=[Optional()],
        coerce=int,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False))
    place = SelectMultipleField(
        'Place',
        validators=[Optional()],
        coerce=int,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False))

    approved = BooleanField('Only approved', default=False)
    has_admission = BooleanField('Has admission', default=False)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.category.choices = get_category_choices()
        self.category.choices.pop(0)  # pop none choice
        self.place.choices = [(p.id, p.name) for p in Place.query.filter_by(
            approved=True
        )]


class UserSearchForm(FlaskForm):
    search = StringField('Search User')
    submit = SubmitField('Search')


class UserUpdateForm(FlaskForm):
    role = SelectField('Set Role', choices=[(role.name) for role in RoleEnum])
    submit = SubmitField('Update')
