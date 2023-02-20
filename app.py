from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

basedir = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

api = Api(app, doc='/', title='A book API', description='A simple API for books usimg Flask Restx')

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(25), nullable = False)
    author = db.Column(db.String(30), nullable = False)
    date_added = db.Column(db.DateTime(), default = datetime.utcnow)

    def __repr__(self):
        return self.title

book_model = api.model(
    'Book',
    {
        'id':fields.Integer(),
        'title':fields.String(),
        'author':fields.String(),
        'date_added':fields.String()
    }
)

@api.route('/books')
class Books(Resource):
    @api.marshal_list_with(book_model, code=200, envelope='books')
    def get(self):
        '''Get all books'''
        books = Book.query.all()
        return books

    @api.marshal_with(book_model, code=201, envelope='book')
    @api.doc(params={'title':'Add title here', 'author':'Add author here'})
    def post(self):
        '''Add a new book'''
        data = request.get_json()

        title = data.get('title')
        author = data.get('author')

        new_book = Book(title=title, author=author)

        db.session.add(new_book)

        db.session.commit()

        return new_book


@api.route('/book/<int:id>')
class BookResources(Resource):
    @api.marshal_with(book_model, code=200, envelope='book')
    def get(self, id):
        '''Get a book using its id'''
        book = Book.query.get_or_404(id)
        return book


    @api.marshal_with(book_model, code=200, envelope='book')
    def put(self, id):
        '''Update a book'''
        update_book = Book.query.get_or_404(id)

        data=request.get_json

        update_book.title = data.get('title')
        update_book.author = data.get('author')

        db.session.commit()

        return update_book, 200

    @api.marshal_with(book_model, code=200, envelope='deleted_book') 
    def delete(self, id):
        '''Delete a book'''
        delete_book = Book.query.get_or_404(id)

        db.session.delete(delete_book)
        db.session.commit()

        return delete_book, 200

@app.shell_context_processor
def make_shell_context():
    return {
        'db' : db,
        'Book' : Book
    }

if __name__ == '__main__':
    app.run(debug=True)    