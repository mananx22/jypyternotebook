from flask import Flask,request,render_template,redirect,url_for,jsonify

app = Flask(__name__)

items = [
    {"id": 1,"name":"Item 1","description":"this is the first element"},
     {"id": 2,"name":"Item 2","description":"this is the second element"}
]

@app.route("/")
def home():
    return "welcome to home"

@app.route("/get_items", methods=["GET"])
def get_items():
    return jsonify(items)

# GET
@app.route('/items/<int:item_id>', methods=["GET"])
def get_item(item_id):
    item_fetch = next((item for item in items if item['id'] == item_id), None)
    if item_fetch is None:
        return jsonify({"error": "failed to fetch item"})
    return jsonify(item_fetch)

# POST - add a new item
@app.route("/items", methods=["POST"])
def create_item():
    if not request.json or not 'name' in request.json:
        return jsonify({"error": "item not found"})
    new_item = {
        "id": items[-1]['id'] + 1 if items else 1,
        "name": request.json['name'],
        "description": request.json['description']
    }
    items.append(new_item)
    return jsonify(new_item)

# PUT - update an existing item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if not request.json or not 'name' in request.json:
        return jsonify({"error": "item not found"})
    item['name'] = request.json.get('name', item['name'])
    item['description'] = request.json.get('description', item['description'])
    return jsonify(item)

# Delete - delete an existing item [logic- Keep all items except the one with this id”]
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete(item_id):
    items = (( item for item in items if item['id'] != item_id) , None)
    return jsonify({"success":"Item deleted"})



if __name__=="__main__":    
    app.run(debug=True)