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

    @app.route('/employees/add-food-category', methods=['POST'])
    def add_food_category():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"meals\"}" "localhost:8080/employees/add-food-category"
        """
        name = flask.request.json["name"]
        food_category = fos.add_food_category(name)
        catDictObj = {
            "category_id": food_category.category_id,
            "category_name": food_category.name
        }
        return json.dumps(catDictObj)
    
    @app.route('/employees/add-food-details', methods=['POST'])
    def add_food_details():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":1, \"food_name\":\"biryani\", \"price\":5}" "localhost:8080/employees/add-food-details"
        """
        category_id = flask.request.json["category_id"]
        food_name = flask.request.json["food_name"]
        price = flask.request.json["price"]
        food_details = fos.add_food_details(category_id, food_name, price)
        detDictObj = {
            "category_id": food_details.category_id,
            "food_id": food_details.food_id,
            "food_name": food_details.food_name,
            "food_price": food_details.price
        }
        return json.dumps(detDictObj)

    @app.route('/employees/add-delivery-person', methods=['POST'])
    def add_delivery_person():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"delivery_person_name\":\"test\", \"delivery_person_phone\":111}" "localhost:8080/employees/add-delivery-person"
        """
        delivery_person_name = flask.request.json["delivery_person_name"]
        delivery_person_phone = flask.request.json["delivery_person_phone"]
        delivery_person = fos.add_delivery_person(delivery_person_name, delivery_person_phone)
        delDictObj = {
            "delivery_person_id": delivery_person.delivery_person_id,
            "delivery_person_name": delivery_person.delivery_person_name,
            "delivery_person_phone": delivery_person.delivery_person_phone
        }
        return json.dumps(delDictObj)

    @app.route('/employees/assign-deliver-person-to-deliver-order', methods=['PUT'])
    def assign_deliver_person_to_deliver_order():
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"delivery_person_id\":1}" "localhost:8080/employees/assign-deliver-person-to-deliver-order"
        """
        order_id = flask.request.json["order_id"]
        delivery_person_id = flask.request.json["delivery_person_id"]
        fos.assign_deliver_person_to_deliver_order(order_id, delivery_person_id)
        assignDictObj = {
            "order_id": order_id,
            "delivery_person_id": delivery_person_id
        }
        return json.dumps(assignDictObj)

    @app.route('/employees/update-order', methods=['PUT'])
    def update_order():
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"order_status\":\"En route\"}" "localhost:8080/employees/update-order"
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"order_status\":\"Delivered\"}" "localhost:8080/employees/update-order"
        """
        order_id = flask.request.json["order_id"]
        order_status = flask.request.json["order_status"]
        fos.update_order(order_id, order_status)
        updateDictObj = {
            "order_id": order_id,
            "order_status": order_status
        }
        return json.dumps(updateDictObj)

    @app.route('/employees/view-sales-today', methods=['GET'])
    def view_sales_today():
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Delivered'\"}" "localhost:8080/employees/view-sales-today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'En route'\"}" "localhost:8080/employees/view-sales-today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/view-sales-today"
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

    @app.route('/employees/sum-revenue-today', methods=['GET'])
    def sum_revenue_today():
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Delivered'\"}" "localhost:8080/employees/sum-revenue-today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'En route'\"}" "localhost:8080/employees/sum-revenue-today"
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/sum-revenue-today"
        """
        order_status = flask.request.json["order_status"]
        sum_rev_today = fos.sum_revenue_today(order_status)
        revDictObj = {
            "today_revenue": sum_rev_today
            }
        return json.dumps(revDictObj)

    @app.route('/employees/delete-order', methods=['DELETE'])
    def delete_order():
        """
        >> curl -H "Content-Type: application/json" -XDELETE -d "{\"order_id\":1}" "localhost:8080/employees/delete-order"
        """
        order_id = flask.request.json["order_id"]
        fos.delete_order(order_id)
        delDictObj = {
            "order_id": order_id
        }
        return json.dumps(delDictObj)
    
    @app.route('/customers/view-menu', methods=['GET'])
    def view_menu():
        """
        >> curl localhost:8080/customers/view-menu
        """
        menu = fos.view_menu()
        result = []
        for m in menu:
            foodCatObj = m[0]
            foodDetObj = m[1]
            foodDictObj = {
                "category_id": foodCatObj.category_id,
                "category_name": foodCatObj.name,
                "food_id": foodDetObj.food_id,
                "food_name": foodDetObj.food_name,
                "price": foodDetObj.price
                }
            result.append(foodDictObj)
        return json.dumps(result)

    @app.route('/customers/signup', methods=['POST'])
    def customer_signup():
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"cust_name\":\"test\", \"cust_phone\":111, \"cust_email\":\"test\"}" "localhost:8080/customers/signup"
        """
        cust_name = flask.request.json["cust_name"]
        cust_phone = flask.request.json["cust_phone"]
        cust_email = flask.request.json["cust_email"]
        cust = fos.customer_signup(cust_name, cust_phone, cust_email)
        custDictObj = {
            "customer_id": cust.cust_id,
            "customer_name": cust.cust_name,
            "customer_email": cust.cust_email
            }
        return json.dumps(custDictObj)

    @app.route('/customers/<int:cust_id>/login', methods=['GET'])
    def customer_login(cust_id):
        """
        >> curl -X GET "localhost:8080/customers/1/login"
        """
        cust = fos.customer_login(cust_id)
        custDictObj = cust.convert_to_dict()
        cust_id = custDictObj["cust_id"]
        cust_name = custDictObj["cust_name"]
        loginDictObj = {
            "cust_id": cust_id,
            "cust_name": cust_name
            }
        return json.dumps(loginDictObj)

    @app.route('/customers/<int:cust_id>/create-order', methods=['POST'])
    def create_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"cust_id\":1}" "localhost:8080/customers/1/create-order"
        """
        cust_id = flask.request.json["cust_id"]
        gen_order_id = fos.create_order(cust_id) 
        orderDictObj = {
            "customer_id": gen_order_id.cust_id,
            "order_id": gen_order_id.order_id
            }
        return json.dumps(orderDictObj)

    @app.route('/customers/<int:cust_id>/add-food-to-order', methods=['POST'])
    def add_food_to_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":1, \"food_id\":1, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"
        """
        order_id = flask.request.json["order_id"]
        food_id = flask.request.json["food_id"]
        food_qty = flask.request.json["food_qty"]
        add_food = fos.add_food_to_order(order_id, food_id, food_qty)
        orderDictObj = {
            "order_id": add_food.order_id,
            "food_id": add_food.food_id,
            "food_qty": add_food.food_qty
            }
        return json.dumps(orderDictObj)

    @app.route('/customers/<int:cust_id>/update-food-to-order', methods=['PUT'])
    def update_process_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"food_id\":1, \"food_qty\":2}" "localhost:8080/customers/1/update-food-to-order"
        """
        order_id = flask.request.json["order_id"]
        food_id = flask.request.json["food_id"]
        food_qty = flask.request.json["food_qty"]
        fos.update_food_to_order(order_id, food_id, food_qty)
        orderDictObj = {
            "order_id": order_id,
            "food_id": food_id,
            "food_qty": food_qty
            }
        return json.dumps(orderDictObj)

    @app.route('/customers/<int:cust_id>/remove-food-to-order', methods=['DELETE'])
    def remove_food_to_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -XDELETE -d "{\"order_id\":1, \"food_id\":2}" "localhost:8080/customers/1/remove-food-to-order"
        """
        order_id = flask.request.json["order_id"]
        food_id = flask.request.json["food_id"]
        fos.remove_food_to_order(order_id, food_id)
        orderDictObj = {
            "order_id": order_id,
            "food_id": food_id
            }
        return json.dumps(orderDictObj)

    @app.route('/customers/<int:cust_id>/checkout', methods=['PUT'])
    def checkout(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"order_address\":\"Karachi\"}" "localhost:8080/customers/1/checkout"
        """
        order_id = flask.request.json["order_id"]
        order_status = "Checkedout"
        order_address = flask.request.json["order_address"]
        checkout_time = datetime.now()
        delivery_time = timedelta(minutes=30)
        estimated_time = checkout_time + delivery_time
        total = fos.view_order_grand_total(order_id)
        if total:
            bill_amount = total[0][2]
        fos.checkout(order_id, order_status, order_address, checkout_time, estimated_time, bill_amount)
        checkoutDictObj = {
            "order_id": order_id,
            "order_status": order_status,
            "order_address": order_address,
            "estimated_time": estimated_time,
            "bill_amount": bill_amount
        }
        return json.dumps(checkoutDictObj)

    @app.route('/customers/<int:cust_id>/cancel-order', methods=['PUT'])
    def cancel_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1}" "localhost:8080/customers/1/cancel-order"
        """
        order_id = flask.request.json["order_id"]
        order_status = "Cancelled"
        cancel = fos.cancel_order(order_id, order_status)
        found_order = False
        if cancel:
            cancelDictObj = {
                "order_id": order_id,
                "order_status": order_status
            }
            found_order = True
        if found_order:
            return json.dumps(cancelDictObj)
        else:
            print("Order ID {} not found".format(order_id))
            return json.dumps(not_found), 404    

    @app.route('/customers/<int:cust_id>/view-order', methods=['GET'])
    def view_order(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":1}" "localhost:8080/customers/1/view-order"
        """
        order_id = flask.request.json["order_id"]
        view_order_item = fos.view_order(order_id)
        found_result = False
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
            found_result = True
        if found_result:
            return json.dumps(result)
        else:
            print("Order ID {} not found".format(order_id))
            return json.dumps(not_found), 404

    @app.route('/customers/<int:cust_id>/view-order-grand-total', methods=['GET'])
    def view_order_grand_total(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":1}" "localhost:8080/customers/1/view-order-grand-total"
        """
        order_id = flask.request.json["order_id"]
        view_grand_total = fos.view_order_grand_total(order_id)
        for cd, cost, grand_total in view_grand_total:
            grand_totalDictObj = {
                "customer_name": cd.cust_name,
                "order_id": cost.order_id,
                "grand_total": grand_total
                }
            return json.dumps(grand_totalDictObj)
    
    @app.route('/customers/<int:cust_id>/view-order-status', methods=['GET'])
    def view_order_status(cust_id):
        """
        >> curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":1}" "localhost:8080/customers/1/view-order-status"
        """
        order_id = flask.request.json["order_id"]
        view_status = fos.view_order_status(order_id)
        for cd, cosa, dp in view_status:
            statusDictObj = {
                "customer_name": cd.cust_name,
                "order_id": cosa.order_id,
                "delivery_person_name": dp.delivery_person_name,
                "order_status": cosa.order_status,
                "total_bill": cosa.bill_amount
                }
            return json.dumps(statusDictObj)
        print("Order ID {} not found".format(order_id))
        return json.dumps(not_found), 404

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