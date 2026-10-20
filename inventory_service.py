from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample inventory data. A database is not needed for this assignment.
inventory = {
    "keyboard": 10,
    "mouse": 25,
    "monitor": 3,
}


@app.get("/health")
def health():
    return jsonify(service="inventory", status="running")


@app.post("/inventory/check")
def check_inventory():
    data = request.get_json() or {}
    item_id = data.get("item_id")
    quantity = data.get("quantity")

    if not item_id or not isinstance(quantity, int) or quantity <= 0:
        return jsonify(error="item_id and a positive quantity are required"), 400

    available_quantity = inventory.get(item_id, 0)
    available = available_quantity >= quantity

    return jsonify(
        item_id=item_id,
        requested_quantity=quantity,
        available_quantity=available_quantity,
        available=available,
    )


if __name__ == "__main__":
    app.run(port=5001)
