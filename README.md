# Food Ordering System

This is a simple command line food ordering system that has two interfaces i.e. Employee and Customer.

Both users have different sets of functions such as:

Employee can add food category, add food details, add delivery person, assign delivery person to an order, update food order, view food details, view revenue and delete order.

Customer can view menu, sign up/log in, create an order, checkout and view order details/status.


## Files

The food ordering system is split into four files i.e. main.py, models.py, core.py and constants.py.

### main.py

Main handles the user's functions and initiates the process of connecting to the database and bootstrapping.

### models.py

Models contains the SQLiteBackend which creates the engine, session and bootstrap function. 

It also containst the classes for 

Tables - store records

Employee/Customer - methods that stores objects

### core.py

Core contains the controller class which inherites from the SQLiteBackend class and composites from the Employee and Customer classes.

The controller class also includes all the methods from the Employee and Customer.

The purpose of the controller class is to mainly connect to the SQLiteBackend class and use the session as well as link the Employee and Customer classes to perform the functions.

### How to run locally:

>> python main.py

Connecting to sqlite:///fos2.db

    Welcome to the Food Ordering System! Please press the below options:

    1. Employee
    2. Customer

    Your Option:

    1

    Welcome to the employee interface! Please press the below options:

    0. Quit
    1. Add food category
    2. Add food details
    3. Add delivery person
    4. Assign delivery person to order
    5. Update order (Only for delivery person use)
    6. View order details
    7. View order status
    8. View revenue today
    9. Delete order

    Your Option:

    1
Enter category name: Desserts

Add Successfully
