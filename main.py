from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper

app = FastAPI()

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

    if intent == "track.order - context: ongoing-tracking":
        return track_order(parameters)
    else:
        return JSONResponse(content={"fulfillmentText": "Intent not recognized."})


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