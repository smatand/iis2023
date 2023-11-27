from __future__ import annotations

import enum
from datetime import datetime
from typing import List

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

event_category_table = db.Table(
    'event_category',
    Column('event_id', Integer, ForeignKey('event.id'),
           primary_key=True),

    Column('category_id', Integer, ForeignKey('category.id'),
           primary_key=True)
)

event_admission_table = db.Table(
    'event_admission',
    Column('event_id', Integer, ForeignKey('event.id'),
           primary_key=True),

    Column('admission_id', Integer, ForeignKey('admission.id'),
           primary_key=True)
)


class UserEvent(db.Model):
    __tablename__ = "event_user"

    event_id: Mapped[int] = mapped_column(
            ForeignKey("event.id"),
            primary_key=True
            )
    user_id: Mapped[int] = mapped_column(
            ForeignKey("user.id"),
            primary_key=True
            )

    user: Mapped["User"] = relationship(
            back_populates="events_association"
            )
    event: Mapped["Event"] = relationship(
            back_populates="users_association"
            )

    admission: Mapped[int] = mapped_column(
            Integer,
            nullable=True
            )
    approved: Mapped[bool] = mapped_column(
            Boolean,
            default=True
            )

    def get_item(user_id, event_id):
        query = db.select(UserEvent).filter_by(
                user_id=user_id, event_id=event_id
                )
        return db.execute(query).scalar_one_or_none()

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete_item(self):
        db.session.delete(self)
        db.session.commit()


class RoleEnum(enum.Enum):
    deactivated = 0
    user = 1
    moderator = 2
    administrator = 3


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True
            )
    name: Mapped[str] = mapped_column(
            String,
            nullable=False, unique=True
            )
    password: Mapped[str] = mapped_column(
            String,
            nullable=False
            )
    role: Mapped[RoleEnum] = mapped_column(
            Enum(RoleEnum),
            nullable=False
            )

    events: Mapped[List["Event"]] = relationship(
            secondary="event_user",
            back_populates="users",
            viewonly=True
            )
    events_association: Mapped[List["UserEvent"]] = relationship(
        back_populates="user"
        )

    owned_events: Mapped[List["Event"]] = relationship(
            back_populates="owner"
            )
    reviews: Mapped[List["Review"]] = relationship(
            back_populates="user"
            )

    def get_detail(id: int):
        return db.session.execute(db.select(User).filter_by(id=id)).one()

    def get_list():
        return db.session.execute(db.select(User.name)).all()

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Place(db.Model):
    __tablename__ = "place"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True
            )
    name: Mapped[str] = mapped_column(
            String,
            nullable=False
            )
    address: Mapped[str] = mapped_column(
            String,
            nullable=False, unique=True
            )
    description: Mapped[str] = mapped_column(
            String,
            nullable=True)

    approved: Mapped[bool] = mapped_column(
            Boolean,
            default=False
            )

    events: Mapped[List["Event"]] = relationship(
            back_populates="place"
            )

    def get_detail(id: int):
        return db.session.execute(db.select(Place).filter_by(id=id)).one()

    def get_list():
        return db.session.execute(db.select(Place.name)).all()

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Event(db.Model):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True
            )
    name: Mapped[str] = mapped_column(
            String,
            nullable=False, unique=True
            )
    start_datetime: Mapped[datetime] = mapped_column(
            DateTime,
            nullable=True
            )
    end_datetime: Mapped[datetime] = mapped_column(
            DateTime,
            nullable=True
            )
    capacity: Mapped[int] = mapped_column(
            Integer,
            nullable=True
            )
    description: Mapped[str] = mapped_column(
            String,
            nullable=True
            )
    image: Mapped[str] = mapped_column(
            String,
            nullable=True
            )
    approved: Mapped[bool] = mapped_column(
            Boolean,
            default=False,
            nullable=True
            )

    owner: Mapped["User"] = relationship(
            back_populates="owned_events"
            )
    owner_id: Mapped[int] = mapped_column(
            ForeignKey("user.id")
            )

    place: Mapped["Place"] = relationship(
            back_populates="events"
            )
    place_id: Mapped[int] = mapped_column(
            ForeignKey("place.id")
            )

    users: Mapped[List["User"]] = relationship(
            secondary="event_user",
            back_populates="events",
            viewonly=True
            )
    users_association: Mapped[List["UserEvent"]] = relationship(
        back_populates="event"
    )

    categories: Mapped[List["Category"]] = relationship(
        secondary="event_category",
        back_populates="events"
    )

    reviews: Mapped[List["Review"]] = relationship(
            back_populates="event"
            )

    admissions: Mapped[List["Admission"]] = relationship(
        secondary="event_admission",
        back_populates="events"
    )

    def get_detail(id: int):
        return db.session.execute(db.select(Event).filter_by(id=id)).one()

    def get_list():
        return db.session.execute(db.select(Event.name)).all()

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True
            )
    name: Mapped[str] = mapped_column(
            String,
            nullable=True, unique=True
            )
    description: Mapped[str] = mapped_column(
            String,
            nullable=True
            )
    approved: Mapped[bool] = mapped_column(
            Boolean,
            default=False
            )

    parent_id = mapped_column(
            Integer,
            ForeignKey("category.id")
            )
    parent: Mapped[List["Category"]] = relationship(
            "Category",
            remote_side=[id],
            backref='children'
            )

    events: Mapped[List["Event"]] = relationship(
        secondary="event_category",
        back_populates="categories"
    )

    def get_detail(id: int):
        return db.session.execute(db.select(Category).filter_by(id=id)).one()

    def get_list():
        return db.session.execute(db.select(Category.name)).all()

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Review(db.Model):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True
            )
    comment: Mapped[str] = mapped_column(
            String,
            nullable=True
            )
    rating: Mapped[int] = mapped_column(
            Integer,
            nullable=False
            )

    user_id: Mapped[int] = mapped_column(
            ForeignKey("user.id")
            )
    user: Mapped["User"] = relationship(
            back_populates="reviews"
            )

    event_id: Mapped[int] = mapped_column(
            ForeignKey("event.id")
            )
    event: Mapped["Event"] = relationship(
            back_populates="reviews"
            )

    def get_detail(id: int):
        return db.session.execute(db.select(Review).filter_by(id=id)).one()

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Admission(db.Model):
    __tablename__ = "admission"

    id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True
            )
    name: Mapped[str] = mapped_column(
            String,
            nullable=True
            )
    amount: Mapped[int] = mapped_column(
            Integer,
            nullable=False
            )

    events: Mapped[List["Event"]] = relationship(
        secondary="event_admission",
        back_populates="admissions"
    )

    def get_detail(id: int):
        return db.session.execute(db.select(Admission).filter_by(id=id)).one()

    def insert(self):
        db.session.add(self)
        db.session.commit()


if __name__ == "__main__":
    print("What are you doing?")
