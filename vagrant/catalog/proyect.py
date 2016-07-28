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

    if request.method == 'POST':
        newCatego = Category(name=request.form['name'],user_id=1)
        session.add( newCatego )
        session.commit()
        flash("new category %s created" % newCatego.name)
        return redirect(url_for('showCategory'))
    else:
        return render_template('newCatego.html')
    


@app.route('/category/<string:category_name>/edit', methods=['GET','POST'])
def editCategory(category_name):
    
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


@app.route('/category/<string:category_name>/delete', methods=['GET','POST'])
def deleteCategory(category_name):
    
    localCategory = session.query(Category).filter_by(name=category_name).one()

    if request.method == 'POST':
        
        session.delete(localCategory)
        session.commit()

        flash("Category %s deleted" % category_name)

        return redirect(url_for('showCategory'))
    else:
        return render_template('deleteCatego.html',
            category = localCategory)



@app.route('/category/<string:category_name>/JSON')
def showMenuJSON(category_name):

    return "This pages return JSON of a single category %s" % category_name
    

@app.route('/category/<string:category_name>')
@app.route('/category/<string:category_name>/list')
def showCategoryList(category_name):

    localCategory = session.query(Category).filter_by(name=category_name).one()
    local_items = session.query(CategoryItem).filter_by(
        category_id=localCategory.id).all()
    localCreator = session.query(User).filter_by(id=localCategory.user_id).one()

    return render_template('categoryList.html', 
                items=local_items, 
                category=localCategory, 
                creator=localCreator)

@app.route('/category/<string:category_name>/list/new', methods=['GET','POST'])
def newCategoryItem(category_name):
    localCategory = session.query(Category).filter_by(name=category_name).one()
    #TODO check if the logged in user i the cretor
    current_user_id = localCategory.user_id
    localCreator = session.query(User).filter_by(id=localCategory.user_id).one()
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