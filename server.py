import flask
from flask import Flask, json
import waitress

from datetime import datetime, timedelta

from core import Controller
from models import FoodCategory, FoodDetails, CustomerDetails, CustOrderSelection, CustOrderStatus


not_found = {"message": "Not Found"}
success = {"message": "Success"}
failed = {"message": "Failed"}

 
def create_app(fos):
    """
    Creates the server app.
    """
    app = Flask('Food Ordering System')

    ### employee routes
    @app.route('/employee/add_food_category', methods=['POST'])
    def add_food_category():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"drinks\"}" "localhost:8080/employee/add_food_category"
        """
        name = flask.request.json["name"]
        add = fos.add_food_category(name)
        return json.dumps("{}".format(success if add else failed))
    
    @app.route('/employee/add_food_details', methods=['POST'])
    def add_food_details():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":4, \"food_name\":\"vodka\", \"price\":2}" "localhost:8080/employee/add_food_details"
        """
        category_id = flask.request.json["category_id"]
        food_name = flask.request.json["food_name"]
        price = flask.request.json["price"]
        add = fos.add_food_details(category_id, food_name, price)
        return json.dumps("{}".format(success if add else failed))

    @app.route('/employee/add_delivery_person', methods=['POST'])
    def add_delivery_person():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"delivery_person_name\":\"test\", \"delivery_person_phone\":11}" "localhost:8080/employee/add_delivery_person"
        """
        delivery_person_name = flask.request.json["delivery_person_name"]
        delivery_person_phone = flask.request.json["delivery_person_phone"]
        add = fos.add_delivery_person(delivery_person_name, delivery_person_phone)
        return json.dumps("{}".format(success if add else failed))

    @app.route('/employee/assign_deliver_person_to_deliver_order', methods=['PUT'])
    def assign_deliver_person_to_deliver_order():
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":9, \"delivery_person_id\":2}" "localhost:8080/employee/assign_deliver_person_to_deliver_order"
        """
        order_id = flask.request.json["order_id"]
        delivery_person_id = flask.request.json["delivery_person_id"]
        assign = fos.assign_deliver_person_to_deliver_order(order_id, delivery_person_id)
        return json.dumps("{}".format(success if assign else failed))

    @app.route('/employee/update_order', methods=['PUT'])
    def update_order():
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":9, \"order_status\":\"En route\"}" "localhost:8080/employee/update_order"
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":9, \"order_status\":\"Delivered\"}" "localhost:8080/employee/update_order"
        """
        order_id = flask.request.json["order_id"]
        order_status = flask.request.json["order_status"]
        update = fos.update_order(order_id, order_status)
        return json.dumps("{}".format(success if update else failed))

    @app.route('/employee/view_sales_today', methods=['GET'])
    def view_sales_today():
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Delivered'\"}" "localhost:8080/employee/view_sales_today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'En route'\"}" "localhost:8080/employee/view_sales_today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employee/view_sales_today"
        """
        order_status = flask.request.json["order_status"]
        sales_today = fos.view_sales_today(order_status)
        result = []
        for i in sales_today:
            sales_dict = {
                "customer_name": i.cust_name,
                "order_id": i.order_id,
                "order_status": i.order_status,
                "bill_amount": i.bill_amount,
                "date_time": i.checkout_time
            }
            result.append(sales_dict)
        return json.dumps(result)

    @app.route('/employee/sum_revenue_today', methods=['GET'])
    def sum_revenue_today():
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Delivered'\"}" "localhost:8080/employee/sum_revenue_today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'En route'\"}" "localhost:8080/employee/sum_revenue_today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employee/sum_revenue_today"
        """
        order_status = flask.request.json["order_status"]
        sum_rev_today = fos.sum_revenue_today(order_status)
        for sum in sum_rev_today:
            revObj = sum[0]
            rev_dict = {
                "today_revenue": revObj
            }
            return json.dumps(rev_dict)
        print("Not found")
        return json.dumps(not_found), 404

    @app.route('/employee/delete_order', methods=['DELETE'])
    def delete_order():
        """
        >> curl -H "Content-Type: application/json" -XDELETE -d "{\"order_id\":2}" "localhost:8080/employee/delete_order"
        """
        order_id = flask.request.json["order_id"]
        delete = fos.delete_order(order_id)
        return json.dumps("{}".format(success if delete else failed))
    
    ### customer routes
    @app.route('/customer/view_menu', methods=['GET'])
    def view_menu():
        """
        >> curl localhost:8080/customer/view_menu
        """
        menu = fos.view_menu()

        # List of food objects to be returned to the client
        result = []

        # Loop through each menu item and convert each to a dict
        # to be compatible for json.
        for m in menu:
            # m is a tuple(FoodCategory, FoodDetails)
            # Get the FoodCategory obj from the menu
            foodCatObj = m[0]
            # Get the FoodDetails obj from the menu
            foodDetObj = m[1]

            # Add converted dict to resulting menu list
            foodDictObj = {
                "category_id": foodCatObj.category_id,
                "category_name": foodCatObj.name,
                "food_id": foodDetObj.food_id,
                "food_name": foodDetObj.food_name,
                "price": foodDetObj.price
                }

            # Add converted dict to resulting menu list
            result.append(foodDictObj)
        return json.dumps(result)


    @app.route('/customer/signup', methods=['POST'])
    def customer_signup():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"cust_name\":\"test\", \"cust_phone\":11, \"cust_email\":\"test\"}" "localhost:8080/customer/signup"
        """
        # Customer information saved in objects
        cust_name = flask.request.json["cust_name"]
        cust_phone = flask.request.json["cust_phone"]
        cust_email = flask.request.json["cust_email"]

        # Information sent to controller to be stored in database
        cust = fos.customer_signup(cust_name, cust_phone, cust_email)

        # Information returned to client
        cust_obj = {
            "customer_id": cust.cust_id,
            "customer_name": cust.cust_name
            }
        return json.dumps(cust_obj)

    @app.route('/customer/login/<int:cust_id>', methods=['GET'])
    def customer_login(cust_id):
        """
        >> curl -X GET "localhost:8080/customer/login/2"
        """
        cust = fos.customer_login(cust_id)

        # Converted object to dict        
        custDictObj = cust.convert_to_dict()

        # Returned cust id to client
        cust_id = custDictObj["cust_id"]
        print("Login successful for cust ID {}".format(cust_id))
        return json.dumps({"cust_id": cust_id})

    @app.route('/customer/create_order/<int:cust_id>', methods=['POST'])
    def create_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"cust_id\":2}" "localhost:8080/customer/create_order/2"
        """
        cust_id = flask.request.json["cust_id"]
        gen_order_id = fos.create_order(cust_id) 
        order_obj = {
            "customer_id": gen_order_id.cust_id,
            "order_id": gen_order_id.order_id
            }
        return json.dumps(order_obj)

    @app.route('/customer/add_food_to_order/<int:cust_id>', methods=['POST'])
    def add_food_to_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":9, \"food_id\":1, \"food_qty\":1}" "localhost:8080/customer/add_food_to_order/2"
        """
        order_id = flask.request.json["order_id"]
        food_id = flask.request.json["food_id"]
        food_qty = flask.request.json["food_qty"]
        add_food = fos.add_food_to_order(order_id, food_id, food_qty) 
        order_obj = {
            "order_id": add_food.order_id,
            "food_id": add_food.food_id,
            "food_qty": add_food.food_qty
            }
        return json.dumps(order_obj)

    @app.route('/customer/update_food_to_order/<int:cust_id>', methods=['PUT'])
    def update_process_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":9, \"food_id\":1, \"food_qty\":2}" "localhost:8080/customer/update_food_to_order/2"
        """
        order_id = flask.request.json["order_id"]
        food_id = flask.request.json["food_id"]
        food_qty = flask.request.json["food_qty"]
        fos.update_food_to_order(order_id, food_id, food_qty)
        order_obj = {
            "order_id": order_id,
            "food_id": food_id,
            "food_qty": food_qty
            }
        return json.dumps(order_obj)

    @app.route('/customer/remove_food_to_order/<int:cust_id>', methods=['DELETE'])
    def remove_food_to_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -XDELETE -d "{\"order_id\":9, \"food_id\":1}" "localhost:8080/customer/remove_food_to_order/2"
        """
        order_id = flask.request.json["order_id"]
        food_id = flask.request.json["food_id"]
        fos.remove_food_to_order(order_id, food_id)
        order_obj = {
            "order_id": order_id,
            "food_id": food_id
            }
        return json.dumps(order_obj)
           
    @app.route('/customer/checkout/<int:cust_id>', methods=['PUT'])
    def checkout(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":9, \"order_address\":\"Karachi\"}" "localhost:8080/customer/checkout/2"
        """
        order_id = flask.request.json["order_id"]
        order_status = "Checkedout"
        order_address = flask.request.json["order_address"]
        checkout_time = datetime.now()
        delivery_time = timedelta(minutes=30)
        estimated_time = checkout_time + delivery_time
        total = fos.view_order_grand_total(order_id)
        if total:
            for cd, cosa, grand_total in total:
                bill_amount = grand_total
        fos.checkout(order_id, order_status, order_address, checkout_time, estimated_time, bill_amount)
        return json.dumps("Checkout successful")

    @app.route('/customer/cancel_order/<int:cust_id>', methods=['PUT'])
    def cancel_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":9}" "localhost:8080/customer/cancel_order/2"
        """
        order_id = flask.request.json["order_id"]
        order_status = "Cancelled"
        fos.cancel_order(order_id, order_status) 
        return json.dumps("Order cancelled")

    ### Common functions
    @app.route('/customer/view_order/<int:cust_id>', methods=['GET'])
    def view_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":9}" "localhost:8080/customer/view_order/2"
        """
        order_id = flask.request.json["order_id"]
        view_order_item = fos.view_order(order_id)
        result = []
        for fc, fd, cos in view_order_item:
            item_dict = {
                "food_category": fc.name,
                "food_name": fd.food_name,
                "food_price": fd.price,
                "food_quantity": cos.food_qty,
                "total_per_item": (fd.price*cos.food_qty)
                }
            result.append(item_dict)
        return json.dumps(result)
    # Need to review - some problem with SQLite and session but the func works fine
    # Create a view order for employee

    @app.route('/customer/view_order_grand_total/<int:cust_id>', methods=['GET'])
    def view_order_grand_total(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":9}" "localhost:8080/customer/view_order_grand_total/2"
        """
        order_id = flask.request.json["order_id"]
        view_grand_total = fos.view_order_grand_total(order_id)
        for cd, cost, grand_total in view_grand_total:
            dict_grand_total = {
                "customer_name": cd.cust_name,
                "order_id": cost.order_id,
                "grand_total": grand_total
                }
        return json.dumps(dict_grand_total)
    # Need to review - some problem with SQLite and session but the func works fine
    # Create a view order grand total for employee
    
    @app.route('/customer/view_order_status/<int:cust_id>', methods=['GET'])
    def view_order_status(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":9}" "localhost:8080/customer/view_order_status/2"
        """
        order_id = flask.request.json["order_id"]
        view_status = fos.view_order_status(order_id)
        for cd, cosa, dp in view_status:
            dict_status = {
                "customer_name": cd.cust_name,
                "order_id": cosa.order_id,
                "delivery_person_name": dp.delivery_person_name,
                "order_status": cosa.order_status,
                "total_bill": cosa.bill_amount
                }
        return json.dumps(dict_status)
    # Need to review - some problem with SQLite and session but the func works fine
    # Create a view_order_status for employee

    return app


def main():
    """
    Run the server.
    """
    db_url = "sqlite:///fos2.db"
    print("Connecting to {}".format(db_url))
    fos = Controller(db_url)
    fos.bootstrap()
    app = create_app(fos)
    waitress.serve(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()