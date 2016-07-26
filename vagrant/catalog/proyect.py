#!/usr/bin/python

from flask import Flask,render_template,redirect, url_for, request, flash
from flask import jsonify
from flask import make_response
from flask import session as login_session


from database_setup import Base, Category, CategoryItem, User

from sqlalchemy import create_engine,  desc, asc, Date
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

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


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    return "this page is for showing login options with state %s" % state


@app.route('/')
@app.route('/category')
def showCategory():
    
    try:
        local_categories = session.query(Category).all()    
        
        return render_template('catalog.html',categories = local_categories)
    except Exception, e:
        return e.args 
    
    #print local_categories

    
    


@app.route('/category/JSON')
def showCategoryJSON():

    return "JSON catalog"
    #restaurants_list = session.query(Restaurant).all()

    #return jsonify(restaurants = [i.serialize for i in restaurants_list])

@app.route('/category/new', methods=['GET','POST'])
def newCategory():

    return "this page will be for making a new category"
    


@app.route('/category/<string:category_name>/edit', methods=['GET','POST'])
def editCategory(category_name):
    
    return "This page is for editing an existing category: %s" % category_name



@app.route('/category/<string:category_name>/delete', methods=['GET','POST'])
def deleteCategory(category_name):
    
    return "This page will detele a category %s"  % category_name


@app.route('/category/<string:category_name>/JSON')
def showMenuJSON(category_name):

    return "This pages return JSON of a single category %s" % category_name
    

@app.route('/category/<string:category_name>')
@app.route('/category/<string:category_name>/list')
def showCategoryList(category_name):
    return "This page will show category list for %s" % category_name

@app.route('/category/<string:category_name>/list/new')
def newCategoryItem(category_name):
    return "This page is for creating a new category item for %s" % category_name

@app.route('/category/<string:category_name>/list/<string:item_name>/edit')
def editCategoryItem(category_name,item_name):
    return "This page is for editing item: %s, of category %s" % ( 
        item_name, category_name)

@app.route('/category/<string:category_name>/list/<string:item_name>/delete')
def deleteCategoryItem(category_name,item_name):
    return "This page is for deleting item: %s, of category %s" % ( 
        item_name, category_name)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)