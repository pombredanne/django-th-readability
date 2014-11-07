=====================
Readability Connector
=====================

From Trigger Happy, this connector provides an access to your Readability account to add/get notes

Requirements :
==============
* `django_th <https://github.com/foxmask/django-th>`_ >= 0.9.1
* `readability-api <https://pypi.python.org/pypi/readability-api>`_  == 0.2.4
* Python < 3.x due to oauth2 required by readability-api

Installation:
=============
to get the project, from your virtualenv, do :

.. code:: python

    pip install django-th-readability
    
then do

.. code:: python

    python manage.py syncdb

to startup the database


Parameters :
============
As usual you will setup the database parameters.

Important parts are the settings of the available services :

Settings.py 
-----------

INSTALLED_APPS
~~~~~~~~~~~~~~

add the module th_rss to INSTALLED_APPS

.. code:: python

    INSTALLED_APPS = (
        'th_readability',
    )    


TH_SERVICES 
~~~~~~~~~~~

TH_SERVICES is a list of the services used by Trigger Happy

.. code:: python

    TH_SERVICES = (
        'th_readability.my_readability.ServiceReadability',
    )


TH_READABILITY
~~~~~~~~~~~~~~
TH_READABILITY is the settings you will need, to be able to add/read data in/from readability Service.

To be able to use readability :

* you will need to (grad the readability keys)[https://readability.com/developers/api] 
* create a new application at readability website

|ImageLink|_

.. |ImageLink| image:: http://foxmask.info/public/trigger_happy/readability_account_settings.png 

* copy the "keys & secret" of your application to the settings.py
 
.. code:: python

    TH_READABILITY = {
        'consumer_key': 'abcdefghijklmnopqrstuvwxyz',
        'consumer_secret': 'abcdefghijklmnopqrstuvwxyz',
    }


Setting up : Administration
===========================

once the module is installed, go to the admin panel and activate the service readability. 

All you can decide here is to tell if the service requires an external authentication or not.

Once they are activated. User can use them.
