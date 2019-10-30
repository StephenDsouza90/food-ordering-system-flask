from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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


class DeliveryPerson(Base, Employee):
    """ Represents delivery person """

    __tablename__ = 'delivery_person'

    delivery_person_id = Column(Integer(), primary_key=True, nullable=False, unique=True, autoincrement=True)
    delivery_person_name = Column(String(30), nullable=False)
    delivery_person_phone = Column(Integer(), nullable=False)


    def update_order(self, order_id, order_status, session):
        """ Delivery person can update the order """

        super(DeliveryPerson, self).__init__()

        update = session.query(CustOrderStatus).\
                    filter(CustOrderStatus.order_id == order_id).\
                    update({CustOrderStatus.order_status: order_status}, 
                    synchronize_session=False)
        try:
            session.commit()
            return update
        except:
            session.rollback()
            raise Exception("update not completed!")
        finally:
            session.expunge_all()
            session.close()