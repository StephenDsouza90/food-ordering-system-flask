# Test cases

## Running server:

```
Connecting to sqlite:///fos2.db
Serving on http://StephenDsouza:8080
```

## Test negative cases

-1. Allow a non-existent customer 'Nobody' to view the order status with non-existent order_id, should return 404

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":5}" "localhost:8080/customers/5/view-order-status"

{"message": "Not Found"}
```

-2. Cancel an order that doesn't exist, should return 404

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":6}" "localhost:8080/customers/2/cancel-order"

{"message": "Not Found"}
```

-3. View customer 'Jude' order with non-existent order_id, should return 404

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":7}" "localhost:8080/customers/1/view-order"

{"message": "Not Found"}
```

-4. View customer 'Jude' order "status" with non-existent order_id, should return 404

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":9}" "localhost:8080/customers/1/view-order-status"

{"message": "Not Found"}
```

-5. View the sales today, should be 0

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/view-sales-today"

[]
```

-6. View the revenue today, should be 0

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/sum-revenue-today"

{"today_revenue": null}
```

## Test Administration:

1. Add 3 food categories, dessert, main-dish, apetizers

```
curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"dessert\"}" "localhost:8080/employees/add-food-category"

{"category_id": 1, "category_name": "dessert"}

curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"main-dish\"}" "localhost:8080/employees/add-food-category"

{"category_id": 2, "category_name": "main-dish"}

curl -H "Content-Type: application/json" -X POST -d "{\"name\":\"apetizers\"}" "localhost:8080/employees/add-food-category"

{"category_id": 3, "category_name": "apetizers"}
```

2. Add 9 food details, 3 for each category:

- 'Biryani' and 'Mutton Karhai' for main-dish

```
curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":2, \"food_name\":\"Biryani\", \"price\":10}" "localhost:8080/employees/add-food-details"

{"category_id": 2, "food_id": 1, "food_name": "Biryani", "food_price": 10}

curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":2, \"food_name\":\"Mutton Karhai\", \"price\":10}" "localhost:8080/employees/add-food-details"

{"category_id": 2, "food_id": 2, "food_name": "Mutton Karhai", "food_price": 10}
```

- 'Seekh kebab' and 'Samosas' for apetizers

```
curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":3, \"food_name\":\"Seekh Kebab\", \"price\":5}" "localhost:8080/employees/add-food-details"

{"category_id": 3, "food_id": 3, "food_name": "Seekh Kebab", "food_price": 5}

curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":3, \"food_name\":\"Samosas\", \"price\":5}" "localhost:8080/employees/add-food-details"

{"category_id": 3, "food_id": 4, "food_name": "Samosas", "food_price": 5}
```

- 'Caramel custard' and 'chocolate ice-cream' for dessert

```
curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":1, \"food_name\":\"Caramel custard\", \"price\":7}" "localhost:8080/employees/add-food-details"

{"category_id": 1, "food_id": 5, "food_name": "Caramel custard", "food_price": 7}

curl -H "Content-Type: application/json" -X POST -d "{\"category_id\":1, \"food_name\":\"Chocolate ice-cream\", \"price\":7}" "localhost:8080/employees/add-food-details"

{"category_id": 1, "food_id": 6, "food_name": "Chocolate ice-cream", "food_price": 7}
```

3. Add 2 delivery persons 'Uber-Eats', 'Foodora'

```
curl -H "Content-Type: application/json" -X POST -d "{\"delivery_person_name\":\"Uber-Eats\", \"delivery_person_phone\":111}" "localhost:8080/employees/add-delivery-person"

{"delivery_person_id": 1, "delivery_person_name": "Uber-Eats", "delivery_person_phone": 111}

curl -H "Content-Type: application/json" -X POST -d "{\"delivery_person_name\":\"Foodora\", \"delivery_person_phone\":222}" "localhost:8080/employees/add-delivery-person"

{"delivery_person_id": 2, "delivery_person_name": "Foodora", "delivery_person_phone": 222}
```

## Test Signup, Login, Creating Orders and checking out

4. Sign up 3 customers 'Jude', 'Vincent', 'Stephen'

```
curl -H "Content-Type: application/json" -X POST -d "{\"cust_name\":\"Jude\", \"cust_phone\":999, \"cust_email\":\"jude@hotmail.com\"}" "localhost:8080/customers/signup"

{"customer_email": "jude@hotmail.com", "customer_id": 1, "customer_name": "Jude"}

curl -H "Content-Type: application/json" -X POST -d "{\"cust_name\":\"Vincent\", \"cust_phone\":888, \"cust_email\":\"vincent@hotmail.com\"}" "localhost:8080/customers/signup"

{"customer_email": "vincent@hotmail.com", "customer_id": 2, "customer_name": "Vincent"}

curl -H "Content-Type: application/json" -X POST -d "{\"cust_name\":\"Stephen\", \"cust_phone\":777, \"cust_email\":\"stephen@hotmail.com\"}" "localhost:8080/customers/signup"

{"customer_email": "stephen@hotmail.com", "customer_id": 3, "customer_name": "Stephen"}
```

5. Allow customer 'Jude' to login and view the menu

```
curl -X GET "localhost:8080/customers/1/login"

{"cust_id": 1, "cust_name": "Jude"}

curl localhost:8080/customers/view-menu

[
    {"category_id": 2, "category_name": "main-dish", "food_id": 1, "food_name": "Biryani", "price": 10}, 
    {"category_id": 2, "category_name": "main-dish", "food_id": 2, "food_name": "Mutton Karhai", "price": 10}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 3, "food_name": "Seekh Kebab", "price": 5}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 4, "food_name": "Samosas", "price": 5}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 5, "food_name": "Caramel custard", "price": 7}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 6, "food_name": "Chocolate ice-cream", "price": 7}
    ]
```

6. Allow customer 'Jude' to create an order

- customer 'Jude' Adds 1x'Biryani', 1x'Mutton Karhai', 1x'Seekh kebab', 1x'chocolate ice-cream' and 1x'Caramel custard' to the order

```
curl -H "Content-Type: application/json" -X POST -d "{\"cust_id\":1}" "localhost:8080/customers/1/create-order"

{"customer_id": 1, "order_id": 1}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":1, \"food_id\":1, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 1, "food_qty": 1, "order_id": 1}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":1, \"food_id\":2, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 2, "food_qty": 1, "order_id": 1}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":1, \"food_id\":3, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 3, "food_qty": 1, "order_id": 1}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":1, \"food_id\":6, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 6, "food_qty": 1, "order_id": 1}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":1, \"food_id\":5, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 5, "food_qty": 1, "order_id": 1}
```

- customer 'Jude' Removes 'Caramel custard' from the order

```
curl -H "Content-Type: application/json" -XDELETE -d "{\"order_id\":1, \"food_id\":5}" "localhost:8080/customers/1/remove-food-to-order"

{"food_id": 5, "order_id": 1}
```

- customer 'Jude' updates the food order and adds food quantity of 2 for 'Biryani'.

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"food_id\":1, \"food_qty\":2}" "localhost:8080/customers/1/update-food-to-order"

{"food_id": 1, "food_qty": 2, "order_id": 1}
```

7. Allow customer 'Jude' to do a checkout.

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"order_address\":\"Karachi\"}" "localhost:8080/customers/1/checkout"

{
    "bill_amount": 42, 
    "estimated_time": "Mon, 25 Nov 2019 19:53:38 GMT", 
    "order_address": "Karachi", 
    "order_id": 1, 
    "order_status": "Checkedout"
    }
```

8. Allow customer 'Stephen' to login and view the menu

```
curl -X GET "localhost:8080/customers/3/login"

{"cust_id": 3, "cust_name": "Stephen"}

curl localhost:8080/customers/view-menu

[
    {"category_id": 2, "category_name": "main-dish", "food_id": 1, "food_name": "Biryani", "price": 10}, 
    {"category_id": 2, "category_name": "main-dish", "food_id": 2, "food_name": "Mutton Karhai", "price": 10}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 3, "food_name": "Seekh Kebab", "price": 5}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 4, "food_name": "Samosas", "price": 5}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 5, "food_name": "Caramel custard", "price": 7}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 6, "food_name": "Chocolate ice-cream", "price": 7}
    ]
```

9. Allow customer 'Stephen' to create an order

- customer 'Stephen' Adds 2x'Mutton Karhai', 5x'Seekh kebab', 1x'chocolate ice-cream' and 1x'Caramel custard' to the order

```
curl -H "Content-Type: application/json" -X POST -d "{\"cust_id\":3}" "localhost:8080/customers/3/create-order"

{"customer_id": 3, "order_id": 2}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":2, \"food_id\":2, \"food_qty\":2}" "localhost:8080/customers/3/add-food-to-order"

{"food_id": 2, "food_qty": 2, "order_id": 2}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":2, \"food_id\":3, \"food_qty\":5}" "localhost:8080/customers/3/add-food-to-order"

{"food_id": 3, "food_qty": 5, "order_id": 2}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":2, \"food_id\":6, \"food_qty\":1}" "localhost:8080/customers/3/add-food-to-order"

{"food_id": 6, "food_qty": 1, "order_id": 2}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":2, \"food_id\":5, \"food_qty\":1}" "localhost:8080/customers/3/add-food-to-order"

{"food_id": 5, "food_qty": 1, "order_id": 2}
```

- customer 'Stephen' updates the food order and updates food quantity of 1 for 'Mutton Karhai'.

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":2, \"food_id\":2, \"food_qty\":1}" "localhost:8080/customers/3/update-food-to-order"

{"food_id": 2, "food_qty": 1, "order_id": 2}
```

10. Allow customer 'Stephen' to do a checkout.

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":2, \"order_address\":\"Karachi\"}" "localhost:8080/customers/3/checkout"

{
    "bill_amount": 49, 
    "estimated_time": "Mon, 25 Nov 2019 20:09:11 GMT", 
    "order_address": "Karachi", 
    "order_id": 2, 
    "order_status": "Checkedout"
    }
```

11. Allow customer 'Vincent' to login and view the menu

```
curl -X GET "localhost:8080/customers/2/login"

{"cust_id": 2, "cust_name": "Vincent"}

curl localhost:8080/customers/view-menu

[
    {"category_id": 2, "category_name": "main-dish", "food_id": 1, "food_name": "Biryani", "price": 10}, 
    {"category_id": 2, "category_name": "main-dish", "food_id": 2, "food_name": "Mutton Karhai", "price": 10}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 3, "food_name": "Seekh Kebab", "price": 5}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 4, "food_name": "Samosas", "price": 5}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 5, "food_name": "Caramel custard", "price": 7}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 6, "food_name": "Chocolate ice-cream", "price": 7}
    ]
```

12. Allow customer 'Vincent' to create an order

- customer 'Vincent' Adds 1x'Mutton Karhai', 2x'Seekh kebab', 2x'chocolate ice-cream' to the order

```
curl -H "Content-Type: application/json" -X POST -d "{\"cust_id\":2}" "localhost:8080/customers/2/create-order"

{"customer_id": 2, "order_id": 3}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":3, \"food_id\":2, \"food_qty\":1}" "localhost:8080/customers/2/add-food-to-order"

{"food_id": 2, "food_qty": 1, "order_id": 3}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":3, \"food_id\":3, \"food_qty\":2}" "localhost:8080/customers/2/add-food-to-order"

{"food_id": 3, "food_qty": 2, "order_id": 3}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":3, \"food_id\":6, \"food_qty\":2}" "localhost:8080/customers/2/add-food-to-order"

{"food_id": 6, "food_qty": 2, "order_id": 3}
```

- customer 'Vincent' Adds 1x'Biryani' to the food order.

```
curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":3, \"food_id\":1, \"food_qty\":1}" "localhost:8080/customers/2/add-food-to-order"

{"food_id": 1, "food_qty": 1, "order_id": 3}
```

13. Allow customer 'Vincent' to do a checkout.

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":3, \"order_address\":\"Karachi\"}" "localhost:8080/customers/2/checkout"

{
    "bill_amount": 44, 
    "estimated_time": "Mon, 25 Nov 2019 20:17:50 GMT", 
    "order_address": "Karachi", 
    "order_id": 3, 
    "order_status": "Checkedout"
    }
```

## Test assigning order to delivery person

14. Assign Delivery person 'Uber-Eats' to 'Jude' order

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":1, \"delivery_person_id\":1}" "localhost:8080/employees/assign-deliver-person-to-deliver-order"

{"delivery_person_id": 1, "order_id": 1}
```

15. Assign Delivery person 'Uber-Eats' to 'Stephen' order

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":2, \"delivery_person_id\":1}" "localhost:8080/employees/assign-deliver-person-to-deliver-order"

{"delivery_person_id": 1, "order_id": 2}
```

16. Assign Delivery person 'Foodora' to 'Vincent' order

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":3, \"delivery_person_id\":2}" "localhost:8080/employees/assign-deliver-person-to-deliver-order"

{"delivery_person_id": 2, "order_id": 3}
```

## Test the sales and revenue today

17. View the sales today # Test if sales today is correct

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/view-sales-today"

[
    {"bill_amount": 42, "customer_name": "Jude", "date_time": "2019-11-25 19:23:38.827091", "order_id": 1, "order_status": "Checkedout"}, 
    {"bill_amount": 49, "customer_name": "Stephen", "date_time": "2019-11-25 19:39:11.292984", "order_id": 2, "order_status": "Checkedout"}, 
    {"bill_amount": 44, "customer_name": "Vincent", "date_time": "2019-11-25 19:47:50.134687", "order_id": 3, "order_status": "Checkedout"}
    ]
```

18. View the revenue today # Test if revenue is correct

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/sum-revenue-today"

{"today_revenue": 135}
```

## Test customer Order status

19. Allow customer 'Vincent' to view his order

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":3}" "localhost:8080/customers/2/view-order"

[
    {"food_category": "main-dish", "food_name": "Biryani", "food_price": 10, "food_quantity": 1, "total_per_item": 10}, 
    {"food_category": "main-dish", "food_name": "Mutton Karhai", "food_price": 10, "food_quantity": 1, "total_per_item": 10}, 
    {"food_category": "apetizers", "food_name": "Seekh Kebab", "food_price": 5, "food_quantity": 2, "total_per_item": 10}, 
    {"food_category": "dessert", "food_name": "Chocolate ice-cream", "food_price": 7, "food_quantity": 2, "total_per_item": 14}
    ]
```

20. Allow customer 'Vincent' to view the grand total

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":3}" "localhost:8080/customers/2/view-order-grand-total"

{"customer_name": "Vincent", "grand_total": 44, "order_id": 3}
```

21. Allow customer 'Vincent' to view the order status

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":3}" "localhost:8080/customers/2/view-order-status"

{"customer_name": "Vincent", "delivery_person_name": "Foodora", "order_id": 3, "order_status": "Checkedout", "total_bill": 44}
```

## Test sales and revenue today after customer makes another order

22. Allow customer 'Jude' to login and view the menu again

```
curl -X GET "localhost:8080/customers/1/login"

{"cust_id": 1, "cust_name": "Jude"}

curl localhost:8080/customers/view-menu

[
    {"category_id": 2, "category_name": "main-dish", "food_id": 1, "food_name": "Biryani", "price": 10}, 
    {"category_id": 2, "category_name": "main-dish", "food_id": 2, "food_name": "Mutton Karhai", "price": 10}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 3, "food_name": "Seekh Kebab", "price": 5}, 
    {"category_id": 3, "category_name": "apetizers", "food_id": 4, "food_name": "Samosas", "price": 5}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 5, "food_name": "Caramel custard", "price": 7}, 
    {"category_id": 1, "category_name": "dessert", "food_id": 6, "food_name": "Chocolate ice-cream", "price": 7}
    ]
```

23. Allow customer 'Jude' to create another order

- customer 'Jude' Adds 2x'Mutton Karhai', 2x'Samosas', 1x'Seekh kebab', 1x'chocolate ice-cream' to the order

```
curl -H "Content-Type: application/json" -X POST -d "{\"cust_id\":1}" "localhost:8080/customers/1/create-order"

{"customer_id": 1, "order_id": 4}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":4, \"food_id\":2, \"food_qty\":2}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 2, "food_qty": 2, "order_id": 4}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":4, \"food_id\":4, \"food_qty\":2}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 4, "food_qty": 2, "order_id": 4}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":4, \"food_id\":3, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 3, "food_qty": 1, "order_id": 4}

curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":4, \"food_id\":6, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 6, "food_qty": 1, "order_id": 4}
```

- customer 'Jude' Adds 1x'Biryani the food order.

```
curl -H "Content-Type: application/json" -X POST -d "{\"order_id\":4, \"food_id\":1, \"food_qty\":1}" "localhost:8080/customers/1/add-food-to-order"

{"food_id": 1, "food_qty": 1, "order_id": 4}
```

24. Allow customer 'Jude' to do a checkout.

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":4, \"order_address\":\"Karachi\"}" "localhost:8080/customers/1/checkout"

{
    "bill_amount": 52, 
    "estimated_time": "Mon, 25 Nov 2019 20:44:05 GMT", 
    "order_address": "Karachi", 
    "order_id": 4, 
    "order_status": "Checkedout"
    }
```

25. View the sales today # Test if sales today is correct

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/view-sales-today"

[
    {"bill_amount": 42, "customer_name": "Jude", "date_time": "2019-11-25 19:23:38.827091", "order_id": 1, "order_status": "Checkedout"}, 
    {"bill_amount": 49, "customer_name": "Stephen", "date_time": "2019-11-25 19:39:11.292984", "order_id": 2, "order_status": "Checkedout"}, 
    {"bill_amount": 44, "customer_name": "Vincent", "date_time": "2019-11-25 19:47:50.134687", "order_id": 3, "order_status": "Checkedout"}, 
    {"bill_amount": 52, "customer_name": "Jude", "date_time": "2019-11-25 20:14:05.222478", "order_id": 4, "order_status": "Checkedout"}
    ]
```

26. View the revenue today # Test if revenue is correct

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/sum-revenue-today"

{"today_revenue": 187}
```

## Test sales and revenue today after customer cancels an order

27. Allow customer 'Vincent' to cancel the order

```
curl -H "Content-Type: application/json" -X PUT -d "{\"order_id\":3}" "localhost:8080/customers/2/cancel-order"

{"order_id": 3, "order_status": "Cancelled"}
```

28. Allow customer 'Vincent' to view the order status

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_id\":3}" "localhost:8080/customers/2/view-order-status"

{"customer_name": "Vincent", "delivery_person_name": "Foodora", "order_id": 3, "order_status": "Cancelled", "total_bill": 44}
```

29. View the sales today # Test if sales today is correct

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/view-sales-today"

[
    {"bill_amount": 42, "customer_name": "Jude", "date_time": "2019-11-25 19:23:38.827091", "order_id": 1, "order_status": "Checkedout"}, 
    {"bill_amount": 49, "customer_name": "Stephen", "date_time": "2019-11-25 19:39:11.292984", "order_id": 2, "order_status": "Checkedout"}, 
    {"bill_amount": 52, "customer_name": "Jude", "date_time": "2019-11-25 20:14:05.222478", "order_id": 4, "order_status": "Checkedout"}
    ]
```

30. View the revenue today # Test if revenue is correct

```
curl -H "Content-Type: application/json" -X GET -d "{\"order_status\":\"'Checkedout'\"}" "localhost:8080/employees/sum-revenue-today"

{"today_revenue": 143}
```