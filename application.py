from flask import Flask, render_template, jsonify
from init_db import db_session as session
from models import *

app = Flask(__name__)


@app.route('/')
def home():
    return render_template(
        'index.html', 
        categories=session.query(Category).all(), 
        items=session.query(Item).all()
        )

@app.route('/catalog/<string:category_name>/items')
def show_category_items(category_name):
    category = session.query(Category).filter_by(name=category_name).first() 
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template(
        'view_items.html',
        items=items,
        category=category,
        num_of_items=len(items)
    )

@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_category_individual_item(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    return render_template('view_individual_item.html',category_name=category_name, item=item)

@app.route('/catalog/category/add')
def add_category():
    return render_template('add_category.html')

@app.route('/catalog/category/<string:category_name>/edit')
def edit_category(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    return render_template('edit_category.html', category_name=category.name)

@app.route('/catalog/category/<string:category_name>/delete')
def delete_category(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    return render_template('delete_category.html')

@app.route('/catalog/item/add')
def add_item():
    categories = session.query(Category).all()
    return render_template('add_item.html', categories=categories)

@app.route('/catalog/item/<string:item_name>/edit')
def edit_item(item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    categories = session.query(Category).all()
    return render_template('edit_item.html', item=item, categories=categories)

@app.route('/catalog/item/<string:item_name>/delete')
def delete_item(item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    return render_template('delete_item.html', item=item)

@app.route('/catalog.json')
def get_json():
    categories = session.query(Category).all()
    return jsonify(category=[i.serialize for i in categories])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)