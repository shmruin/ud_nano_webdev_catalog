from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

from flask import session as login_session
import random, string

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


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" % login_session['state']

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
    result = json.loads(h.request(url, 'GET')[1])
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
        response = make_response(json.dumps('Current user is already connected.'), 200)
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
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/')
def catalogItemAll():
    #TODO: Read All Category Items - plus after login processs
    categories = session.query(Category).all()
    latestItems = session.query(CategoryItem).order_by(desc(CategoryItem.time_updated))
    return render_template('catalogItemAll.html', categories=categories, latestItems=latestItems)


@app.route('/catalog/<string:category_name>/items')
def catalogItemLists(category_name):
    #TODO: Read category item lists
    categories = session.query(Category).all()
    associatedItems = session.query(CategoryItem).filter_by(category_name=category_name).all()
    return render_template('catalogItemLists.html', categories=categories, selectedCategory=category_name, associatedItems=associatedItems)


@app.route('/catalog/<string:category_name>/<string:item_name>', methods=['GET', 'POST'])
def catalogItemDesc(category_name, item_name):
    #TODO: Read a category item description - plus after login process
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    return render_template('catalogItemDesc.html', item=item)


@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def catalogItemEdit(item_name):
    #TODO: Edit a category item - Only after login
    category = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item_name).first()
    return render_template('catalogItemEdit.html', category=category, item=item)


@app.route('/catalog/<string:item_name>/delete',  methods=['GET', 'POST'])
def catalogItemDelete(item_name):
    #TODO: Delete a category item - Only after login
    item = session.query(CategoryItem).filter_by(name=item_name).first()
    return render_template('catalogItemDelete.html', item=item)


@app.route('/catalog.json')
def catalogJSON():
    #TODO: Return category JSON
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
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
