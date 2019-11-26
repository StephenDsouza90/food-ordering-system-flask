# Food Ordering System

## Introduction

This application is a food ordering system which has two interfaces i.e. Employee and Customer. It can be used via the command line or REST API.

Both users can interact with the system through several options to perform an activity.

The Employee and Customer interface are modeled through classes and the options are mapped to the methods in these classes.

The options available to the Employee are add food category, add food details, add delivery person, assign delivery person to an order, update food order, view food details, view revenue and delete order.

The options available to the Customer are view menu, sign up and log in, create an order, checkout and view order details and status.

## Creating tables

There are several classes that inherit the Base class from SQLAlchemy in order to create tables. 

These classes are Food Category, Food Details, Customer Details, Customer Order Selection, Customer Order Status and Delivery Person. These classes also include a convert_to_dict method so that the tables can serialize to a JSON format so that it can be used in REST APIs.

The property name __tablename__ in these classes direct the name of the table in the DB and the remaining properties are the columns of the table.

The SQLiteBackend class is responsible for creating an engine. In case the engine has already been created then that engine will be returned. 

The bootstrap method will connect to the engine and after a successful connection, it will create the tables in the DB. If the engine does not successfully connect to the DB then it will retry and then return an error.

### Purpose of the tables

The purpose of the tables in the DB is to store records when the Employee or Customer performs a certain activity.

For example - If an employee adds a food category and food detail so this will be stored in the Food Caterogy table and Food Details table respectively. When the customer will view the menu, so they will be able to see these items.

## Employee and Customer class

These classes contains methods through which a process is carried out when the employee or customer performs an activity.

For example - When an employee inputs a category name "Dessert", so the method add_food_caterogy has a parameter with name. This name parameter is passed on to an object that holds the class (Food Caterogy) and value (name). The object is then passed on to the session through the session.add() and holds it temporarily and the session.commit() stores the record in the DB. 

## How to run locally via command line:

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

## How to run locally via REST API:

Add 3 food categories, dessert, main-dish, apetizers

```
>> python server.py

Connecting to sqlite:///fos2.db
Serving on http://StephenDsouza:8080

curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"dessert\"}" "localhost:8080/employees/add-food-category"

{"category_id": 1, "category_name": "dessert"}

curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"main-dish\"}" "localhost:8080/employees/add-food-category"

{"category_id": 2, "category_name": "main-dish"}

curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"apetizers\"}" "localhost:8080/employees/add-food-category"

{"category_id": 3, "category_name": "apetizers"}
```

## REST API

A REST (REpresentational State Transfer) API (Application Programming Interface) is a transfer of resources (data) from a Server to a Client over the internet. Through the REST API, the client can perform a GET, POST, PUT, DELETE request on the server.

A client can use an API to request for resources from the server. A server has the resources and transfers it to the client through an API. A resource can be any object for example, user, photo, number. An API allows one software to talk to another. It is a procedure allowing a client to access the data from a server. 

This app runs with the Endpoint localhost (my computer) that has an IP address '0.0.0.0' (which maps to my computer) and a port 8080.

## Order process

The customer can make an order once they have signed up and logged in. 

The customer will proceed to the "Process order" option to make an order after which they can add food items as well as update or remove food items. Once the customer has finalized the selection of food items for their order, an order ID will be generated.

Before confirming (checkout) the order, the customer can view the items in the cart as well as the total bill amount. The customer will then proceed to the "Checkout" option to confirm the order. The customer also has an option to cancel their order. 

The customer can view the items of their order and view the status of their order through the "View order" and "View order status" options respectively.

## Files

The food ordering system is split into four files i.e. main.py, models.py, core.py and constants.py

### main.py

Main contains the controllor object which connects to the DB through bootstrapping. It also handles the user's options via the commande line through which they can perform their activities.

### models.py

Models contains the SQLiteBackend class which holds the engine, session and bootstrap. 

It also contains the Food Category, Food Details, Customer Details, Customer Order Selection, Customer Order Status and Delivery Person classes for the purpose of record keeping. 

It also has the Employee and Customer class that have methods to carry out the processes.

Models also has one function for the session which rollback (in case the commit fails) and close (when the process is complete).  

### core.py

Core contains the controller class which inherites from the SQLiteBackend class and composites from the Employee and Customer classes.

The controller class also includes all the methods from the Employee and Customer classes.

The purpose of the controller class is to mainly connect to the SQLiteBackend class and use the session as well as link the Employee and Customer classes to perform the functions.

### server.py

Server contains the controllor object which connects to the DB through bootstrapping. It is also responsible for creating and running the server.

The employee and customer routes are mapped to their respective functions and the functions call the methods from the Controller class.

The functions in server.py perform a GET, POST, PUT and DELETE requests over HTTP REST and returns results in JSON format.