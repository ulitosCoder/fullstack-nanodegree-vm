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
    """ Creates a new user in the database

    Args:
        login_session: The dictionary that contains the data of th new user,
            the data is taken from the the authetication system
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ Get the info of a user from the database
        Args: 
            user_id: user id
    """
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user    
    except:
        return None
    

def getUserID(email):
    """ Get the user id of a given email address

        Args:
            email: email addres of the user to look for
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/login')
def showLogin():
    """ Shows login page

        This route creates a one time token for protection and shows the
        login page to ask the user for credentials 
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print login_session['state']
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Authenticates a User using Google+ API

           This routes gets the POST request params, autheticates a user and
        creates the session variables used for the user, then the user can
        create, delete and edit items, but only items created by the user
    """
    

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
    """ Disconnectos from a Google+ account

        Use the session token to revoke the permissions, effectively login out
        the current user
    """
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
    """ Terminates a User session

        Deletes the variables of the login_session, so the session itself is no
        longer valid, in other words terminates the usser session

    """

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
    """ Displays the main catalog

        Prints the list of categories contained in the database, if user session
        is active, the user can create new categories, for those categories
        created by the current user, he/she can delete or edit such categories,
        and create, edit, delete items inside the user's categories.
    """
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

    
    
@app.route('/catalog.json')
@app.route('/catalog/json')
def showCatalogJSON():
    """ Returns a JSON string of the categories

        Retusr a JSON string that contains all the categories in the database
    """
    local_categories = session.query(Category).all() 

    return jsonify(categories = [i.serialize for i in local_categories])

@app.route('/catalog/new', methods=['GET','POST'])
def newCategory():
    """ Creates a new category

        This route handles the creatin of a new catgory in the data base,
        first renders the web form to ask for a name, the use that infor
        to add the new category.

        A user session needs to be active or this function won't create a new
        category
    """
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

    """ Edits an existen category

        This route modifies the category named in category_name, 
        to reach here a user session needs to be active,
        in the category list, only those coteagories created by the current
        user display the edit link.
       
        Args:
            category_name: name of the category to edit
    """

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
    """ Deletes a category

        This route deletes the category named category_name,
        A user session need to be active, only those coteagories created by 
        the current user display the delete link.

        Args:
            category_name: name of the category to delete
    """
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
def showCategoryJSON(category_name):
    """ Retursn a JSON string of a given category

        Args:
            category_name: name of the category to look for
    """
    try:
        localCategory = session.query(Category).filter_by(name=category_name).one() 

        return jsonify(localCategory.serialize)
    except Exception, e:
        return 'Not found'
    
    

@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>/list')
@app.route('/catalog/<string:category_name>/items')
def showCategoryList(category_name):
    """ Display the items list of a category

        Renders the web page of a given category, if there's a valid session and
        the current user is the owner of this category, the paga will display
        options to add/edit/delete items for this category.

        Args:
            category_name: name of the category to look for

    """
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

    
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showCategoryItem(category_name,item_name):

    localUser = None
    try:
        current_user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=current_user_id).one()
    except Exception, e:
        localUser = None

    localCategory = session.query(Category).filter_by(name=category_name).one()
    localItem = session.query(CategoryItem).filter_by(
              category_id=localCategory.id).filter_by(name=item_name).one()

    return render_template('showItem.html',
        category=localCategory,
        item=localItem,
        user=localUser)


@app.route('/catalog/<string:category_name>/list/new', methods=['GET','POST'])
def newCategoryItem(category_name):
    """ Creates a new item
        
        Add a new item in the database, linked to a category and to a user.
        A valid session need to be active, only the user who owns this category
        can add new items to it.

        Args:
            category_name: name of the category for the new item
    """
    current_user_id = None
    localUser = None
    try:
        current_user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=current_user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategoryList',category_name=category_name))

    localCategory = session.query(Category).filter_by(name=category_name).one()

    if localCategory.user_id != localUser.id:
        flash('Only the owner can modify this list')
        return redirect(url_for('showCategoryList',
            category_name=localCategory.name))        

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
    """ Modifies an existing item
        
        Changes some values of an item in the database.
        A valid session need to be active, only the user who owns this category
        can make modifications to the items

        Args:
            category_name: name of the category which the items belongs
            item_name: name of the item to modify
    """

    localUser = None
    try:
        current_user_id = login_session['user_id']
        localUser = session.query(User).filter_by(id=current_user_id).one()
    except Exception, e:
        flash("You must log in first")
        return redirect(url_for('showCategoryList',category_name=category_name))

    localCategory = session.query(Category).filter_by(name=category_name).one()
    localItem = session.query(CategoryItem).filter_by(
        category_id=localCategory.id).filter_by(name=item_name).one()

    if localCategory.user_id != localUser.id:
        flash('Only the owner can modify this list')
        return redirect(url_for('showCategoryList',
            category_name=localCategory.name))  

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
    """ Deletes an existing item
        
        Removes an item from the database.
        A valid session need to be active, only the user who owns this category
        can delete  the items

        Args:
            category_name: name of the category which the items belongs
            item_name: name of the item to delete
    """

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