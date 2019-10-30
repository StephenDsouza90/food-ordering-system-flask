from datetime import datetime

from sqlalchemy.exc import IntegrityError

import constants
from models import Employee, Customer, DeliveryPerson, SQLiteBackend


class Controller(SQLiteBackend):
    """ Controller class that inherites from SQLite Backend and composition 
        from Emploeyee, Customer and Delivery Person classes """

    def __init__(self, db_url):
        super(Controller, self).__init__(db_url)
        self.employee = Employee()
        self.customer = Customer()
        self.delivery_person = DeliveryPerson()


    def add_food_category(self, category_name):
        session = self.Session()
        self.employee.add_food_category(category_name, session)
        print("\nAdd {}".format("Successfully" if True else "not successfully"))


    def add_food_details(self, category_id, food_name, price):
        session = self.Session()
        self.employee.add_food_details(category_id, food_name, price, session)
        print("\nAdd {}".format("Successfully" if True else "not successfully"))


    def add_delivery_person(self, delivery_person_name, delivery_person_phone):
        session = self.Session()
        d = self.employee.add_delivery_person(delivery_person_name, delivery_person_phone, session)
        if d:
            print("\nAdd {} \nDeliver person ID: {} ".format(
                "Successfully", d.delivery_person_id if True else  "not successfully"))


    def assign_deliver_person_to_deliver_order(self, order_id, delivery_person_id):
        session = self.Session()
        self.employee.assign_deliver_person_to_deliver_order(order_id, delivery_person_id, session) 
        print("Add {}".format("sucessful" if True else "not sucessful")) 


    def update_order(self, order_id, order_status):
        session = self.Session()
        self.delivery_person.update_order(order_id, order_status, session) 
        print("Order update {}".format("successful" if True else "not successful"))


    def view_orders(self, order_id):
        session = self.Session()
        view_order = self.employee.view_orders(order_id, session)
        if view_order:
            for fc, fd, cos in view_order:
                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nPrice per item: {}".format(
                    fc.name, fd.food_name, fd.price, cos.food_qty, (fd.price*cos.food_qty)))
                

    def view_order_grand_total(self, order_id):
        session = self.Session()
        view_order_grand = self.employee.view_order_grand_total(order_id, session)
        if view_order_grand:
            for cd, cosa in view_order_grand:                        
                print("\nCustomer name: {} \nOrder ID: {} \nTotal bill: {}".format(
                    cd.cust_name, cosa.order_id, cosa.bill_amount))                


    def view_order_status(self, order_id):
        session = self.Session()
        view_status = self.employee.view_order_status(order_id, session)
        if view_status:
            for cd, cosa, dp in view_status:
                print("\nCustomer name: {} \nOrder ID: {} \nDeliver person name: {} \nOrder status: {} \nTotal bill: {}".format(
                    cd.cust_name, cosa.order_id, dp.delivery_person_name, cosa.order_status, cosa.bill_amount))


    def view_sales_today(self, order_status):
        session = self.Session()
        sales_today = self.employee.view_sales_today(order_status, session)
        if sales_today:
            for cos, cd in sales_today:
                print("\nCustomer name: {} \nOrder ID: {} \nOrder Status: {} \nBill amount: {} \nDate & Time: {}".format(
                    cd.cust_name, cos.order_id, cos.order_status, cos.bill_amount, cos.checkout_time))


    def sum_revenue_today(self, order_status):
        session = self.Session()
        sum_rev_today = self.employee.sum_revenue_today(order_status, session)
        if sum_rev_today:
            for cos, s in sum_rev_today:
                print("\nToday's revenue: {} ".format(s))


    def delete_order(self, order_id):
        session = self.Session()
        self.employee.delete_order(order_id, session)
        print("\nOrder {} deleted!".format(order_id))


    def view_menu(self):
        session = self.Session()
        menu = self.customer.view_menu(session)
        for fc, fd in menu:
            print("\nFood ID: {} \nFood category: {} \nFood name: {} \nFood price: {}".format(
                fd.food_id, fc.name, fd.food_name, fd.price))


    def customer_signup(self, cust_name, cust_phone, cust_email):
        session = self.Session()
        c = self.customer.customer_signup(cust_name, cust_phone, cust_email, session)
        if c:
            print("\nSignup {}! Customer ID: {}".format("successfully", c.cust_id if True else "not successfully"))


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

        while option != constants.CUST_OPT_BACK:
            
            if option == constants.CUST_OPT_ADD_FOOD_TO_ORDER:
                food_id = input("Enter food ID: ")
                food_qty = input("Enter food quantity: ")
                self.customer.add_food_to_order(o.order_id, food_id, food_qty, session)
                print("Add {}!".format("successful" if True else "not successful."))

            elif option == constants.CUST_OPT_REMOVE_FOOD_TO_ORDER:
                food_id = input("Enter food ID: ")
                self.customer.remove_food_to_order(o.order_id, food_id, session)
                print("Items {}".format("removed" if True else "not removed"))

            elif option == constants.CUST_OPT_UPDATE_FOOD_TO_ORDER:
                food_id = input("Enter food ID: ")
                food_qty = input("Enter food quantity: ")
                self.customer.update_food_to_order(o.order_id, food_id, food_qty, session)
                print("Items {}".format("updated" if True else "not updated"))

            option = int(input(selection))
        
        if o:
            print("Order {}. \nOrder number: {}".format("generated", o.order_id if True else "not generated"))


    def view_order(self, order_id):
        session = self.Session()
        view_order_item = self.customer.view_order_per_item(order_id, session)
        if view_order_item:
            for fc, fd, cos in view_order_item:
                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nTotal per item: {}".format(
                    fc.name, fd.food_name, fd.price, cos.food_qty, (fd.price*cos.food_qty)))

        view_order_grand = self.customer.view_order_grand_total(order_id, session)
        if view_order_grand:
            for fd, cos, cd, cosa, t in view_order_grand:
                print("\nCustomer name: {} \nOrder ID: {} \nTotal bill: {}".format(cd.cust_name, cosa.order_id, t))


    def checkout(self, order_id, order_status, order_address, checkout_time, estimated_time, bill_amount):
        session = self.Session()
        c = self.customer.checkout(order_id, order_status, order_address, 
                        checkout_time, estimated_time, bill_amount, session) 
        if c:
            print("Checkout {}!".format("successful" if True else "not successful"))


    def cancel_order(self, order_id, order_status):
        session = self.Session()
        c = self.customer.cancel_order(order_id, order_status, session) 
        if c:
            print("Cancel {}!".format("successful" if True else "not successful"))
        

    def view_orders_status(self, order_id):
        session = self.Session()
        view_order_item = self.customer.view_order_per_item(order_id, session)
        if view_order_item:
            for fc, fd, cos in view_order_item:
                print("\nFood category: {} \nFood name: {} \nFood price: {} \nFood quantity: {} \nTotal per item: {}".format(
                    fc.name, fd.food_name, fd.price, cos.food_qty, (fd.price*cos.food_qty)))
                        
        view_status = self.customer.view_orders_status(order_id, session)
        if view_status:
            for cos, cd, cosa, dp in view_status:                        
                print("\nCustomer name: {} \nOrder ID: {} \nDeliver person name: {} \nOrder status: {} \nTotal price: {}".format(
                    cd.cust_name, cosa.order_id, dp.delivery_person_name, cosa.order_status, cosa.bill_amount))
    # Printing it 3 times - need to review.