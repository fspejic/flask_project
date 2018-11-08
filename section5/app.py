from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity
# JWT - JSON Web Token

app = Flask(__name__)
app.secret_key = 'jose'
api = Api(app)

# resource is something that api creates or reqeusts
# every resource must be class

# JWT object creates new endpoint, /auth
# when JWT token is sent, it calls identitiy method
jwt = JWT(app, authenticate, identity)

items = []

class Item(Resource):

    parser = reqparse.RequestParser() # parse request that only looks price in request body, not anythin else if there is
    parser.add_argument('price', type=float, required=True,
                        help='This field caanot be left blank!')

    @jwt_required()
    def get(self, name):
        # for item in items:
        #     if item['name'] == name:
        #         return item

        # The next() returns the next item from the iterator
        # If there isn't anything to return, we must set default value, in this case is None
        # In this case we are sure that there is only one matching item so we dont use list() here, but next()
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': 'An item with name "{}" alreay exists'.format(name)}, 400

        data = Item.parser.parse_args()


        item = {'name': name, 'price': data}
        items.append(item)

        return item, 201 if item else 404

    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        item = next(filter(lambda x: x['name'] == name, items), None)
         
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
        else:
            item.update(data)

        return item


class ItemList(Resource):
    def get(self):
        return {'items': items}

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
app.run(port=5000, debug=True)
