from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from init_db import db_session as session
from models import *

app = Flask(__name__)

# MOCK

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
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template(
        'view_items.html',
        items=items,
        category=category,
        num_of_items=len(items),
        categories=categories
    )

@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_category_individual_item(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    return render_template('view_individual_item.html',category_name=category_name, item=item)

@app.route('/catalog/item/add', methods=['GET', 'POST'])
def add_item():
    categories = session.query(Category).all()
    if request.method == 'GET':
        return render_template('add_item.html', categories=categories)
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        if not(title and category):
            return jsonify("Title and category are mandatory to create new item")
        else:
            item_names = set(name for (name,) in session.query().with_entities(Item.name))
            category_names = set(cat.name for cat in categories)
            if category not in category_names:
                return jsonify("Category {} does not exist".format(category))
            elif title in item_names:
                return jsonify("Item {} already exist".format(title))
            else:
                user = session.query(User).one()
                item = Item(
                    name=title,
                    description=description,
                    category=session.query(Category).filter_by(name=category).first(),
                    user=user
                )

                session.add(item)
                session.commit()
                print("Item has been edited")
                return redirect(url_for('home'))
    else:
        return jsonify("HTTP method is required to be GET or POST")

@app.route('/catalog/item/<string:item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    categories = session.query(Category).all()
    if request.method == 'GET':
        return render_template('edit_item.html', item=item, categories=categories)
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        if not(title and category):
            return jsonify("Title and category are mandatory to edit item")
        else:
            item_names = set(name for (name,) in session.query().with_entities(Item.name))
            category_names = set(cat.name for cat in categories)
            if category not in category_names:
                return jsonify("Category {} does not exist".format(category))
            elif title != item_name and title in item_names:
                return jsonify("Item {} already exist".format(title))
            else:
                item = session.query(Item).filter_by(name=item_name).first()
                item.name = title
                item.description = description
                item.category = session.query(Category).filter_by(name=category).first()

                session.add(item)
                session.commit()
                print("Item has been edited")
                return redirect(url_for('home'))
    else:
        return jsonify("HTTP method is required to be GET or POST")

@app.route('/catalog/item/<string:item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    if request.method == 'GET':
        item = session.query(Item).filter_by(name=item_name).first()
        return render_template('delete_item.html', item=item)
    elif request.method == 'POST':
        title = request.form['title']

        if not title:
            return jsonify("Cannot delete item without title")
        else:
            item_names = set(name for (name,) in session.query().with_entities(Item.name))
            if title not in item_names:
                return jsonify("Item {} does not exist".format(title))
            else:
                item = session.query(Item).filter_by(name=title).first()
                session.delete(item)
                session.commit()
                print("Item has been deleted")
                return redirect(url_for('home'))
    else:
        return jsonify("HTTP method is required to be GET or POST")

@app.route('/catalog.json')
def get_json():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)