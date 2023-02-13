from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Books(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    year = Column(Integer, index=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id"))

    publisher = relationship("Publishers", back_populates="books")


class Publishers(Base):
    __tablename__ = "publishers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

    books = relationship("Books", back_populates="publisher")


class Members(Base):
    __tablename__ = "members"

    id = Column(String, primary_key=True, index=True)
    subject_id = Column(String, index=True)
    publisher_id = Column(Integer, ForeignKey("publishers.id"))

    publisher = relationship("Publishers", back_populates="members")
