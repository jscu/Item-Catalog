from models import User, Base, Item, Category
from init_db import init_db, db_session

if __name__ == '__main__':
    init_db()

    user = User(
        name='Justin',
        email='justin.sou@gmail.com',
    )

    db_session.add(user)
    db_session.commit()

    category = Category(
        name='Basketball',
        user=user
    )

    db_session.add(category)
    db_session.commit()

    item = Item(
        name='Basketball Shoes',
        description='A pair of special basktball shoes',
        category=category,
        user=user
    )

    db_session.add(item)
    db_session.commit()