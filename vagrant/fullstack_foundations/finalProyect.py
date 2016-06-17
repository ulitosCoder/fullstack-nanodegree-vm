#!/usr/bin/python

from flask import Flask,render_template,redirect, url_for, request, flash
from sqlalchemy import create_engine,  desc, asc, Date
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

app = Flask(__name__)



engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}



@app.route('/')
@app.route('/restaurant')
def showRestautans():
    real_restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = real_restaurants)

@app.route('/restaurant/new', methods=['GET','POST'])
def newRestaurant():
    #return "this page will be for maing a new restaurant"
    if request.method == 'POST':
        newRest = Restaurant(name=request.form['name'])
        session.add(newRest)
        session.commit()
        flash("new Restaurant: %s created" % newRest.name)
        return redirect(url_for('showRestautans'))
    else:
        return render_template('newRestaurant.html', restaurants = restaurants)


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    #return "this page will be for editing restaurant %s" % restaurant_id
    try:
        real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':

            oldName = real_restaurant.name
            
            if request.form['name']:
                real_restaurant.name=request.form['name']
            
            session.add(real_restaurant)
            session.commit()
            
            flash("Restaurant %s name changed to: %s " % (oldName, real_restaurant.name))

            return redirect(url_for('showRestautans'))
        else:
            return render_template('editRestaurant.html', restaurant = real_restaurant)
    except IndexError:
        return render_template('notFound.html',itemval = restaurant_id)



@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    #return "this page will be for deleting restaurant %s" % restaurant_id
    return render_template('deleteRestaurant.html', restaurant = restaurant)



@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    #return "This page will show menu of restaurant %s" %restaurant_id
    try: 
        this_rest = restaurants[restaurant_id-1];
        return render_template('menu.html', restaurant = this_rest)
    except IndexError:
        return render_template('notFound.html',itemval = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
    #return "This page will create a new item for restaurant %s" % restaurant_id
    return render_template('newMenuItem.html', restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenuItem(restaurant_id,menu_id):
    #return "This page will edit the item  %s for restaurant %s" % (menu_id , restaurant_id)
    return render_template('editMenuItem.html', restaurant = restaurant, item = item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id,menu_id):
    #return "This page will delete the item  %s for restaurant %s" % (menu_id , restaurant_id)
    return render_template('deleteMenuItem.html', restaurant = restaurant, item = item)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)