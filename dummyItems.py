
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, CategoryItem, Base

engine = create_engine('sqlite:///categoryItems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Add categories
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

category2 = Category(name="Casino")

session.add(category2)
session.commit()

category3 = Category(name="Computer Game")

session.add(category3)
session.commit()

category4 = Category(name="Book")

session.add(category4)
session.commit()

print("added categories!")


# Add Items
categoryItem1 = CategoryItem(
    name="WorldCup", description="WorldCup!", category=category1)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    name="Goal", description="Goal!", category=category1)

session.add(categoryItem2)
session.commit()


categoryItem1 = CategoryItem(
    name="BlackJack", description="BlackJack!", category=category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    name="Slot Machine", description="Slot Machine!", category=category2)

session.add(categoryItem2)
session.commit()


categoryItem1 = CategoryItem(
    name="Super Mario", description="Super Mario!", category=category3)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    name="The last of us", description="The last of us!", category=category3)

session.add(categoryItem2)
session.commit()


categoryItem1 = CategoryItem(
    name="Doctors", description="Doctors!", category=category4)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(
    name="Princess Diary", description="Princess Diary!", category=category4)

session.add(categoryItem2)
session.commit()


print("added category items!")
