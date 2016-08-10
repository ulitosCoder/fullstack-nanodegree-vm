#!/usr/bin/python

from flask import Flask,render_template,redirect, url_for, request, flash
from flask import jsonify
from sqlalchemy import create_engine,  desc, asc, Date
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem, User
from flask import session as login_session
import random, string


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



# User Helper Functions
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print 'begin gconn'
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



@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"
    

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

        print 'flashing'
        flash('you have been succesfully logged out!')

        print 'redirecting'
        return redirect(url_for('showRestaurants'))
    else:
        flash('you were not logged in to begin with')
        return redirect(url_for('showRestaurants'))

@app.route('/')
@app.route('/restaurant')
def showRestaurants():
    real_restaurants = session.query(Restaurant).all()


    try:
        user_id = login_session['user_id']
        return render_template('restaurants.html', restaurants = real_restaurants)
    except:
        return render_template('publicrestaurants.html', restaurants = real_restaurants)


@app.route('/restaurant/JSON')
def showRestaurantsJSON():

    restaurants_list = session.query(Restaurant).all()

    return jsonify(restaurants = [i.serialize for i in restaurants_list])

@app.route('/restaurant/new', methods=['GET','POST'])
def newRestaurant():
    #return "this page will be for maing a new restaurant"
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newRest = Restaurant(name=request.form['name'], 
            user_id=login_session['user_id'])
        session.add(newRest)
        session.commit()
        flash("new Restaurant: %s created" % newRest.name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    
    if 'username' not in login_session:
        return redirect('/login')

    try:
        real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':

            oldName = real_restaurant.name
            
            if request.form['name']:
                real_restaurant.name=request.form['name']
            
            session.add(real_restaurant)
            session.commit()
            
            flash("Restaurant %s name changed to: %s " % (oldName, real_restaurant.name))

            return redirect(url_for('showRestaurants'))
        else:
            return render_template('editRestaurant.html', restaurant = real_restaurant)
    except:
        return render_template('notFound.html',itemval = restaurant_id)



@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')

    real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        
        oldName  =  real_restaurant.name

        session.delete(real_restaurant)
        session.commit()


        flash("Restaurant %s deleted :'( " % oldName)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant = real_restaurant)


@app.route('/restaurant/<int:restaurant_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):

    real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item_list = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    return jsonify(menu_items=[i.serialize for i in item_list])
    

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    
    try: 
        real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        local_items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()

        creator = getUserInfo(real_restaurant.user_id)

        
        if 'username' not in login_session or creator.id != login_session['user_id']:
            return render_template('publicmenu.html', 
                items=local_items, 
                restaurant=real_restaurant, 
                creator=creator)
        else:
            return render_template('menu.html', 
                items=local_items, 
                restaurant=real_restaurant, 
                creator=creator)

    except IndexError:
        return render_template('notFound.html',itemval = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    
    if 'username' not in login_session:
        return redirect('/login')

    real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    
    if request.method == 'POST':

        newItem = MenuItem(
            name=request.form['name'], 
            restaurant_id=restaurant_id, 
            user_id=real_restaurant.user_id)
        session.add(newItem)
        session.commit()
        
        flash('new menu item created')

        return redirect(url_for('showMenu', restaurant_id = restaurant_id))

    else:
        return render_template('newMenuItem.html', restaurant = real_restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON', methods=['GET','POST'])
def showMenuItemJSON(restaurant_id,menu_id):

    item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(menu_item = [item.serialize])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id,menu_id):

    if 'username' not in login_session:
        return redirect('/login')

    real_restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()


    if request.method == 'POST':
        oldName = item.name

        item.name = request.form['name']

        session.add(item)
        session.commit()

        flash('new menu item name changed from %s to %s'  % (oldName, item.name) )

        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant = real_restaurant, item = item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    if 'username' not in login_session:
        return redirect('/login')

    real_restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    if request.method == 'POST':

        oldName = item.name

        session.delete(item)
        session.commit()

        flash('new menu item %s deleted' % oldName)

        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', restaurant = real_restaurant, item = item)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)