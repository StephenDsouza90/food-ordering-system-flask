# Food Ordering System

## Introduction

This is a simple command line food ordering system which has two interfaces i.e. Employee and Customer.

Both users can interact with the system through several options to perfrom an activity.

The Employee and Customer interface are modeled through classes and the options are mapped to the methods in these classes.

The options available to the Employee are add food category, add food details, add delivery person, assign delivery person to an order, update food order, view food details, view revenue and delete order.

The options available to the Customer are view menu, sign up and log in, create an order, checkout and view order details and status.

## Creating tables

There are several classes that inherit the Base class from SQLAlchemy in order to create tables. 

These classes are Food Category, Food Details, Customer Details, Customer Order Selection, Customer Order Status and Delivery Person.

The property name __tablename__ in these classes direct the name of the table in the DB and the remaining properties are the columns of the table.

The SQLiteBackend class is responsible for creating an engine. In case the engine has already been created then that engine will be returned. 

The bootstrap method will connect to the engine and after a successful connection, it will create the tables in the DB. If the engine does not successfully connect to the DB then it will retry and then return an error.

### Purpose of the tables

The purpose of the tables in the DB is to store records when the Employee or Customer performs a certain activity.

For example - If an employee adds a food category and food detail so this will be stored in the Food Caterogy table and Food Details table respectively. When the customer will view the menu, so they will be able to see these items.

## Employee and Customer class

These classes contains methods through which a process is carried out when the employee or customer performs an activity.

For example - When an employee inputs a category name "Dessert", so the method add_food_caterogy has a parameter with name. This name parameter is passed on to an object that holds the class (Food Caterogy) and value (name). The object is then passed on to the session through the session.add() and holds it temporarily and the session.commit() stores the record in the DB. 

## How to run locally:

```
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
```

## Files

The food ordering system is split into four files i.e. main.py, models.py, core.py and constants.py

### main.py

Main contains the controllor object which connects to the DB through bootstrapping. It also handles the user's options through which they can perform their activities.

### models.py

Models contains the SQLiteBackend class which holds the engine, session and bootstrap. 

It also contains the Food Category, Food Details, Customer Details, Customer Order Selection, Customer Order Status and Delivery Person classes for the purpose of record keeping. 

It also has the Employee and Customer class that have methods to carry out the processes.

Models also has one function for the session which rollback (in case the commit fails) and close (when the process is complete).  

### core.py

Core contains the controller class which inherites from the SQLiteBackend class and composites from the Employee and Customer classes.

The controller class also includes all the methods from the Employee and Customer classes.

The purpose of the controller class is to mainly connect to the SQLiteBackend class and use the session as well as link the Employee and Customer classes to perform the functions.