from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    uuid = Column(String(32), primary_key=True)
    lastname = Column(Text, nullable=False)
    firstname = Column(Text, nullable=False)
    age = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    email_hash = Column(String(64), nullable=False, index=True, unique=True)
    password = Column(Text, nullable=False)
    role = Column(String(10), nullable=False, default="user")

    tickets = relationship(
        "Ticket", back_populates="user", cascade="all, delete-orphan"
    )


class Ticket(Base):
    __tablename__ = "tickets"

    uuid = Column(String(32), primary_key=True)
    showing = Column(Text, nullable=False)
    user_id = Column(String(32), ForeignKey("users.uuid"), nullable=False)

    user = relationship("User", back_populates="tickets")
