from database.database import get_all_items


async def get_available_items_title_db():
    items = await get_all_items()
    return [item[2] for item in items]


def get_type_name(type: int):
    if type == 1:
        return 'BOX'
    else:
        return 'BAG'

def get_type_name_grammar(type: int, qty: int):
    if type == 1:
        if qty > 1:
            return 'boxes'
        return 'box'
    else:
        if qty > 1:
            return 'bags'
        return 'bag'

def format_number_with_spaces(number):
    return "{:,}".format(number).replace(',', ' ')