import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class TodoList(Base):
	__tablename__ = 'todo_list'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(250), nullable=False)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
		}

class TodoItem(Base):
	__tablename__ = 'todo_item'

	id = Column(Integer, primary_key=True, autoincrement=True)
	description = Column(String(250), nullable=False)
	list_id = Column(Integer, ForeignKey('todo_list.id'), nullable=False)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'description': self.description,
		}


engine = create_engine('postgresql://localhost/todo-anywhere')


Base.metadata.create_all(engine)
