#!/usr/bin/python

from flask import Flask,render_template,redirect, url_for, request, flash
from flask import jsonify
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
#restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
#restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
#items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
#item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}



@app.route('/')
@app.route('/restaurant')
def showRestautans():
    real_restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = real_restaurants)


@app.route('/restaurant/JSON')
def showRestautansJSON():

    restaurants_list = session.query(Restaurant).all()

    return jsonify(restaurants = [i.serialize for i in restaurants_list])

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
    except:
        return render_template('notFound.html',itemval = restaurant_id)



@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        
        oldName  =  real_restaurant.name

        session.delete(real_restaurant)
        session.commit()


        flash("Restaurant %s deleted :'( " % oldName)
        return redirect(url_for('showRestautans'))
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
        return render_template('menu.html', restaurant = real_restaurant, items = local_items)
    except IndexError:
        return render_template('notFound.html',itemval = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    
    real_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    
    if request.method == 'POST':

        newItem = MenuItem(
            name=request.form['name'], restaurant_id=restaurant_id)
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