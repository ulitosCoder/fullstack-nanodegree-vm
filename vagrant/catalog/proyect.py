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
        latestItems = session.query(CategoryItem).join(CategoryItem.category
            ).order_by(desc(CategoryItem.date_added)).limit(10).all()

        localUser = session.query(User).filter_by(id=2).one()
        try:
            user_id = login_session['user_id']
            localUser = session.query(User).filter_by(id=user_id)
        except:
            user_id = 0


        return render_template('catalog.html',
            categories = local_categories,
            latest=latestItems,
            user=localUser)

    except Exception, e:
        return e.args 
    
    #print local_categories

    
    


@app.route('/category/JSON')
def showCategoryJSON():
    
    local_categories = session.query(Category).all() 

    return jsonify(categories = [i.serialize for i in local_categories])

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

    try:
        localCategory = session.query(Category).filter_by(name=category_name).one() 

        return jsonify(localCategory.serialize)
    except Exception, e:
        return 'Not found'
    
    

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

@app.route('/category/<string:category_name>/list/<string:item_name>/edit',
    methods=['GET','POST'])
def editCategoryItem(category_name,item_name):

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

@app.route('/category/<string:category_name>/list/<string:item_name>/delete',
    methods=['GET','POST'])
def deleteCategoryItem(category_name,item_name):
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