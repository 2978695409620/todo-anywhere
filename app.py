import os

from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, TodoList, TodoItem

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret_key'

DATABASE_URI = os.environ.get("DATABASE_URL", 'postgresql://localhost/todo-anywhere')
engine = create_engine(DATABASE_URI)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

ERROR_LIST_NOT_FOUND = 'Todo list not found'
ERROR_ITEM_NOT_FOUND = 'Todo item not found'
ERROR_LIST_CREATION_FAILED = 'Unable to create todo list'
ERROR_ITEM_CREATION_FAILED = 'Unable to create todo item'
ERROR_INVALID_PARAMS = 'Invalid params'


@app.route('/', methods=['GET'])
def landing():
    return render_template('lists.html')

@app.route('/list/', methods=['GET'])
def show_all_lists():
    lists = session.query(TodoList).order_by(asc(TodoList.name))
    return render_template('todoLists.html', lists=lists)

@app.route('/list/new/', methods=['GET', 'POST'])
def create_list():
	if request.method == 'GET':
		return render_template('createList.html')
	else:
		if request.form['name'] and request.form['name'] != '':
			newList = TodoList(name=request.form['name'])
			session.add(newList)
			flash('New List Created Successfully')
			session.commit()
			return redirect(url_for('show_all_lists'))
		else:
			status = 'Must enter a valid name'
			return render_template('createList.html', status=status)

@app.route('/list/<int:list_id>/', methods=['GET'])
@app.route('/list/<int:list_id>/item/', methods=['GET'])
def show_list(list_id):
	todoList = session.query(TodoList).filter(TodoList.id == list_id).one_or_none()
	if todoList:
		todoItems = session.query(TodoItem).filter(TodoItem.list_id == list_id).all()
		return render_template('showList.html', todoList=todoList, todoItems=todoItems)
	else:
		flash('No list found')
		return redirect(url_for('show_all_lists'))
	

@app.route('/list/<int:list_id>/edit/', methods=['GET', 'POST'])
def edit_list(list_id):
	todoList = session.query(TodoList).filter_by(id=list_id).one_or_none()
	if todoList:
		if request.method == 'GET':
			return render_template('editList.html', todoList=todoList)
		else:
			if request.form['name']:
				todoList.name = request.form['name']
				session.commit()
				flash('List Edited Successfully')
				return redirect(url_for('show_all_lists'))
	else:
		flash('No list found')
		return redirect(url_for('show_all_lists'))

@app.route('/list/<int:list_id>/delete/', methods=['GET', 'POST'])
def delete_list(list_id):
	todoList = session.query(TodoList).filter_by(id=list_id).one_or_none()
	if todoList:
		if request.method == 'GET':
			return render_template('deleteList.html', todoList=todoList)
		else:
			todoItems = session.query(TodoItem).filter(TodoItem.list_id == list_id).all()
			for item in todoItems:
				session.delete(item)
			session.commit()
			session.delete(todoList)
			session.commit()
			flash('List Deleted Successfully')
			return redirect(url_for('show_all_lists'))
	else:
		flash('No list found')
		return redirect(url_for('show_all_lists'))

@app.route('/list/<int:list_id>/item/<int:item_id>/', methods=['GET'])
def show_item(list_id, item_id):
	todoList = session.query(TodoList).filter(TodoList.id == list_id).one_or_none()
	if not todoList:
		flash('No list found')
		return redirect(url_for('show_all_lists'))

	todoItem = session.query(TodoItem).filter(TodoItem.list_id == list_id, TodoItem.id == item_id).one_or_none()
	if not todoItem:
		flash('No item found')
		return redirect(url_for('show_list', list_id=list_id))

	todoItems = session.query(TodoItem).filter(TodoItem.list_id == list_id).all()
	return render_template('showItem.html', todoItem=todoItem)

@app.route('/list/<int:list_id>/create/', methods=['GET', 'POST'])
def create_item(list_id):
	todoList = session.query(TodoList).filter(TodoList.id == list_id).one_or_none()
	if todoList:
		if request.method == 'GET':
			return render_template('createItem.html', list_id=todoList.id)
		else:
			item = TodoItem(description=request.form['description'], list_id=list_id)
			session.add(item)
			session.commit()
			flash('New item successfully created')
			return redirect(url_for('show_list', list_id=list_id))
	else:
		flash('No list found')
		return redirect(url_for('show_all_lists'))

@app.route('/list/<int:list_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(list_id, item_id):
	todoList = session.query(TodoList).filter(TodoList.id == list_id).one_or_none()
	if not todoList:
		flash('No list found')
		return redirect(url_for('show_all_lists'))

	todoItem = session.query(TodoItem).filter(TodoItem.list_id == list_id, TodoItem.id == item_id).one_or_none()
	if not todoItem:
		flash('No item found')
		return redirect(url_for('show_list', list_id=list_id))

	if request.method == 'GET':
		return render_template('editItem.html', todoList=todoList, todoItem=todoItem)
	else:
		if request.form['description']:
			todoItem.description = request.form['description']
			session.commit()
			flash('Item Edited Successfully')
			return redirect(url_for('show_list', list_id=list_id))

@app.route('/list/<int:list_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def delete_item(list_id, item_id):
	todoList = session.query(TodoList).filter(TodoList.id == list_id).one_or_none()
	if not todoList:
		flash('No list found')
		return redirect(url_for('show_all_lists'))

	todoItem = session.query(TodoItem).filter(TodoItem.list_id == list_id, TodoItem.id == item_id).one_or_none()
	if not todoItem:
		flash('No item found')
		return redirect(url_for('show_list', list_id=list_id))

	if request.method == 'GET':
		return render_template('deleteItem.html', todoList=todoList, todoItem=todoItem)
	else:
		session.delete(todoItem)
		session.commit()
		flash('List Deleted Successfully')
		return redirect(url_for('show_list', list_id=list_id))
		

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
