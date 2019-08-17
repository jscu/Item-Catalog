from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session as login_session
import random, string
from init_db import db_session as session
from models import *

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.secret_key = json.loads(open('client_secrets.json', 'r').read())['web']['client_secret'] 
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

def is_user_logged_in():
    return 'username' in login_session

def is_item_owner(item):
    return item.user.name == login_session.get('username') and item.user.email == login_session.get('email')

def get_all_categories():
    return session.query(Category).all() 

def get_all_items():
    return session.query(Item).all()

def get_categories_by_filters(**args):
    return session.query(Category).filter_by(**args).all()

def get_items_by_filters(**args):
    return session.query(Item).filter_by(**args).all()

def get_user_by_filters(**args):
    return session.query(Item).filter_by(**args).first()

def get_categories_by_filters_or_default(**args):
    return get_categories_by_filters(**args) or [None]

def get_items_by_filters_or_default(**args):
    return get_items_by_filters(**args) or [None]

@app.route('/')
def home():
    return render_template(
        'index.html', 
        categories=get_all_categories(),
        items=get_all_items(),
        is_user_logged_in=is_user_logged_in()
    )

@app.route('/catalog/<string:category_name>/items')
def show_category_items(category_name):
    categories = get_all_categories()
    category = get_categories_by_filters_or_default(name=category_name)[0]
    items = []

    if not category:
        flash('Category {} does not exist'.format(category_name))
        category_name=None
    else:
        items = get_items_by_filters(category_id=category.id)

    return render_template(
        'view_items.html',
        items=items,
        category_name=category_name,
        num_of_items=len(items),
        categories=categories
    )

@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_category_individual_item(category_name, item_name):
    category = get_categories_by_filters_or_default(name=category_name)[0]
    item = None
    is_editable_item = False

    if not category:
        flash('Category {} does not exist'.format(category_name))
        category_name=None
    else:
        item = get_items_by_filters_or_default(name=item_name)[0]
        
        if not item:
            flash('Item {} does not exist'.format(item_name))
        else:
            is_editable_item = is_item_owner(item)

    return render_template(
        'view_individual_item.html',
        category_name=category_name, 
        item=item,
        is_editable_item=is_editable_item
    )

@app.route('/catalog/item/add', methods=['GET', 'POST'])
def add_item():
    if 'username' not in login_session:
        flash('You have not logged in yet. Redirected you to login page')
        redirect('/login')

    categories = get_all_categories()
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
                # user = session.query(User).one()
                user = get_user_by_filters(name=login_session['username'])
                if not user:
                    return jsonify("Cannot create new items with invalid user credentials")

                item = Item(
                    name=title,
                    description=description,
                    category=get_categories_by_filters(name=category)[0],
                    user=user
                )

                session.add(item)
                session.commit()
                return redirect(url_for('home'))
    else:
        return jsonify("HTTP method is required to be GET or POST")

@app.route('/catalog/item/<string:item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    if 'username' not in login_session:
        flash('You have not logged in yet. Redirected you to login page')
        redirect('/login')

    item = get_items_by_filters_or_default(name=item_name)[0]

    if not item:
        return jsonify("Cannot edit item because item {} does not exist".format(item_name))

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
                item = get_items_by_filters_or_default(name=item_name)[0]
                if not is_item_owner(item):
                    return jsonify("Cannot edit item with invalid credentials")

                item.name = title
                item.description = description
                item.category = get_categories_by_filters_or_default(name=category)[0]

                session.add(item)
                session.commit()
                flash('Item has been edited')
                return redirect(url_for('home'))
    else:
        return jsonify("HTTP method is required to be GET or POST")

@app.route('/catalog/item/<string:item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    if 'username' not in login_session:
        flash('You have not logged in yet. Redirected you to login page')
        redirect('/login')

    item = get_items_by_filters_or_default(name=item_name)[0]

    if not item:
        return jsonify("Cannot delete item because item {} does not exist".format(item_name))

    if request.method == 'GET':
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
                item = get_items_by_filters_or_default(name=item_name)[0]
                if not is_item_owner(item):
                    return jsonify("Cannot delete item with invalid credentials")

                session.delete(item)
                session.commit()
                flash("Item has been deleted")
                return redirect(url_for('home'))
    else:
        return jsonify("HTTP method is required to be GET or POST")

@app.route('/catalog.json')
def get_json():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])

@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output

@app.route('/gdisconnect')
def logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        # return response
        flash('You are logged out succesfully')
        return redirect(url_for('home'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)