from models import Category
from wtforms import ValidationError


def get_category_choices():
    # query only approved categories
    categories = Category.query.filter_by(approved=True).all()

    def get_category_tree(category, prefix=''):
        choices = [(category.id, prefix + category.name)]
        for subcategory in category.children:
            # if approved
            if subcategory.approved:
                choices.extend(get_category_tree(subcategory, prefix + '>'))
        return choices
    choices = [(None, '---none---')]
    for category in categories:
        if category.parent is None:
            if category.approved:
                choices.extend(get_category_tree(category))
    return choices


def validate_date(form, field):
    if form.start_datetime.data and form.end_datetime.data:
        if field.data <= form.start_datetime.data:
            raise ValidationError('End time must be after start time.')
