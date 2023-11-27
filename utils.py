from models import Category


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
