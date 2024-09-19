from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

# GET request handler
@app.get("/")
async def get_root():
    return {"message": "GET request is working"}

# POST request handler
@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        #'order.remove - context: ongoing-order': remove_from_order,
        #'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }
    return intent_handler_dict[intent](parameters, session_id)

def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def track_order(parameters: dict):
    print("Parameters in track_order:", parameters)  

    order_id_key = 'number'  
    if order_id_key in parameters:
        try:
            order_id = int(parameters[order_id_key][0])
            print("Order ID extracted and converted to int:", order_id)
            order_status = db_helper.get_order_status(order_id)

            if order_status:
                fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
            else:
                fulfillment_text = f"No order found with order id: {order_id}"
        except(IndexError, ValueError) as e:
            fulfillment_text = "Invalid order ID format or empty list."
    else:        
        fulfillment_text = "Order ID not provided in the request."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })