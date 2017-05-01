import os

from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from model import Base, TodoList, TodoItem

from flask_heroku import Heroku

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/todo-anywhere'
heroku = Heroku(app)
db = SQLAlchemy(app)

session = db.session

ERROR_LIST_NOT_FOUND = 'Todo list not found'
ERROR_ITEM_NOT_FOUND = 'Todo item not found'
ERROR_LIST_CREATION_FAILED = 'Unable to create todo list'
ERROR_ITEM_CREATION_FAILED = 'Unable to create todo item'
ERROR_INVALID_PARAMS = 'Invalid params'


@app.route('/', methods=['GET'])
def landing():
    return render_template('lists.html')

@app.route('/list/', methods=['GET'])
def todo_list_all():
    return 'Page for exploring all todo lists'

@app.route('/list/<int:list_id>/', methods=['GET'])
def todo_list(list_id):
    return 'Page for a todo list'

@app.route('/list/<int:list_id>/random/', methods=['GET'])
def random_todo(list_id):
    return 'Page for a random todo item'

# --------------------------------- API Routes for todo lists ----------------------------------

# Get all todo lists
@app.route('/api/list/', methods=['GET'])
def api_list_all():
	lists = session.query(TodoList)
	return_dict = {'todo_lists': [l.serialize for l in lists]}
	return jsonify(success=True, content=return_dict)

# Create a todo list
@app.route('/api/list/', methods=['POST'])
def api_create_list():
	if request.form['name']:
		newList = TodoList(name=request.form['name'])
		session.add(newList)
		session.commit()
		return_dict = {'list_created': newList.id}
		return jsonify(success=True, content=return_dict)
	return jsonify(success=False, message=ERROR_INVALID_PARAMS)

# Get info for a specific list
@app.route('/api/list/<int:list_id>/', methods=['GET'])
def api_get_list_info(list_id):
	todo_list = session.query(TodoList).filter(TodoList.id == list_id).one_or_none()
	if todo_list != None:
		todo_name = todo_list.name
		todo_items = session.query(TodoItem).filter(TodoItem.list_id == list_id).all()
		return_dict = {'name': todo_list.name, 'items': [item.serialize for item in todo_items]}
		return jsonify(success=True, content=return_dict)
	return jsonify(success=False, message=ERROR_LIST_NOT_FOUND)

# Edit a todo list
@app.route('/api/list/<int:list_id>/', methods=['PUT'])
def api_edit_list(list_id):
	if request.form['name']:
		todo_list = session.query(TodoList).filter(TodoList.id == list_id).one_or_none
		if todo_list != None:
			todo_list.name = request.form['name']
			session.commit()
			return jsonify(success=True)
		else:
			return jsonify(success=False, message=ERROR_LIST_NOT_FOUND)
	return jsonify(success=False, message=ERROR_INVALID_PARAMS)

# Delete a todo list, also deletes all of its todo items
@app.route('/api/list/<int:list_id>/', methods=['DELETE'])
def api_delete_list(list_id):
	todo_list = session.query(TodoList).filter(TodoList.id == list_id).one()
	if todo_list != None:
		todo_items = session.query(TodoItem).filter(TodoItem.list_id == list_id).all()
		for item in todo_items:
			session.delete(item)
		session.commit()
		session.delete(todo_list)
		session.commit()
		return_dict = {'list_id_deleted': todo_list.id}
		return jsonify(success=True, content=return_dict)
	return jsonify(success=False, message=ERROR_LIST_NOT_FOUND)

# --------------------------------- API Routes for list items ---------------------------------

# Create a todo item for a todo list
@app.route('/api/list/<int:list_id>/item/', methods=['POST'])
def api_create_list_item(list_id):
	if request.form['description']:
		newItem = TodoItem(description=request.form['description'], list_id=list_id)
		session.add(newItem)
		session.commit()
		return_dict = {'item_id': newItem.id}
		return jsonify(success=True, content=return_dict)
	return jsonify(success=False, message=ERROR_INVALID_PARAMS)

# Get info about a todo item
@app.route('/api/list/<int:list_id>/item/<int:item_id>/', methods=['GET'])
def api_get_list_item(list_id, item_id):
	item = session.query(TodoItem).filter(TodoItem.list_id == list_id, TodoItem.id == item_id).one_or_none()
	if item != None:
		return_dict = item.serialize
		return jsonify(success=True, content=return_dict)
	return jsonify(success=False, message=ERROR_ITEM_NOT_FOUND)

# Edit a todo item
@app.route('/api/list/<int:list_id>/item/<int:item_id>/', methods=['PUT'])
def api_edit_list_item(list_id, item_id):
	if request.form['description']:
		todo_item = session.query(TodoItem).filter(TodoItem.id == item_id, TodoItem.list_id == list_id).one_or_none()
		if todo_item != None:
			todo_item.description = request.form['description']
			session.commit()
			return_dict = {'item_id': item_id}
			return jsonify(success=True, content=return_dict)
		return jsonify(success=False, message=ERROR_ITEM_NOT_FOUND)
	return jsonify(success=False, message=ERROR_INVALID_PARAMS)

# Delete a todo item
@app.route('/api/list/<int:list_id>/item/<int:item_id>/', methods=['DELETE'])
def api_delete_list_item(list_id, item_id):
	todo_item = session.query(TodoItem).filter(TodoItem.id == item_id, TodoItem.list_id == list_id).one()
	if todo_item != None:
		session.delete(todo_item)
		session.commit()
		return_dict = {'item_id': todo_item.id}
		return jsonify(success=True, content=return_dict)
	return jsonify(success=False, message=ERROR_ITEM_NOT_FOUND)


if __name__ == '__main__':
    app.run()
