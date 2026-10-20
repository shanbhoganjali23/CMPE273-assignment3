from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

inventory_url = "http://127.0.0.1:5001/inventory/check"
orders = []
next_order_id = 1


@app.get("/health")
def health():
    return jsonify(service="order", status="running")


@app.post("/orders")
def create_order():
    global next_order_id

    data = request.get_json() or {}
    item_id = data.get("item_id")
    quantity = data.get("quantity")

    if not item_id or not isinstance(quantity, int) or quantity <= 0:
        return jsonify(error="item_id and a positive quantity are required"), 400

    try:
        inventory_response = requests.post(
            inventory_url,
            json={"item_id": item_id, "quantity": quantity},
            timeout=2,
        )
        inventory_response.raise_for_status()
    except requests.RequestException:
        return jsonify(error="Inventory Service is unavailable"), 503

    inventory_result = inventory_response.json()
    if not inventory_result["available"]:
        return jsonify(error="Item is unavailable"), 409

    order = {
        "order_id": next_order_id,
        "item_id": item_id,
        "quantity": quantity,
        "status": "created",
    }
    orders.append(order)
    next_order_id += 1

    # This represents publishing an OrderCreated event for Notification Service.
    print("OrderCreated event:", order)

    return jsonify(order), 201


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    for order in orders:
        if order["order_id"] == order_id:
            return jsonify(order)
    return jsonify(error="Order not found"), 404


if __name__ == "__main__":
    app.run(port=5000)
