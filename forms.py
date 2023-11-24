from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateTimeField,
    IntegerField,
    SubmitField,
    ValidationError
)
from wtforms.validators import DataRequired


def validate_date(form, field):
    if form.start_datetime.data and form.end_datetime.data:
        if field.data <= form.start_datetime.data:
            raise ValidationError('End time must be after start time.')


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
    description = StringField('Description', validators=[DataRequired()])
    image = StringField('Image URL')
    place_id = IntegerField('Place ID', validators=[DataRequired()])
    submit = SubmitField('Create Event')

    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        result = True
        return result
