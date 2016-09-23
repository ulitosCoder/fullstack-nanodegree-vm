# Udacity's Web developer full stack - Project 5 - Linux Server Configuration
==============================================================

   This project reimplements the work for Project 2, but is updated to work 
with PosgreSQL on a remote server.
   In this project I configure a remote Linux server to host a Web application,
with security measures. 




## Access to the server
-----------------------

   To login to the server you need the provided rsa key, to the IP address 52.35.27.137, paste the rsa key into
   a file named udacity_key.rsa
   use the following commands
   
   1. chmod 600 udacity_key.rsa
   2. ssh grader@52.35.27.137 -p 2200 -i udacity_key.rsa

## Web application
------------------

+ To use the web application use your favorite Web browser and open [this address](http://ec2-52-35-27-137.us-west-2.compute.amazonaws.com/)

+ You must login with Google+ to create/delete/modify your own categories, click on the link in the upper side of the webpage. 


+ Once loged in:
  + click [Add New](http://ec2-52-35-27-137.us-west-2.compute.amazonaws.com/catalog/new) to create new categories
  + click Edit or Delte to the categories created by you.
  + Click on a category name to see the content.
  + If you created the category click on Add new item, to add items to your category.
  + Also you can Edit/Delet items only on the items of your categories.
   



