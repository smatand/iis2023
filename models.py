from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


db = SQLAlchemy()

class EventCategory(db.Model):
    __tablename__ = "event_category_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))

class UserEvent(db.Model):
    __tablename__ = "user_event_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    events: Mapped[List["Event"]] = relationship(
        secondary="user_event_table",
        back_populates="users"
    )

    reviews: Mapped[List["Review"]] = relationship(back_populates="user")


class Place(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    events: Mapped[List["Event"]] = relationship(back_populates="place")


class Event(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_datetime: Mapped[int] = mapped_column(Integer)
    end_datetime: Mapped[int] = mapped_column(Integer)
    capacity: Mapped[str] = mapped_column(String)

    place: Mapped["Place"] = relationship(back_populates="events")
    place_id: Mapped[int] = mapped_column(ForeignKey("place.id"))

    users: Mapped[List["User"]] = relationship(
        secondary="user_event_table",
        back_populates="events"
    )
    categories: Mapped[List["Category"]] = relationship(
        secondary="event_category_table", 
        back_populates="events"
    )

    reviews: Mapped[List["Review"]] = relationship(back_populates="event")


class Category(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    parent_id = mapped_column(Integer, ForeignKey("category.id"))
    parent: Mapped[List["Category"]] = relationship("Category", remote_side=[id])

    events: Mapped[List["Event"]] = relationship(
        secondary="event_category_table", 
        back_populates="categories"
    )


class Review(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(String)
    rating: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="reviews")

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    event: Mapped["Event"] = relationship(back_populates="reviews")

if __name__ == "__main__":
    print("What are you doing?")
