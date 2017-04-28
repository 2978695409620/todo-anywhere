from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/list/')
def todo_list_all():
    return 'Page for exploring all todo lists'

@app.route('/list/<int:list_id>')
def todo_list(list_id):
    return 'Page for a todo list'

@app.route('/list/<int:list_id>/random')
def random_todo(list_id):
    return 'Page for a random todo item'

if __name__ == '__main__':
    app.run()
