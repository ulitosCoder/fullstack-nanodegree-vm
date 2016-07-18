#!/usr/bin/python

from flask import Flask,render_template,redirect, url_for, request, flash
from flask import jsonify
from flask import make_response
from flask import session as login_session

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

#from database_setup import Restaurant, Base, MenuItem, User

#engine = create_engine('sqlite:///item_calog.db')
#Base.metadata.bind = engine
#DBSession = sessionmaker(bind=engine)
#session = DBSession()


@app.route('/')
@app.route('/category')
def showCategory():
    
    return "Main item catalog"


@app.route('/category/JSON')
def showCategoryJSON():

    return "JSON catalog"
    #restaurants_list = session.query(Restaurant).all()

    #return jsonify(restaurants = [i.serialize for i in restaurants_list])

@app.route('/category/new', methods=['GET','POST'])
def newCategory():

    return "this page will be for making a new category"
    


@app.route('/category/<string:category_name>/edit', methods=['GET','POST'])
def editCategory(restaurant_id):
    
    return "This page is for editing an existing category"



@app.route('/category/<string:category_name>/delete', methods=['GET','POST'])
def deleteCategory(restaurant_id):
    
    return "This page will detele a category"


@app.route('/category/<string:category_name>/JSON')
def showMenuJSON(restaurant_id):

    return "This pages return JSON of a single category"
    

@app.route('/category/<string:category_name>')
@app.route('/category/<string:category_name>/list')
def showCategoryList(restaurant_id):
    return "This page will show category list"


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)