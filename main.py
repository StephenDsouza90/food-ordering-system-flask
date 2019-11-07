from datetime import datetime, timedelta

import constants
from core import Controller


def process_employee_options_flow(fos):
    emp_options = """
    Welcome to the employee interface! Please press the below options:
        
    0. Quit                                 5. Update order (Only for delivery person use)
    1. Add food category                    6. View order details
    2. Add food details                     7. View order status
    3. Add delivery person                  8. View revenue/sales today
    4. Assign delivery person to order      9. Delete order
    
    Your Option:
    """

    employee_options = int(input(emp_options))

    while employee_options != constants.EMP_OPT_QUIT:

        if employee_options == constants.EMP_OPT_ADD_FOOD_CATEGORY:
            category_name = input("Enter category name: ")
            fos.add_food_category(category_name)

        elif employee_options == constants.EMP_OPT_ADD_FOOD_DETAILS:
            category_id = input ("Enter category ID: ")
            food_name = input("Enter food name: ")
            price = input("Food price: ")
            fos.add_food_details(category_id, food_name, price)

        elif employee_options == constants.EMP_OPT_ADD_DELIVERY_PERSON:
            delivery_person_name = input("Enter delivery person name: ")
            delivery_person_phone = input("Enter delivery person phone: ")
            fos.add_delivery_person(delivery_person_name, delivery_person_phone)

        elif employee_options == constants.EMP_OPT_ASSIGN_DELIVERY_PERSON_TO_ORDER:
            order_id = input("Enter order ID: ")
            delivery_person_id = input("Enter delivery person ID: ")
            fos.assign_deliver_person_to_deliver_order(order_id, delivery_person_id) 

        elif employee_options == constants.EMP_OPT_UPDATE_ORDER:
            order_id = input("Enter order ID: ")
            select = """                 
            To update order, press
                
            1. En route
            2. Delivered

            Your option: 
 
            """
                
            options = int(input(select))
            if options == constants.EMP_OPT_UO_EN_ROUTE:
                order_status = "En route"
                fos.update_order(order_id, order_status) 

            elif options == constants.EMP_OPT_UO_DELIVERED:
                order_status = "Delivered"
                fos.update_order(order_id, order_status)

        elif employee_options == constants.EMP_OPT_VIEW_ORDER_DETAILS:
            order_id = input("Enter order ID: ")
            fos.view_order(order_id)
            fos.view_order_grand_total(order_id)

        elif employee_options == constants.EMP_OPT_VIEW_ORDER_STATUS:
            order_id = input("Enter order ID: ")
            fos.view_order_status(order_id)

        elif employee_options == constants.EMP_OPT_VIEW_REVENUE_TODAY:
            select = """ 
            To see revenue for a certain status, please press 
                
            1. Checkedout
            2. En route
            3. Delivered
                
            Your option:                 
            """                
            options = int(input(select))
            if options == constants.EMP_OPT_RT_CHECKEDOUT:
                order_status = "'Checkedout'"
            elif options == constants.EMP_OPT_RT_EN_ROUTE:
                order_status = "'En route'"
            else:
                order_status = "'Delivered'"
            fos.view_sales_today(order_status)
            fos.sum_revenue_today(order_status)
                
        elif employee_options == constants.EMP_OPT_DELETE_ORDER:
            order_id = input("Enter order ID: ")
            fos.delete_order(order_id)

        employee_options = int(input(emp_options))


def process_order_flow(fos):
    selection = """ 
    0. Logout                   3. Checkout
    1. Process order            4. Cancel order
    2. View order               5. View order status
    
    Select option: 
    """
    order = int(input(selection))

    while order != constants.CUST_OPT_LOGOUT:

        if order == constants.CUST_OPT_PROCESS_ORDER:
            cust_id = input("Enter customer ID: ")
            fos.process_order(cust_id)

        elif order == constants.CUST_OPT_VIEW_ORDER:
            order_id = input("Enter order ID: ")
            fos.view_order(order_id)
            fos.view_order_grand_total(order_id)
                
        elif order == constants.CUST_OPT_CHECKOUT:
            order_id = input("Enter order ID: ")
            order_address = input("Enter delivery address: ")
            checkout = int(input("Press 1 to confirm checkout: "))
            if checkout == constants.CUST_OPT_CHECKEDOUT:
                order_status = "Checkedout"
            checkout_time = datetime.now()
            delivery_time = timedelta(minutes=30)
            estimated_time = checkout_time + delivery_time
            session = fos.Session()
            view_grand_total = fos.common_func.view_order_grand_total(session, order_id) # sums bill
            if view_grand_total:
                for cd, cosa, grand_total in view_grand_total:
                    bill_amount = grand_total
            fos.checkout(order_id, order_status, order_address, checkout_time, estimated_time, bill_amount)

        elif order == constants.CUST_OPT_CANCEL_ORDER:
            order_id = input("Enter order ID: ")
            cancel = int(input("Press 1 to confirm cancellation: "))
            if cancel == constants.CUST_OPT_CANCELLED:
                order_status = "Cancelled"
            fos.cancel_order(order_id, order_status) 

        elif order == constants.CUST_OPT_VIEW_ORDER_STATUS:
            order_id = input("Enter order ID: ")
            fos.view_order_status(order_id)

        order = int(input(selection))               


def process_customer_options_flow(fos):
    cust_options = """ 
    Welcome to the customer interface! Please press the below options:
        
    0. Quit                 2. Customer signup
    1. View menu            3. Customer login
    
    Your Option:
    """        
        
    customer_options = int(input(cust_options))

    while customer_options != constants.CUST_OPT_QUIT:
        
        if customer_options == constants.CUST_OPT_VIEW_MENU:
            fos.view_menu()

        elif customer_options == constants.CUST_OPT_CUSTOMER_SIGNUP:
            cust_name = input("Enter customer name: ")
            cust_phone = input("Enter customer phone number: ")
            cust_email = input("Enter customer email address: ")
            fos.customer_signup(cust_name, cust_phone, cust_email)

        elif customer_options == constants.CUST_OPT_CUSTOMER_LOGIN:
            cust_id = input("Enter customer ID: ")
            c = fos.customer_login(cust_id)
            if c:
                print("Login successful! \nWelcome {}".format(c.cust_name))
                process_order_flow(fos)
            else:
                print("Login not successfully. Please try again or signup!")
                            
        customer_options = int(input(cust_options))


def main():
    """ The user interface in which employee/customer will use to 
    perform actions on the Food Ordering System. """

    db_url = "sqlite:///fos2.db"
    print("Connecting to {}".format(db_url))

    fos = Controller(db_url)
    fos.bootstrap()

    welcome_message = """ 
    Welcome to the Food Ordering System! Please press the below options:

    1. Employee             2. Customer

    Your Option:
    """

    option = int(input(welcome_message))

    if option == constants.EMPLOYEE:
        process_employee_options_flow(fos)
    
    elif option == constants.CUSTOMER:
        process_customer_options_flow(fos)

main()