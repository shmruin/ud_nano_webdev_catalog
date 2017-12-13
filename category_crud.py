from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   jsonify)
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json

from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///categoryItems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# proper google sign-in method
@app.route('/gconnect', methods=['POST'])
def gconnect():
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
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content=Type'] = 'application/json'
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

    # Check if the user is already login
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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

    return redirect(url_for('catalogItemAll'))


# proper google sign-out method
@app.route("/gdisconnect")
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('catalogItemAll'))
    else:
        return redirect(url_for('catalogItemAll'))


@app.route('/')
def catalogItemAll():
    # Read All Category Items - plus after login processs
    categories = session.query(Category).all()
    latestItems = session.query(CategoryItem).order_by(
        desc(CategoryItem.time_updated))
    latestCategories = []
    for i in latestItems:
        latestCategories.append(session.query(
            Category).filter_by(id=i.category_id).first())
    # When accessing public page
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in range(32))
        login_session['state'] = state
        return render_template('publicCatalogItemAll.html',
                               categories=categories,
                               latest=zip(latestCategories, latestItems),
                               STATE=state)
    # When accessing admin page
    else:
        return render_template('catalogItemAll.html',
                               categories=categories,
                               latest=zip(latestCategories, latestItems))


@app.route('/catalog/<string:category_name>/items')
def catalogItemLists(category_name):
    # Read category item lists
    categories = session.query(Category).all()
    associatedCategory = session.query(
        Category).filter_by(name=category_name).first()
    associatedItems = session.query(CategoryItem).filter_by(
        category_id=associatedCategory.id).all()
    # When accessing public page
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in range(32))
        login_session['state'] = state
        return render_template('publicCatalogItemLists.html',
                               categories=categories,
                               associatedCategory=associatedCategory,
                               associatedItems=associatedItems,
                               STATE=state)
    # When accessing admin page
    else:
        return render_template('catalogItemLists.html',
                               categories=categories,
                               associatedCategory=associatedCategory,
                               associatedItems=associatedItems)


@app.route('/catalog/<string:category_name>/<string:item_name>',
           methods=['GET', 'POST'])
def catalogItemDesc(category_name, item_name):
    # Read a category item description
    categories = session.query(Category).all()
    associatedCategory = session.query(
        Category).filter_by(name=category_name).first()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    # When accessing public page
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in range(32))
        login_session['state'] = state
        return render_template('publicCatalogItemDesc.html',
                               associatedCategory=associatedCategory,
                               item=item,
                               STATE=state)
    # When accessing admin page
    else:
        return render_template('catalogItemDesc.html', item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def catalogItemAdd():
    # Edit a category item - Only after login
    if 'username' not in login_session:
        return redirect(url_for('catalogItemAll'))
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form.get('category_selected')).first()
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category.id,
                               username=login_session['username'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalogItemAll'))
    else:
        categories = session.query(Category).all()
        return render_template('catalogItemAdd.html', categories=categories)


@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def catalogItemEdit(item_name):
    # Edit a category item - Only after login
    if 'username' not in login_session:
        return redirect(url_for('catalogItemAll'))
    editItem = session.query(CategoryItem).filter_by(name=item_name).first()
    if editItem.username != login_session['username']:
        return "<script>function myFunction() \
                {alert('You are not authorized to edit this item. \
                Please create your own item in order to edit. \
                Now redirect to add your own item...'); \
                window.location.href='/catalog/add'} \
                </script><body onload='myFunction()''>"
    print(item_name)
    print(editItem)
    if request.method == 'POST':
        editItem.name = request.form['name']
        editItem.description = request.form['description']
        editItemCategory = session.query(Category).filter_by(
            name=request.form.get('category_selected')).first()
        editItem.category_id = editItemCategory.id
        session.add(editItem)
        session.commit()
        return redirect(url_for('catalogItemAll'))
    else:
        category = session.query(Category).all()
        item = session.query(CategoryItem).filter_by(name=item_name).first()
        return render_template('catalogItemEdit.html',
                               category=category,
                               item=item)


@app.route('/catalog/<string:item_name>/delete',  methods=['GET', 'POST'])
def catalogItemDelete(item_name):
    # Delete a category item - Only after login
    if 'username' not in login_session:
        return redirect(url_for('catalogItemAll'))
    deleteItem = session.query(CategoryItem).filter_by(name=item_name).first()
    if deleteItem.username != login_session['username']:
        return "<script>function myFunction() \
                {alert('You are not authorized to delete this item. \
                Please create your own item in order to delete. \
                Now redirect to main page...'); \
                window.location.href='/'} \
                </script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('catalogItemAll'))
    else:
        item = session.query(CategoryItem).filter_by(name=item_name).first()
        return render_template('catalogItemDelete.html', item=item)


@app.route('/catalog.json')
def catalogJSON():
    # Return category JSON
    categories = session.query(Category).all()
    items = session.query(CategoryItem).all()
    category = [i.serialize for i in categories]

    for idx, var in enumerate(categories):
        itemArray = []
        for j in items:
            if j.category_id == var.id:
                itemArray.append(j.serialize)
        category[idx]['item'] = itemArray

    return jsonify(Category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
