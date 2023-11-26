from models import Category


def get_category_choices():
    categories = Category.query.all()

    def get_category_tree(category, prefix=''):
        choices = [(category.id, prefix + category.name)]
        for subcategory in category.children:
            choices.extend(get_category_tree(subcategory, prefix + '-'))
        return choices
    choices = []
    for category in categories:
        if category.parent is None:
            choices.extend(get_category_tree(category))
    return choices
