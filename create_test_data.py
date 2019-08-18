from models import User, Item, Category
from init_db import init_db, db_session

if __name__ == '__main__':
    init_db()

    user = User(
        name='Justin Sou',
        email='jscu14@gmail.com',
    )

    db_session.add(user)
    db_session.commit()

    for cat in ['Soccer', 'Baseball', 'Frisbee', 'Snowboarding', 'Rock Climbing', 'Foosball', 'Skating', 'Hockey', 'Basketball']:
        category = Category(
            name=cat,
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
