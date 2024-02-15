from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,Table
from sqlalchemy.orm import relationship

user_tag_association = Table(
    'user_tag_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class Users(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True,index=True)
    email=Column(String,unique=True)
    username=Column(String,unique=True)
    first_name=Column(String)
    last_name=Column(String)
    hashed_password=Column(String)
    is_active=Column(Boolean,default=True)
    role= Column(String)
    tags = relationship("Tag", secondary=user_tag_association, backref="users")

class Todos(Base):
    __tablename__='todos'
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean,default=False)
    owner_id = Column(Integer,ForeignKey("users.id"))

