# Udacity's Web developer full stack Project 2 - Items Catalog
==============================================================

This project stores information about different categories and items
whithin each category. Implements security with Authentication 
and authorization with third party authentication providers.



## Install
------------


The easiest way to test this code is with [Vagrant](https://www.vagrantup.com/)

Follow these steps to get you started:

1. Install [Vagrant](https://www.vagrantup.com/)
2. Install [VirtualBox](https://www.virtualbox.org/)
3. Install [cygwin](https://www.cygwin.com/), be sure to select **git** from the packages list 

---------------

## Setting up the environment

1. Clone my catalog repository 
    * Open a cygwin terminal
    * execute `git clone https://github.com/ulitosCoder/fullstack-nanodegree-vm`
2. Navigate to the catalog directory
    * `cd fullstack-nanodegree-vm/vagrant/catalog/`
3. Start the Vagrant VM
    * `vagrant up`
4. Probably you will need to update the Flask framework, execute these commands,
   if needed add `sudo` to the beggining of every command
    * `pip install werkzeug==0.8.3`
    * `pip install flask==0.9`
    * `pip install Flask-Login==0.1.3`
5. Enter to the VM
    * To start de VM execute `vagrant up` in cygwin
    * Then vagrant ssh
6. Start the webserver, once inside the VM execute these to start the web server
    * `cd /vagrant/catalog/`
    * `python project.py`

    When executing the webserver, an empty database will be created with the
    design according to the classes in the databe_setup.py file

   The source code in the repository will be accessible in the VM with the synced folders in /vagrant/

## Testing the code
    * Open your favorite web browser and open http://localhost:8000
    * If you can´t use port 8000 in your host machine, map the port to another
      available:
      -Edit the Vagrantfile in the fullstack/vagrant/ directory in ypur git cloned copy.
      -look for this line  
         `config.vm.network "forwarded_port", guest: 8000, host: <port>`
      -change the port bumber in the <host> field
      -Use the new port in the abobve link


