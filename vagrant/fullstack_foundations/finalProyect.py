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

@app.route('/')
@app.route('/restaurant')
def showRestautans():
	return "This page will show restaurants"

@app.route('/restaurant/new')
def newRestaurant():
	return "this page will be for maing a new restaurant"


@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
	return "this page will be for editing restaurant %s" % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
	return "this page will be for deleting restaurant %s" % restaurant_id



@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	return "This page will show menu of restaurant %s" %restaurant_id

@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
	return "This page will create a new item for restaurant %s" % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenuItem(restaurant_id,menu_id):
	return "This page will edit the item  %s for restaurant %s" % (menu_id , restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id,menu_id):
	return "This page will delete the item  %s for restaurant %s" % (menu_id , restaurant_id)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)