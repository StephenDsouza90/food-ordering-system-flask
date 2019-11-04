# Food Ordering System

This is a simple command line food ordering system that has two interfaces i.e. Employee and Customer.

Both users have different sets of functions such as:

The Employee can add food category, add food details, add delivery person, assign delivery person to an order, update food order, view food details, view revenue and delete order.

The Customer can view menu, sign up/log in, create an order, checkout and view order details/status.


## The files

The food ordering system is split into four files i.e. main.py, models.py, core.py and constants.py.

### main.py

Main handles the user's functions and initiates the process of connecting to the database and bootstrapping.

### models.py

Models contains the SQLiteBackend which creates the engine, session and bootstrap function. 

It also containst the classes for 

Tables - store records

Employee/Customer - methods that stores objects

### core.py

Core contains the controller class that inherites from the SQLiteBackend class and composites from the Employee and Customer classes.

The controller class also includes all the methods from the Employee and Customer.

The purpose of the controller class is to mainly connect to the SQLiteBackend class and use the session as well as link the Employee and Customer classes to perform the functions.

