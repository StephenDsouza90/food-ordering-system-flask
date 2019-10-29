import time
import datetime

EMP_OPT_UO_EN_ROUTE = 1
EMP_OPT_UO_DELIVERED = 2

EMP_OPT_RT_CHECKEDOUT = 1
EMP_OPT_RT_EN_ROUTE = 2

EMP_OPT_ADD_FOOD_CATEGORY = 1
EMP_OPT_ADD_FOOD_DETAILS = 2
EMP_OPT_ADD_DELIVERY_PERSON = 3
EMP_OPT_ASSIGN_DELIVERY_PERSON_TO_ORDER = 4 
EMP_OPT_UPDATE_ORDER = 5
EMP_OPT_VIEW_ORDER_DETAILS = 6
EMP_OPT_VIEW_ORDER_STATUS = 7
EMP_OPT_VIEW_REVENUE_TODAY = 8
EMP_OPT_DELETE_ORDER = 9

CUST_OPT_ADD_FOOD_TO_ORDER = 1
CUST_OPT_REMOVE_FOOD_TO_ORDER = 2
CUST_OPT_UPDATE_FOOD_TO_ORDER = 3

CUST_OPT_PROCESS_ORDER = 1
CUST_OPT_VIEW_ORDER = 2
CUST_OPT_CHECKOUT = 3
CUST_OPT_CANCEL_ORDER = 4
CUST_OPT_VIEW_ORDER_STATUS = 5

CUST_OPT_VIEW_MENU = 1
CUST_OPT_CUSTOMER_SIGNUP = 2
CUST_OPT_CUSTOMER_LOGIN = 3

EMPLOYEE = 1
CUSTOMER = 2

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
    food_id = Column(Integer(), ForeignKey('food_details.food_id'), primary_key=True)  
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
    bill_amount = Column(Integer())

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

        details = DeliveryPerson(delivery_person_name=delivery_person_name, 
                    delivery_person_phone=delivery_person_phone)
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

        update = session.query(CustOrderStatus).\
                    filter(CustOrderStatus.order_id == order_id).\
                    update({CustOrderStatus.delivery_person_id: delivery_person_id}, 
                    synchronize_session=False)
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
            view = session.query(FoodCategory, FoodDetails, CustOrderSelection).\
                        filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                        filter(FoodCategory.category_id == FoodDetails.category_id).\
                        filter(CustOrderSelection.order_id == order_id)
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()        

    def view_order_grand_total(self, order_id, session):
        """ Employee can view orders with grand total """

        try:
            view = session.query(CustomerDetails, CustOrderStatus).\
                        filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                        filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                        filter(CustOrderStatus.order_id == order_id)            
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def view_order_status(self, order_id, session):
        """ View status of a particular order """

        try:
            view = session.query(CustomerDetails, CustOrderStatus, DeliveryPerson).\
                        filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                        filter(DeliveryPerson.delivery_person_id == CustOrderStatus.delivery_person_id).\
                        filter(CustOrderStatus.order_id == order_id)
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def view_sales_today(self, order_status, session):
        """ View sales of today """

        try:
            sales_today = session.query(CustOrderStatus, CustomerDetails).\
                            filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                            filter(CustOrderStatus.order_status == order_status).\
                            filter(CustOrderStatus.checkout_time <= datetime.today()).\
                            group_by(CustOrderStatus.order_id)
            return sales_today
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def sum_revenue_today(self, order_status, session):
        """ Sum revenue of today """

        try:
            revenue = session.query(CustOrderStatus, func.sum(CustOrderStatus.bill_amount)).\
                        filter(CustOrderStatus.order_status == order_status).\
                        filter(CustOrderStatus.checkout_time <= datetime.today())
            return revenue
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def delete_order(self, order_id, session):
        """ Delete order """

        del_status = session.query(CustOrderStatus).filter_by(order_id=order_id).delete()
        del_selection = session.query(CustOrderSelection).filter_by(order_id=order_id).delete()
        try:
            session.commit()
            return del_status, del_selection            
        except IntegrityError:
            session.rollback()
            raise Exception("Order not deleted!")
        finally:
            session.expunge_all()
            session.close()        

class Customer:
    """ Customer's end operation """    

    def view_menu(self, session):
        """ Customer can view menu """

        try:
            menu = session.query(FoodCategory, FoodDetails).\
                        filter(FoodCategory.category_id == FoodDetails.category_id).all()
            return menu
        except Exception as ex:
            print("Error getting menu, error={}".format(str(ex)))
        finally:
            session.close()            

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
            return login
        except Exception as ex:
            print("Error getting customer ID, error={}".format(str(ex)))
        finally:
            session.close()            
         
    def create_order_id(self, cust_id, session): 
        """ Generate order id """

        order_status = CustOrderStatus(cust_id=cust_id)
        session.add(order_status)
        try:
            session.commit()
            return order_status
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
    
    def remove_food_to_order(self, order_id, food_id, session):
        """ Remove food items """

        remove = session.query(CustOrderSelection).\
                    filter_by(order_id=order_id).filter_by(food_id=food_id).\
                    delete()
        try:
            session.commit()
            return remove
        except:
            session.rollback()
            raise Exception("Remove not completed!")
        finally:
            session.expunge_all()
            session.close()

    def update_food_to_order(self, order_id, food_id, food_qty, session):
        """ Update food items """

        update = session.query(CustOrderSelection).\
                    filter(CustOrderSelection.order_id == order_id).\
                    filter(CustOrderSelection.food_id == food_id).\
                    update({CustOrderSelection.food_qty: food_qty}, 
                    synchronize_session=False)
        try:
            session.commit()
            return update
        except:
            session.rollback()
            raise Exception("Remove not completed!")
        finally:
            session.expunge_all()
            session.close()

    def view_order_per_item(self, order_id, session):
        """ Customer can view their orders with price per item before checkout/confirming order """

        try:
            view = session.query(FoodCategory, FoodDetails, CustOrderSelection).\
                        filter(FoodCategory.category_id == FoodDetails.category_id).\
                        filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                        filter(CustOrderSelection.order_id == order_id)            
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def view_order_grand_total(self, order_id, session):
        """ Customer can view their orders with grand total before checkout/confirming order """

        try:
            view = session.query(
                        FoodDetails, CustOrderSelection, CustomerDetails, 
                        CustOrderStatus, func.sum(CustOrderSelection.food_qty*FoodDetails.price)).\
                            filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                            filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                            filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                            filter(CustOrderSelection.order_id == order_id)            
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

    def checkout(self, order_id, order_status, order_address, checkout_time, estimated_time, bill_amount, session):
        """ Customer can checkout/confirm order """

        checkout_update = session.query(CustOrderStatus).\
                            filter(CustOrderStatus.order_id == order_id).\
                            update({
                            CustOrderStatus.order_status: order_status, 
                            CustOrderStatus.order_address: order_address, 
                            CustOrderStatus.checkout_time: checkout_time,
                            CustOrderStatus.estimated_time: estimated_time,
                            CustOrderStatus.bill_amount: bill_amount}, 
                            synchronize_session=False)
        try:
            session.commit()
            return checkout_update
        except:
            session.rollback()
            raise Exception("Checkout not completed!")
        finally:
            session.expunge_all()
            session.close()

    def cancel_order(self, order_id, order_status, session):
        """ Cancel order """

        update = session.query(CustOrderStatus).\
                    filter(CustOrderStatus.order_id == order_id).\
                    update({CustOrderStatus.order_status: order_status}, 
                    synchronize_session=False)
        try:
            session.commit()
            return update
        except:
            session.rollback()
            raise Exception("Checkout not completed!")
        finally:
            session.expunge_all()
            session.close()

    def view_orders_status(self, order_id, session):
        """ Customer can view their orders and status after checkout/confirming order """

        try:
            view = session.query(CustOrderSelection, CustomerDetails, CustOrderStatus, DeliveryPerson).\
                filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                filter(DeliveryPerson.delivery_person_id == CustOrderStatus.delivery_person_id).\
                filter(CustOrderStatus.order_id == order_id)
            return view
        except Exception as ex:
            print("Error getting order, error={}".format(str(ex)))
        finally:
            session.close()

class Controller(SQLiteBackend):
    """ Controller class that inherites from SQLite Backend and composition from Emploeyee, Customer and Delivery Person classes """

    def __init__(self, db_url):
        super(Controller, self).__init__(db_url)
        self.employee = Employee()
        self.customer = Customer()
        self.delivery_person = DeliveryPerson()

    def add_food_category(self, category_name):
        session = self.Session()
        c = self.employee.add_food_category(category_name, session)
        if c:
            print("\nCategory ID: {} \nCategory Name: {} \nsuccessfully!".format(c.category_id, c.name))
        else:
            print("Adding details was not successfully. Please try again!")    

    def add_food_details(self, category_id, food_name, price):
        session = self.Session()
        f = self.employee.add_food_details(category_id, food_name, price, session)
        if f:
            print("\nFood ID: {} \nCategory ID: {} \nFood Name: {} \nPrice: {} \nSucessfully!".format(f.food_id, f.category_id, f.food_name, f.price ))
        else:
            print("Adding details was not sucessfully. Please try again!")    

    def add_delivery_person(self, delivery_person_name, delivery_person_phone):
        session = self.Session()
        d = self.employee.add_delivery_person(delivery_person_name, delivery_person_phone, session)
        if d:
            print("\nDeliver person ID: {} \nDeliver person name: {} \nDelivery person phone: {} \nSuccessfully!".format(d.delivery_person_id, d.delivery_person_name, d.delivery_person_phone))
        else:
            print("Adding details was not successfully. Please try again!")    

    def assign_deliver_person_to_deliver_order(self, order_id, delivery_person_id):
        session = self.Session()
        d = self.employee.assign_deliver_person_to_deliver_order(order_id, delivery_person_id, session) 
        if d:
            print("Add sucessful!")
        else:
            print("Add not sucessful!") 

    def update_order(self, order_id, order_status):
        session = self.Session()
        s = self.delivery_person.update_order(order_id, order_status, session) 
        if s:
            print("Order update successful!")
        else:
            print("Order update not successful!") 

    def view_orders(self, order_id):
        session = self.Session()
        view_order = self.employee.view_orders(order_id, session)
        if view_order:
            for fc, fd, cos in view_order:
                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nPrice per item: {}".format(fc.name, fd.food_name, fd.price, cos.food_qty, (fd.price*cos.food_qty)))
                
    def view_order_grand_total(self, order_id):
        session = self.Session()
        view_order_grand = self.employee.view_order_grand_total(order_id, session)
        if view_order_grand:
            for cd, cosa in view_order_grand:                        
                print("\nCustomer name: {} \nOrder ID: {} \nTotal bill: {}".format(cd.cust_name, cosa.order_id, cosa.bill_amount))                

    def view_order_status(self, order_id):
        session = self.Session()
        view_status = self.employee.view_order_status(order_id, session)
        if view_status:
            for cd, cosa, dp in view_status:
                print("\nCustomer name: {} \nOrder ID: {} \nDeliver person name: {} \nOrder status: {} \nTotal bill: {}".format(cd.cust_name, cosa.order_id, dp.delivery_person_name, cosa.order_status, cosa.bill_amount))

    def view_sales_today(self, order_status):
        session = self.Session()
        sales_today = self.employee.view_sales_today(order_status, session)
        if sales_today:
            for cos, cd in sales_today:
                print("\nCustomer name: {} \nOrder ID: {} \nOrder Status: {} \nBill amount: {} \nDate & Time: {}".format(cd.cust_name, cos.order_id, cos.order_status, cos.bill_amount, cos.checkout_time))

    def sum_revenue_today(self, order_status):
        session = self.Session()
        sum_rev_today = self.employee.sum_revenue_today(order_status, session)
        if sum_rev_today:
            for cos, s in sum_rev_today:
                print("\nToday's revenue: {} ".format(s))

    def delete_order(self, order_id):
        session = self.Session()
        self.employee.delete_order(order_id, session)
        print("Order {} deleted!".format(order_id))

    def view_menu(self):
        session = self.Session()
        menu = self.customer.view_menu(session)
        for fc, fd in menu:
            print("\nFood ID: {} \nFood category: {} \nFood name: {} \nFood price: {}".format(fd.food_id, fc.name, fd.food_name, fd.price))

    def customer_signup(self, cust_name, cust_phone, cust_email):
        session = self.Session()
        c = self.customer.customer_signup(cust_name, cust_phone, cust_email, session)
        if c:
            print("\nCustomer ID: {} \nCustomer name: {} \nCustomer phone number: {} \nCustomer email address: {} \nSucessfully!".format(c.cust_id, c.cust_name, c.cust_phone, c.cust_email))
        else:
            print("Adding details was not sucessfully. Please try again!")    

    def customer_login(self, cust_id):
        session = self.Session()
        login = self.customer.customer_login(cust_id, session)
        return login

    def process_order(self, cust_id):
        session = self.Session()
        o = self.customer.create_order_id(cust_id, session)
        selection = """
        
        0. Back
        1. Add food to order
        2. Remove food to order
        3. Update food to order
                
        Select option: 

        """
        option = int(input(selection))

        while option != 0:
            
            if option == CUST_OPT_ADD_FOOD_TO_ORDER:
                food_id = input("Enter food ID: ")
                food_qty = input("Enter food quantity: ")
                add = self.customer.add_food_to_order(o.order_id, food_id, food_qty, session)
                if add:
                    print("Add successful!")
                else:
                    print("Add not successful. Please try again!")

            elif option == CUST_OPT_REMOVE_FOOD_TO_ORDER:
                food_id = input("Enter food ID: ")
                remove = self.customer.remove_food_to_order(o.order_id, food_id, session)
                if remove:
                    print("Items removed")
                else:
                    print("Items not removed")

            elif option == CUST_OPT_UPDATE_FOOD_TO_ORDER:
                food_id = input("Enter food ID: ")
                food_qty = input("Enter food quantity: ")
                update = self.customer.update_food_to_order(o.order_id, food_id, food_qty, session)
                if update:
                    print("Items updated")
                else:
                    print("Items not updated")

            option = int(input(selection))
        
        if o:
            print("\nYour order is generated. \nOrder number: {}".format(o.order_id))
        else:
            print("Order not generated. Please try again!")

    def view_order(self, order_id):
        session = self.Session()
        view_order_item = self.customer.view_order_per_item(order_id, session)
        if view_order_item:
            for fc, fd, cos in view_order_item:
                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nTotal per item: {}".format(fc.name, fd.food_name, fd.price, cos.food_qty, (fd.price*cos.food_qty)))

        view_order_grand = self.customer.view_order_grand_total(order_id, session)
        if view_order_grand:
            for fd, cos, cd, cosa, t in view_order_grand:
                print("\nCustomer name: {} \nOrder ID: {} \nTotal bill: {}".format(cd.cust_name, cosa.order_id, t))

    def checkout(self, order_id, order_status, order_address, checkout_time, estimated_time, bill_amount):
        session = self.Session()
        c = self.customer.checkout(order_id, order_status, order_address, checkout_time, estimated_time, bill_amount, session) 
        if c:
            print("Checkout sucessful!")
        else:
            print("Checkout not sucessful!") 

    def cancel_order(self, order_id, order_status):
        session = self.Session()
        c = self.customer.cancel_order(order_id, order_status, session) 
        if c:
            print("Cancel sucessful!")
        else:
            print("Cancel not sucessful!") 
        
    def view_orders_status(self, order_id):
        session = self.Session()
        view_order_item = self.customer.view_order_per_item(order_id, session)
        if view_order_item:
            for fc, fd, cos in view_order_item:
                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nTotal per item: {}".format(fc.name, fd.food_name, fd.price, cos.food_qty, (fd.price*cos.food_qty)))
                        
        view_status = self.customer.view_orders_status(order_id, session)
        if view_status:
            for cos, cd, cosa, dp in view_status:                        
                print("\nCustomer name: {} \nOrder ID: {} \nDeliver person name: {} \nOrder status: {} \nTotal price: {}".format(cd.cust_name, cosa.order_id, dp.delivery_person_name, cosa.order_status, cosa.bill_amount))
    # Printing it 3 times - need to review.

class DeliveryPerson(Base, Employee):
    """ Represents delivery person """

    __tablename__ = 'delivery_person'

    delivery_person_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    delivery_person_name = Column(String(30), nullable=False)
    delivery_person_phone = Column(Integer(), nullable=False)

    def update_order(self, order_id, order_status, session):
        """ Delivery person can update the order """

        super(DeliveryPerson, self).__init__()

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

def process_employee_options_flow(fos):
    emp_options = """
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

    """

    employee_options = int(input(emp_options))

    while employee_options != 0:

        if employee_options == EMP_OPT_ADD_FOOD_CATEGORY:
            category_name = input("Enter category name: ")
            fos.add_food_category(category_name)

        elif employee_options == EMP_OPT_ADD_FOOD_DETAILS:
            category_id = input ("Enter category ID: ")
            food_name = input("Enter food name: ")
            price = input("Food price: ")
            fos.add_food_details(category_id, food_name, price)

        elif employee_options == EMP_OPT_ADD_DELIVERY_PERSON:
            delivery_person_name = input("Enter delivery person name: ")
            delivery_person_phone = input("Enter delivery person phone: ")
            fos.add_delivery_person(delivery_person_name, delivery_person_phone)

        elif employee_options == EMP_OPT_ASSIGN_DELIVERY_PERSON_TO_ORDER:
            order_id = input("Enter order ID: ")
            delivery_person_id = input("Enter delivery person ID: ")
            fos.assign_deliver_person_to_deliver_order(order_id, delivery_person_id) 

        elif employee_options == EMP_OPT_UPDATE_ORDER:
            order_id = input("Enter order ID: ")
            select = """                 
            To update order, press
                
            1. En route
            2. Delivered

            Your option: 
 
            """
                
            options = int(input(select))
            if options == EMP_OPT_UO_EN_ROUTE:
                order_status = "En route"
                fos.update_order(order_id, order_status) 

            elif options == EMP_OPT_UO_DELIVERED:
                order_status = "Delivered"
                fos.update_order(order_id, order_status)

        elif employee_options == EMP_OPT_VIEW_ORDER_DETAILS:
            order_id = input("Enter order ID: ")
            fos.view_orders(order_id)
            fos.view_order_grand_total(order_id)

        elif employee_options == EMP_OPT_VIEW_ORDER_STATUS:
            order_id = input("Enter order ID: ")
            fos.view_order_status(order_id)
            fos.view_orders(order_id)

        elif employee_options == EMP_OPT_VIEW_REVENUE_TODAY:
            select = """ 
            To see revenue for a certain status, please press 
                
            1. Checkedout
            2. En route
            3. Delivered
                
            Your option:                 

            """                
            options = int(input(select))
            if options == EMP_OPT_RT_CHECKEDOUT:
                order_status = "Checkedout"
            elif options == EMP_OPT_RT_EN_ROUTE:
                order_status = "En route"
            else:
                order_status = "Delivered"
            fos.view_sales_today(order_status)
            fos.sum_revenue_today(order_status)
                
        elif employee_options == EMP_OPT_DELETE_ORDER:
            order_id = input("Enter order ID: ")
            fos.delete_order(order_id)

        employee_options = int(input(emp_options))

def process_order_flow(fos):
    selection = """ 

    0. Logout
    1. Process order
    2. View order
    3. Checkout
    4. Cancel order
    5. View order status
                
    Select option: 

    """
    order = int(input(selection))

    while order != 0:

        if order == CUST_OPT_PROCESS_ORDER:
            cust_id = input("Enter customer ID: ")
            fos.process_order(cust_id)

        elif order == CUST_OPT_VIEW_ORDER:
            order_id = input("Enter order ID: ")
            fos.view_order(order_id)
                
        elif order == CUST_OPT_CHECKOUT:
            order_id = input("Enter order ID: ")
            order_address = input("Enter delivery address: ")
            checkout = int(input("Press 1 to confirm checkout: "))
            if checkout == 1:
                order_status = "Checkedout"
            checkout_time = datetime.now()
            delivery_time = timedelta(minutes=30)
            estimated_time = checkout_time + delivery_time
            session = fos.Session()
            view_grand_total = fos.customer.view_order_grand_total(order_id, session)
            if view_grand_total:
                for fd, cos, cd, cosa, t in view_grand_total:
                    bill_amount = t
            fos.checkout(order_id, order_status, order_address, checkout_time, estimated_time, bill_amount)

        elif order == CUST_OPT_CANCEL_ORDER:
            order_id = input("Enter order ID: ")
            cancel = int(input("Press 1 to confirm cancellation: "))
            if cancel == 1:
                order_status = "Cancelled"
            fos.cancel_order(order_id, order_status) 

        elif order == CUST_OPT_VIEW_ORDER_STATUS:
            order_id = input("Enter order ID: ")
            fos.view_orders_status(order_id)

        order = int(input(selection))               

def process_customer_options_flow(fos):
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
        
        if customer_options == CUST_OPT_VIEW_MENU:
            fos.view_menu()

        elif customer_options == CUST_OPT_CUSTOMER_SIGNUP:
            cust_name = input("Enter customer name: ")
            cust_phone = input("Enter customer phone number: ")
            cust_email = input("Enter customer email address: ")
            fos.customer_signup(cust_name, cust_phone, cust_email)

        elif customer_options == CUST_OPT_CUSTOMER_LOGIN:
            cust_id = input("Enter customer ID: ")
            c = fos.customer_login(cust_id)
            if c:
                print("Login successful! \nWelcome {} \nCustomer ID {}".format(c.cust_name, c.cust_id))
            else:
                print("Login not sucessfully. Please try again or signup!")
                break
            process_order_flow(fos)

        customer_options = int(input(cust_options))

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

    if option == EMPLOYEE:
        process_employee_options_flow(fos)
    
    elif option == CUSTOMER:
        process_customer_options_flow(fos)

main()