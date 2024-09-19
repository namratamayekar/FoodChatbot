import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Namrata#24",
    database="pandeyji_eatery"
)


# Function to fetch the order status from the order_tracking table
def get_order_status(order_id: int):
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = "SELECT status FROM order_tracking WHERE order_id = %s"
    cursor.execute(query, (order_id,))

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    return result[0] if result else None



