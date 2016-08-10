#!/usr/bin/python

from flask import Flask,render_template,redirect, url_for, request, flash
from flask import jsonify
from flask import make_response
from flask import session as login_session


from database_setup import Base, Category, CategoryItem, User

from sqlalchemy import create_engine,  desc, asc, Date
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests


app = Flask(__name__)

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):

    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user    
    except:
        return None
    


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print login_session['state']
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print 'begin gconn', request.args.get('state'), '---' , login_session['state']

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    print 'begin try1'
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
    print 'begin l58'
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    real_userID  = getUserID(login_session['email'])

    if real_userID is None:
        real_userID = createUser(login_session)

    login_session['user_id'] = real_userID

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
   
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        print 'status not 200'
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        print response
        print 'returning'
        return response
        

    


@app.route('/disconnect')
def disconnect():
    print 'disconnecting'
    
    if 'provider' in login_session:
        print 'provider exist'
        if login_session['provider'] == 'google':
            print 'provider google'
            gdisconnect()
            print 'returned from gdisconnect'
            del login_session['gplus_id']
            del login_session['credentials']

        if login_session['provider'] == 'facebook':
            print 'provider facebook'
            fbdisconnect()
            del login_session['facebook_id']

        print 'clearing session info'

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        del login_session['user_id']

        print 'flashing'
        flash('you have been succesfully logged out!')

        print 'redirecting'
        return redirect(url_for('showCategory'))
    else:
        flash('you were not logged in to begin with')
        return redirect(url_for('showCategory'))
 


@app.route('/')
@app.route('/catalog')
def showCategory():
    try:
        local_categories = session.query(Category).all() 
        latestItems = session.query(CategoryItem).join(CategoryItem.category
            ).order_by(desc(CategoryItem.date_added)).limit(10).all()
        
        localUser = None
        try:
            user_id = login_session['user_id']
            print user_id
            localUser = session.query(User).filter_by(id=user_id).one()
            print localUser.name
        except:
            user_id = 0


        return render_template('catalog.html',
            categories = local_categories,
            latest=latestItems,
            user=localUser)

    except Exception, e:
        return e.args 
    
    #print local_categories

    
    


@app.route('/catalog/JSON')
def showCategoryJSON():
    
    local_categories = session.query(Category).all() 

    return jsonify(categories = [i.serialize for i in local_categories])

@app.route('/catalog/new', methods=['GET','POST'])
def newCategory():

    localUser = None
    try:
        user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategory'))

    if request.method == 'POST':
        newCatego = Category(name=request.form['name'],user_id=localUser.id)
        session.add( newCatego )
        session.commit()
        flash("new category %s created" % newCatego.name)
        return redirect(url_for('showCategory'))
    else:
        return render_template('newCatego.html')
    


@app.route('/catalog/<string:category_name>/edit', methods=['GET','POST'])
def editCategory(category_name):

    localUser = None
    try:
        user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategory'))
    
    localCategory = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        oldName = localCategory.name

        if request.form['name']:
            localCategory.name = request.form['name']
            session.add(localCategory)
            session.commit()

            flash("category %s changed to %s" % (oldName, localCategory.name))
            return redirect(url_for('showCategory'))
        else:
            flash("use another name")
            return render_template('editCatego.html',category = localCategory)

    else:
        return render_template('editCatego.html',category = localCategory)


@app.route('/catalog/<string:category_name>/delete', methods=['GET','POST'])
def deleteCategory(category_name):
    
    localUser = None
    try:
        user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategory'))

    localCategory = session.query(Category).filter_by(name=category_name).one()

    if request.method == 'POST':
        
        session.delete(localCategory)
        session.commit()

        flash("Category %s deleted" % category_name)

        return redirect(url_for('showCategory'))
    else:
        return render_template('deleteCatego.html',
            category = localCategory)



@app.route('/catalog/<string:category_name>/JSON')
def showMenuJSON(category_name):

    try:
        localCategory = session.query(Category).filter_by(name=category_name).one() 

        return jsonify(localCategory.serialize)
    except Exception, e:
        return 'Not found'
    
    

@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>/list')
def showCategoryList(category_name):

    try:
    
        localCategory = session.query(Category).filter_by(name=category_name).one()
        local_items = session.query(CategoryItem).filter_by(
            category_id=localCategory.id).all()

        user_id = login_session['user_id']

        localUser = session.query(User).filter_by(id=user_id).one()

        return render_template('categoryList.html', 
                items=local_items, 
                category=localCategory, 
                user=localUser)


    except NoResultFound, e:
        flash("Category %s, not found" % category_name)

        return redirect(url_for('showCategory'))

    

@app.route('/catalog/<string:category_name>/list/new', methods=['GET','POST'])
def newCategoryItem(category_name):

    localUser = None
    try:
        user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategoryList',category_name=category_name))

    localCategory = session.query(Category).filter_by(name=category_name).one()
    #TODO: user user from sesion
    current_user_id = localCategory.user_id
    

    if request.method == 'POST':

        if request.form['name']:
            newItem = CategoryItem(
                name = request.form['name'],
                description = request.form['descript'],
                category_id = localCategory.id,
                user_id = current_user_id
                )

            session.add(newItem)
            session.commit()
            flash('new item %s added' % newItem.name)
        else:
            flash('bad data used')

        return redirect(url_for('showCategoryList',
            category_name=localCategory.name))
    else:
        return render_template('newCategoItem.html',category=localCategory)

@app.route('/catalog/<string:category_name>/list/<string:item_name>/edit',
    methods=['GET','POST'])
def editCategoryItem(category_name,item_name):

    localUser = None
    try:
        user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategoryList',category_name=category_name))

    localCategory = session.query(Category).filter_by(name=category_name).one()
    localItem = session.query(CategoryItem).filter_by(
        category_id=localCategory.id).filter_by(name=item_name).one()
    #TODO check if the logged in user i the cretor
    current_user_id = localCategory.user_id
    localCreator = session.query(User).filter_by(id=localCategory.user_id).one()

    print localItem.name

    if request.method == 'POST':
        change = False
        oldName = localItem.name
        if request.form['name'] and request.form['name'] != oldName:
            localItem.name = request.form['name']
            change = True

        oldDesc = localItem.description
        if request.form['descript'] and request.form['descript'] != localItem.description:
            localItem.description = request.form['descript'] 
            change = True


        if change:
            session.add(localItem)
            session.commit()
            flash('item %s, changed' % localItem.name)
        else:
            flash('No change made')

        
        return redirect(url_for('showCategoryList',
            category_name=localCategory.name))
    else:
        localItem.name
        return render_template('editCategoItem.html',
            category=localCategory,
            item=localItem)

@app.route('/catalog/<string:category_name>/list/<string:item_name>/delete',
    methods=['GET','POST'])
def deleteCategoryItem(category_name,item_name):

    localUser = None
    try:
        user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategoryList',category_name=category_name))

    localCategory = session.query(Category).filter_by(name=category_name).one()
    localItem = session.query(CategoryItem).filter_by(
        category_id=localCategory.id).filter_by(name=item_name).one()
    #TODO check if the logged in user i the cretor
    current_user_id = localCategory.user_id
    localCreator = session.query(User).filter_by(id=localCategory.user_id).one()

    if request.method == 'POST':
        session.delete(localItem)
        session.commit()        

        flash('Item %s deleted' % item_name)
        
        return redirect(url_for('showCategoryList',
            category_name=localCategory.name))
    else:
        return render_template('deleteCategoItem.html',
            category=localCategory,
            item=localItem)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)