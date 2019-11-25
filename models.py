import time
from datetime import datetime, date
import json

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy import create_engine, func
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def handle_session(f):

    def wrapper(self, *args, **kwargs):
        session = self.Session()
        try:
            result = f(self, session, *args, **kwargs)
            return result
        except IntegrityError:
            session.rollback()
            raise Exception("Error")
        finally:
            session.expunge_all()
            session.close()    
    return wrapper


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


class FoodCategory(Base):
    """ Represents food categories """

    __tablename__ = 'food_category'

    category_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = Column(String(30), nullable=False)

    def convert_to_dict(self):
        obj_dict = {
            "category_id":self.category_id, 
            "name":self.name
            }
        return obj_dict


class FoodDetails(Base):
    """ Represents food details """

    __tablename__ = 'food_details'

    food_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    category_id = Column(Integer(), ForeignKey('food_category.category_id'), nullable=False)
    food_name = Column(String(30), nullable=False)
    price = Column(Integer(), nullable=False)

    def convert_to_dict(self):
        obj_dict = {
            "food_id":self.food_id, 
            "category_id":self.category_id, 
            "food_name":self.food_name, 
            "price":self.price
            }
        return obj_dict


class CustomerDetails(Base):
    """ Represents customer details """

    __tablename__ = 'customer_details'

    cust_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    cust_name = Column(String(30), nullable=False)
    cust_phone = Column(Integer())
    cust_email = Column(String(30))

    def convert_to_dict(self):
        obj_dict = {
            "cust_id":self.cust_id, 
            "cust_name":self.cust_name,
            "cust_phone":self.cust_phone, 
            "cust_email":self.cust_email
            }
        return obj_dict


class CustOrderSelection(Base):    
    """ Represents food ordered """

    __tablename__ = 'customer_order_selection'

    order_id = Column(Integer(), ForeignKey('customer_order_status.order_id'), primary_key=True, nullable=False)
    food_id = Column(Integer(), ForeignKey('food_details.food_id'), primary_key=True)  
    food_qty = Column(Integer())

    def convert_to_dict(self):
        obj_dict = {
            "order_id":self.order_id, 
            "food_id":self.food_id,
            "food_qty":self.food_qty
            }
        return obj_dict


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

    def convert_to_dict(self):
        obj_dict = {
            "order_id":self.order_id, 
            "cust_id":self.cust_id,
            "delivery_person_id":self.delivery_person_id,
            "checkout_time":self.checkout_time, 
            "estimated_time":self.estimated_time,
            "order_status":self.order_status, 
            "order_address":self.order_address,
            "bill_amount":self.bill_amount
            }
        return obj_dict


class Employee:
    """ Restaurant's end operation """

    def add_food_category(self, session, category_name):
        """ Insert a new food category """

        category = FoodCategory(name=category_name)
        session.add(category)
        session.commit()
        return category

    def add_food_details(self, session, category_id, food_name, price):
        """ Insert new food details """

        details = FoodDetails(category_id=category_id, food_name=food_name, price=price)
        session.add(details)
        session.commit()
        return details

    def add_delivery_person(self, session, delivery_person_name, delivery_person_phone):
        """ Insert new delivery person """

        details = DeliveryPerson(delivery_person_name=delivery_person_name, 
                    delivery_person_phone=delivery_person_phone)
        session.add(details)
        session.commit()
        return details

    def assign_deliver_person_to_deliver_order(self, session, order_id, delivery_person_id):
        """ Update CustOrderStatus table to add deliver person to deliver order """

        update = session.query(CustOrderStatus).\
                    filter(CustOrderStatus.order_id == order_id).\
                    update({CustOrderStatus.delivery_person_id: delivery_person_id}, 
                    synchronize_session=False)
        session.commit()
        return update
        
    def view_sales_today(self, session, order_status):
        """ View revenue/sales of today """

        sales_today = text("""SELECT cd.cust_name, cos.order_id, cos.order_status, cos.bill_amount, cos.checkout_time 
            FROM customer_order_status as cos 
            JOIN customer_details as cd 
                ON cd.cust_id = cos.cust_id 
            WHERE cos.order_status = {} AND date(cos.checkout_time) = date(CURRENT_DATE);""".format(order_status))
        result = session.connection().execute(sales_today).fetchall()
        return result
            
    def sum_revenue_today(self, session, order_status):
        """ Sum revenue/sales of today """

        rev = text("""SELECT IFNULL(SUM(cos.bill_amount), 0) 
            FROM customer_order_status as cos 
            WHERE cos.order_status = {} AND date(cos.checkout_time) = date(CURRENT_DATE);""".format(order_status))
        result = session.connection().execute(rev).scalar()
        return result

    def delete_order(self, session, order_id):
        """ Delete order """

        del_status = session.query(CustOrderStatus).filter_by(order_id=order_id).delete()
        del_selection = session.query(CustOrderSelection).filter_by(order_id=order_id).delete()
        session.commit()
        return del_status, del_selection


class Customer:
    """ Customer's end operation """    

    def view_menu(self, session):
        """ Customer can view menu """

        menu = session.query(FoodCategory, FoodDetails).\
                filter(FoodCategory.category_id == FoodDetails.category_id).all()
        return menu

    def customer_signup(self, session, cust_name, cust_phone, cust_email):
        """ Add a new customer """

        signup = CustomerDetails(cust_name=cust_name, cust_phone=cust_phone, cust_email=cust_email)
        session.add(signup)
        session.commit()
        return signup

    def customer_login(self, session, cust_id):
        """ Customer can login into their account """

        login = session.query(CustomerDetails).filter_by(cust_id=cust_id).first()
        return login
         
    def create_order_id(self, session, cust_id): 
        """ Generate order id """

        order_status = CustOrderStatus(cust_id=cust_id)
        session.add(order_status)
        session.commit()
        return order_status

    def add_food_to_order(self, session, order_id, food_id, food_qty): 
        """ Add food items """

        add = CustOrderSelection(order_id=order_id, food_id=food_id, food_qty=food_qty)
        session.add(add)
        session.commit()
        return add
    
    def remove_food_to_order(self, session, order_id, food_id):
        """ Remove food items """

        remove = session.query(CustOrderSelection).\
                    filter_by(order_id=order_id).filter_by(food_id=food_id).\
                    delete()
        session.commit()
        return remove
    
    def update_food_to_order(self, session, order_id, food_id, food_qty):
        """ Update food items """

        update = session.query(CustOrderSelection).\
                    filter(CustOrderSelection.order_id == order_id).\
                    filter(CustOrderSelection.food_id == food_id).\
                    update({CustOrderSelection.food_qty: food_qty}, 
                    synchronize_session=False)
        session.commit()
        return update
                    
    def checkout(self, session, order_id, order_status, order_address, checkout_time, estimated_time, bill_amount):
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
        session.commit()
        return checkout_update
    
    def cancel_order(self, session, order_id, order_status):
        """ Cancel order """

        update = session.query(CustOrderStatus).\
                    filter(CustOrderStatus.order_id == order_id).\
                    update({CustOrderStatus.order_status: order_status}, 
                    synchronize_session=False)
        session.commit()
        return update
    

class DeliveryPerson(Base, Employee):
    """ Represents delivery person """

    __tablename__ = 'delivery_person'

    delivery_person_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    delivery_person_name = Column(String(30), nullable=False)
    delivery_person_phone = Column(Integer(), nullable=False)

    def convert_to_dict(self):
        obj_dict = {
            "delivery_person_id":self.delivery_person_id, 
            "delivery_person_name":self.delivery_person_name,
            "delivery_person_phone":self.delivery_person_phone
            }
        return obj_dict

    def update_order(self, session, order_id, order_status):
        """ Delivery person can update the order """

        super(DeliveryPerson, self).__init__()

        update = session.query(CustOrderStatus).\
                    filter(CustOrderStatus.order_id == order_id).\
                    update({CustOrderStatus.order_status: order_status}, 
                    synchronize_session=False)
        session.commit()
        return update


def view_order(session, order_id):
    """ Employee/Customer can view details of a particular order """

    view = session.query(FoodCategory, FoodDetails, CustOrderSelection).\
            filter(CustOrderSelection.food_id == FoodDetails.food_id).\
            filter(FoodCategory.category_id == FoodDetails.category_id).\
            filter(CustOrderSelection.order_id == order_id)
    return view


def view_order_grand_total(session, order_id):
    """ Employee/Customer can view the grand total of an order """

    view = session.query(
            CustomerDetails, CustOrderStatus, func.sum(CustOrderSelection.food_qty*FoodDetails.price)).\
                filter(CustOrderSelection.food_id == FoodDetails.food_id).\
                filter(CustOrderSelection.order_id == CustOrderStatus.order_id).\
                filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
                filter(CustOrderSelection.order_id == order_id)            
    return view


def view_order_status(session, order_id):
    """ Employee/Customer can view status of the order """

    view = session.query(CustomerDetails, CustOrderStatus, DeliveryPerson).\
            filter(CustomerDetails.cust_id == CustOrderStatus.cust_id).\
            filter(DeliveryPerson.delivery_person_id == CustOrderStatus.delivery_person_id).\
            filter(CustOrderStatus.order_id == order_id)
    return view