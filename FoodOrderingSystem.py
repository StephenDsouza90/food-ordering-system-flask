import time
import datetime

from datetime import datetime, timedelta

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy import create_engine, func, update

from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FoodCategory(Base):
    """ Represents food categories """
    __tablename__ = 'food_category'

    category_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = Column(String(30), nullable=False)

class FoodDetails(Base):
    """ Represents food details """
    __tablename__ = 'food_details'

    food_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    category_id = Column(Integer(), ForeignKey('food_category.category_id'), nullable=False)
    food_name = Column(String(30), nullable=False)
    price = Column(Integer(), nullable=False)

class CustomerDetails(Base):
    """ Represents customer details """
    __tablename__ = 'customer_details'

    cust_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    cust_name = Column(String(30), nullable=False)
    cust_phone = Column(Integer())
    cust_email = Column(String(30))

class CustOrderSelection(Base):    
    """ Represents food ordered """
    __tablename__ = 'customer_order_selection'

    order_id = Column(Integer(), ForeignKey('customer_order_status.order_id'), primary_key=True, nullable=False)
    food_id = Column(Integer(), ForeignKey('food_details.food_id')) 
    food_qty = Column(Integer())

class CustOrderStatus(Base):
    """ Represents order status """
    __tablename__ = 'customer_order_status'

    order_id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    cust_id = Column(Integer(), ForeignKey('customer_details.cust_id'))
    delivery_person_id = Column(Integer(), ForeignKey('delivery_person.delivery_person_id'))
    checkout_time = Column(DateTime, default=datetime.utcnow)
    estimated_time = Column(DateTime, default=datetime.utcnow)
    order_status = Column(String(30))
    order_address = Column(String(30))

class SQLiteBackend(object):
    """ Represents SQLite Backend that manages creating the engine and session """
    def __init__(self, db_creation):
        self.engine = None
        self.Session = sessionmaker(autocommit=False, expire_on_commit=False)
        self.setup_engine(db_creation)

    def setup_engine(self, db_creation=None):
        """ Setup engine, return engine if exist """
        if self.engine:
            return
        self.engine = create_engine(db_creation, echo=False, pool_recycle=3600)
        self.Session.configure(bind=self.engine)

    def bootstrap(self):
        """ Connects to engine and creates tables """
        connection  = None

        for i in range(2):
            try:
                connection = self.engine.connect()
            except:
                print("DB Server is not up yet, Retrying..")
                time.sleep(i * 5)
                continue
        if not connection:
            raise Exception("Couldn't connect to DB Server even after retries!")

        Base.metadata.create_all(self.engine)
        connection.close()

class Employee:
    """ Restaurant's end operation """
    # View order and status by customer id
    # View all orders/status
    # Delete and update food category and food details and delivery person
    # View checkout orders/en route orders/ delieverd orders
    # View revenue of a particular date/month

    def add_food_category(self, category_name, session):
        """ Insert a new food category """
        category = FoodCategory(name=category_name)
        session.add(category)
        try:
            session.commit()
            return category
        except IntegrityError:
            session.rollback()
            raise Exception("Category exist")
        finally:
            session.expunge_all()
            session.close()

    def add_food_details(self, category_id, food_name, price, session):
        """ Insert new food details """
        details = FoodDetails(category_id=category_id, food_name=food_name, price=price)
        session.add(details)
        try:
            session.commit()
            return details
        except IntegrityError:
           session.rollback()
           raise Exception("Food exist")
        finally:
            session.expunge_all()
            session.close()

    def add_delivery_person(self, delivery_person_name, delivery_person_phone, session):
        """ Insert new delivery person """
        details = DeliveryPerson(delivery_person_name=delivery_person_name, delivery_person_phone=delivery_person_phone)
        session.add(details)
        try:
            session.commit()
            return details
        except IntegrityError:
           session.rollback()
           raise Exception("Delivery person exist")
        finally:
            session.expunge_all()
            session.close()

    def assign_deliver_person_to_deliver_order(self, order_id, delivery_person_id, session):
        """ Update CustOrderStatus table to add deliver person to deliver order """
        update = session.query(CustOrderStatus).filter(CustOrderStatus.order_id == order_id).update({CustOrderStatus.delivery_person_id: delivery_person_id}, synchronize_session=False)
        try:
            session.commit()
            return update
        except:
            session.rollback()
            raise Exception("Checkout not completed!")
        finally:
            session.expunge_all()
            session.close()

    def view_orders(self, order_id, session):
        """ View particular details of an order """
        try:
            view = session.query(FoodCategory, FoodDetails, CustOrderSelection, CustomerDetails, CustOrderStatus).\
                filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                filter(FoodCategory.category_id == FoodDetails.category_id).\
                filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                filter(CustOrderStatus.order_id == order_id)
                # label('total_price'), func.sum(CustOrderSelection.food_qty*FoodDetails.price)
                # (func.sum(CustOrderSelection.food_qty*FoodDetails.price).label("total_price"))
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()        

    def view_order_status(self, order_id, session):
        """ View status of a particular order """

        try:
            view = session.query(FoodCategory, FoodDetails, CustOrderSelection, CustomerDetails, CustOrderStatus, DeliveryPerson).\
                filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                filter(FoodCategory.category_id == FoodDetails.category_id).\
                filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                filter(DeliveryPerson.delivery_person_id == CustOrderStatus.delivery_person_id).\
                filter(CustOrderStatus.order_id == order_id)
                # label('total_price'), func.sum(CustOrderSelection.food_qty*FoodDetails.price)
                # (func.sum(CustOrderSelection.food_qty*FoodDetails.price).label("total_price"))
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def view_revenue_today(self, order_status, session):
        """ View revenue of today """
        # Sum all the total price of the delieverd orders

        try:
            revenue_today = session.query(FoodDetails, CustOrderSelection, CustomerDetails, CustOrderStatus).\
            filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
            filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
            filter(CustOrderSelection.food_id == FoodDetails.food_id).\
            filter(CustOrderStatus.order_status == order_status).\
            filter(CustOrderStatus.checkout_time <= datetime.today())
            # label('total_price'), func.sum(CustOrderSelection.food_qty*FoodDetails.price)
            # (func.sum(CustOrderSelection.food_qty*FoodDetails.price).label("total_price"))
            return revenue_today
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def view_revenue_month(self, session):
        """ View revenue of particular month """


        # Get all orders of a particular month
        # Sum all those orders
        # Use CustOrderSelection table
        # Need to check how to get a range or month
        pass

class Customer:
    """ Customer's end operation """    
    def customer_signup(self, cust_name, cust_phone, cust_email, session):
        """ Add a new customer """
        signup = CustomerDetails(cust_name=cust_name, cust_phone=cust_phone, cust_email=cust_email)
        session.add(signup)
        try:
            session.commit()
            return signup
        except:
            session.rollback()
            raise Exception("User exist!")
        finally:
            session.expunge_all()
            session.close()

    def customer_login(self, cust_id, session):
        """ Customer can login into their account """
        try:
            login = session.query(CustomerDetails).filter_by(cust_id=cust_id).first()
        except Exception as ex:
            print("Error getting customer ID, error={}".format(str(ex)))
        finally:
            session.close()
        return login    
         
    def view_menu(self, session):
        """ Customer can view menu """
        try:
            menu = session.query(FoodCategory, FoodDetails).filter(FoodCategory.category_id == FoodDetails.category_id).all()
            return menu
        except Exception as ex:
            print("Error getting menu, error={}".format(str(ex)))
        finally:
            session.close()            

    def create_order_id(self, cust_id, session): 
        """ Generate order id """
        order = CustOrderStatus(cust_id=cust_id)
        session.add(order)
        try:
            session.commit()
            return order
        except:
            session.rollback()
            raise Exception("Order ID not created!")
        finally:
            session.expunge_all()
            session.close()

    def add_food_to_order(self, order_id, food_id, food_qty, session): 
        """ Add food items """
        add = CustOrderSelection(order_id=order_id, food_id=food_id, food_qty=food_qty)
        session.add(add)
        try:
            session.commit()            
            return add
        except:
            session.rollback()
            raise Exception("Food items not added!")
        finally:
            session.expunge_all()
            session.close()
        
    def view_order(self, cust_id, session):
        """ Customer can view their orders before checkout/confirming order """
        try:
            view = session.query(FoodCategory, FoodDetails, CustOrderSelection, CustomerDetails, CustOrderStatus).\
                filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                filter(FoodCategory.category_id == FoodDetails.category_id).\
                filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                filter(CustOrderStatus.cust_id == cust_id)
                # label('total_price'), func.sum(CustOrderSelection.food_qty*FoodDetails.price)
                # (func.sum(CustOrderSelection.food_qty*FoodDetails.price).label("total_price"))
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def checkout(self, cust_id, order_status, order_address, checkout_time, estimated_time, session):
        """ Customer can checkout/confirm order """
        checkout_update = session.query(
            CustOrderStatus
            ).filter(CustOrderStatus.cust_id == cust_id
            ).update(
                {CustOrderStatus.order_status: order_status, 
                CustOrderStatus.order_address: order_address, 
                CustOrderStatus.checkout_time: checkout_time,
                CustOrderStatus.estimated_time: estimated_time}, 
                synchronize_session=False
                )
        try:
            session.commit()
            return checkout_update
        except:
            session.rollback()
            raise Exception("Checkout not completed!")
        finally:
            session.expunge_all()
            session.close()

    def delete_order(self, order_id, session):
        """ Delete complete order """
        del_order = session.query(CustOrderStatus).filter_by(order_id=order_id).delete()
        dele = session.query(CustOrderSelection).filter_by(order_id=order_id).delete()
        try:
            session.commit()
            return del_order, dele            
        except IntegrityError:
            session.rollback()
            raise Exception("Order not deleted!")
        finally:
            session.expunge_all()
            session.close()        

    def view_orders_status(self, cust_id, session):
        """ Customer can view their orders after checkout/confirming order """
        try:
            view = session.query(FoodCategory, FoodDetails, CustOrderSelection, CustomerDetails, CustOrderStatus, DeliveryPerson).\
                filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                filter(FoodCategory.category_id == FoodDetails.category_id).\
                filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                filter(DeliveryPerson.delivery_person_id == CustOrderStatus.delivery_person_id).\
                filter(CustOrderStatus.cust_id == cust_id)
                # label('total_price'), func.sum(CustOrderSelection.food_qty*FoodDetails.price)
                # (func.sum(CustOrderSelection.food_qty*FoodDetails.price).label("total_price"))
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

class Controller(SQLiteBackend):
     def __init__(self, db_url):
        super(Controller, self).__init__(db_url)
        self.employee = Employee()
        self.customer = Customer()
        self.delivery_person = DeliveryPerson()

class DeliveryPerson(Base, Employee):
    """ Represents delivery person """

    __tablename__ = 'delivery_person'

    delivery_person_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    delivery_person_name = Column(String(30), nullable=False)
    delivery_person_phone = Column(Integer(), nullable=False)

    def update_order(self, order_id, order_status, session):
        super(DeliveryPerson, self).__init__()
        """ Delivery person can update the order. """

        update = session.query(
            CustOrderStatus
            ).filter(CustOrderStatus.order_id == order_id
            ).update(
                {CustOrderStatus.order_status: order_status}, 
                synchronize_session=False
                )
        try:
            session.commit()
            return update
        except:
            session.rollback()
            raise Exception("update not completed!")
        finally:
            session.expunge_all()
            session.close()

def main():
    """ The user interface in which employee/customer will use to perform actions on the Food Ordering System. """
    db_url = "sqlite:///fos.db"
    print("Connecting to {}".format(db_url))

    fos = Controller(db_url)
    fos.bootstrap()

    welcome_message = """ 
    
    Welcome to the Food Ordering System! Please press the below options:

    1. Employee
    2. Customer

    Your Option:

    """

    option = int(input(welcome_message))

    if option == 1:
        emp_options = """ 
        
        Welcome to the employee interface! Please press the below options:
        
        0. Quit
        1. Add food category
        2. Add food details
        3. Add delivery person
        4. Add deliver person to deliver order 
        5. Update order (Only for delivery person use)
        6. View order details
        7. View order status
        8. View revenue today
        9. View revenue month
    
        Your Option:

        """

        employee_options = int(input(emp_options))

        while employee_options != 0:

            if employee_options == 1:
                category_name = input("Enter category name: ")
                session = fos.Session()
                c = fos.employee.add_food_category(category_name, session)
                if c:
                    print("\nCategory ID: {} \nCategory Name: {} \nSucessfully! ".format(c.category_id, c.name))
                else:
                    print("Adding details was not sucessfully. Please try again!")    

            elif employee_options == 2:
                category_id = input ("Enter category ID: ")
                food_name = input("Enter food name: ")
                price = input("Food price: ")
                session = fos.Session()
                f = fos.employee.add_food_details(category_id, food_name, price, session)
                if f:
                    print("\nFood ID: {} \nCategory ID: {} \nFood Name: {} \nPrice: {} \nSucessfully! ".format(f.food_id, f.category_id, f.food_name, f.price ))
                else:
                    print("Adding details was not sucessfully. Please try again!")    

            elif employee_options == 3:
                delivery_person_name = input("Enter delivery person name: ")
                delivery_person_phone = input("Enter delivery person phone: ")
                session = fos.Session()
                d = fos.employee.add_delivery_person(delivery_person_name, delivery_person_phone, session)
                if d:
                    print("\nDeliver person ID: {} \nDeliver person name: {} \nDelivery person phone: {} \nSucessfully! ".format(d.delivery_person_id, d.delivery_person_name, d.delivery_person_phone))
                else:
                    print("Adding details was not sucessfully. Please try again!")    
                pass

            elif employee_options == 4:
                order_id = input("Enter order ID: ")
                delivery_person_id = input("Enter delivery person ID: ")
                session = fos.Session()
                d = fos.employee.assign_deliver_person_to_deliver_order(order_id, delivery_person_id, session) 
                if d:
                    print("Add sucessful!")
                else:
                    print("Add not sucessful!") 

                pass     

            elif employee_options == 5:
                order_id = input("Enter order ID: ")
                select = """                 
                Press
                
                1. En route
                2. Delivered

                Your option: 
                """
                
                options = int(input(select))
                 
                if options == 1:
                    order_status = "En route"
                    session = fos.Session()
                    s = fos.delivery_person.update_order(order_id, order_status, session) 
                    if s:
                        print("Order update sucessful!")
                    else:
                        print("Order update not sucessful!") 

                if options == 2:
                    order_status = "Delivered"
                    session = fos.Session()
                    s = fos.delivery_person.update_order(order_id, order_status, session) 
                    if s:
                        print("Order update sucessful!")
                    else:
                        print("Order update not sucessful!")

            elif employee_options == 6:
                order_id = input("Enter order ID: ")
                session = fos.Session()
                view_order = fos.employee.view_orders(order_id, session)
                if view_order:
                    for fc, fd, cos, cd, cosa in view_order:
                        print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {}".format(fc.name, fd.food_name, fd.price, cos.food_qty))
                        
                    print("\nCustomer name: {} \nOrder ID: {} \nTotal price: ".format(cd.cust_name, cosa.order_id))                
            # figure out how to use total price

            elif employee_options == 7:
                order_id = input("Enter order ID: ")
                session = fos.Session()
                view_status = fos.employee.view_order_status(order_id, session)
                if view_status:
                    for fc, fd, cos, cd, cosa, dp in view_status:
                        print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {}".format(fc.name, fd.food_name, fd.price, cos.food_qty))
                        
                    print("\nCustomer name: {} \nOrder ID: {} \nDeliver person name: {} \nOrder status: {} \nTotal price: ".format(cd.cust_name, cosa.order_id, dp.delivery_person_name, cosa.order_status))
            # figure out how to use total price

            elif employee_options == 8:
                select = """ 
                To see revenue for a certain status, please press 
                
                1. Checkedout
                2. En route
                3. Delivered
                
                Your option:                 
                """
                
                options = int(input(select))

                if options == 1:
                    order_status = "Checkedout"
                    print("No orders remaining in Checkedout")
                elif options == 2:
                    order_status = "En route"
                    print("No orders remaining in En route")
                else:
                    order_status = "Delivered"

                session = fos.Session()
                view_rev_today = fos.employee.view_revenue_today(order_status, session)
                if view_rev_today:
                    for fd, cos, cd, cost in view_rev_today:
                        print("\nCustomer name: {} \nOrder ID: {} \nOrder Status: {}".format(cd.cust_name, cos.order_id, cost.order_status))

                    print("\nToday's revenue: ") # fd.price
            # figure out how to use total revenue

            elif employee_options == 9:
                pass

            employee_options = int(input("\nYour option: "))
            
    elif option == 2:
        cust_options = """ 
        
        Welcome to the employee interface! Please press the below options:
        
        0. Quit
        1. View menu
        2. Customer signup
        3. Customer login

        Your Option:

        """        
        
        customer_options = int(input(cust_options))

        while customer_options != 0:

            if customer_options == 1:
                session = fos.Session()
                menu = fos.customer.view_menu(session)
                for c, d in menu:
                    print("\nFood ID: {} \nFood category: {} \nFood name: {} \nFood price: {}".format(d.food_id, c.name, d.food_name, d.price))

            elif customer_options == 2:
                cust_name = input("Enter customer name: ")
                cust_phone = input("Enter customer phone number: ")
                cust_email = input("Enter customer email address: ")
                session = fos.Session()
                c = fos.customer.customer_signup(cust_name, cust_phone, cust_email, session)
                if c:
                    print("\nCustomer ID: {} \nCustomer name: {} \nCustomer phone number: {} \nCustomer email address: {} \nSucessfully! ".format(c.cust_id, c.cust_name, c.cust_phone, c.cust_email))
                else:
                    print("Adding details was not sucessfully. Please try again!")    

            elif customer_options == 3:
                cust_id = input("Enter customer ID: ")
                session = fos.Session()
                c = fos.customer.customer_login(cust_id, session)
                if c:
                    print("\nCustomer ID {} login successful! \nWelcome {}".format(c.cust_id, c.cust_name))
                else:
                    print("Login not sucessfully. Please try again or signup!")
                    return    

                selection = """ 
                Please select food items!

                0. Logout
                1. Create order
                2. Add food to order
                3. Remove food to order
                4. View order
                5. Checkout
                6. Delete order
                7. View order status
                
                Select option: 
                """
                order = int(input(selection))

                while order != 0:

                    if order == 1:
                        session = fos.Session()
                        o = fos.customer.create_order_id(c.cust_id, session)
                        if o:
                            print("\nOrder ID {} generated! Please proceed to making an order.".format(o.order_id))
                        else:
                            print("Order ID not generated. Please try again!")

                    elif order == 2:
                        food_id = input("Enter food ID: ")
                        food_qty = input("Enter quantity: ")
                        session = fos.Session()
                        a = fos.customer.add_food_to_order(o.order_id, food_id, food_qty, session)
                        if a:
                            print("Order sucessful!")
                        else:
                            print("Order not sucessful. Please try again!")
                    # Had made 2 items in the order but only 1 showed
                  
                    elif order == 3:
                        pass
                    # To fill

                    elif order == 4:
                        session = fos.Session()
                        view_menu = fos.customer.view_order(c.cust_id, session) # o.order_id
                        if view_menu:
                            for fc, fd, cos, cd, cosa in view_menu:
                                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nTotal per item: ".format(fc.name, fd.food_name, fd.price, cos.food_qty))
                        
                            print("\nCustomer name: {} \nOrder ID: {} \nTotal price: ".format(cd.cust_name, cosa.order_id))                
                    # figure out how to use total price per item and total/grand price
                
                    elif order == 5:
                        order_address = input("Enter delivery address: ")
                        checkout = int(input("Press 1 to checkout: "))
                        if checkout == 1:
                            order_status = "Checkedout"
                        checkout_time = datetime.now()
                        delivery_time = timedelta(minutes=30)
                        estimated_time = checkout_time + delivery_time
                        session = fos.Session()
                        c = fos.customer.checkout(c.cust_id, order_status, order_address, checkout_time, estimated_time, session) 
                        if c:
                            print("Checkout sucessful!")
                        else:
                            print("Checkout not sucessful!") 

                    elif order == 6:
                        order_id = input("Enter order ID: ")
                        session = fos.Session()
                        d = fos.customer.delete_order(order_id, session)
                        print("Order {} deleted!".format(order_id))

                    elif order == 7:
                        session = fos.Session()
                        view_status = fos.customer.view_orders_status(c.cust_id, session) # o.order_id
                        if view_status:
                            for fc, fd, cos, cd, cosa, dp in view_status:
                                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {}".format(fc.name, fd.food_name, fd.price, cos.food_qty))
                        
                            print("\nCustomer name: {} \nOrder ID: {} \nDeliver person name: {} \nOrder status: {} \nTotal price: ".format(cd.cust_name, cosa.order_id, dp.delivery_person_name, cosa.order_status))
                    # figure out how to use total price

                    order = int(input("\nSelect option: "))               

            customer_options = int(input("\nYour option: "))

main()