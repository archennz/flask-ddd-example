import os

from flask import Flask
from flaskr.db import db_session

import orm
from model import OrderLine, Batch

def create_app(test_config=None):
    orm.start_mappers()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route("/allocate", methods=["POST"])
    def allocate_endpoint():
        pass

    @app.route("/test", methods=["GET"])
    def test_get():
        ol = OrderLine("id-1", "sku-1", 5)
        db_session.add(ol)
        return 'Ok'

    @app.route("/test-2", methods=["GET"])
    def test_get_2():
        ol = db_session.get(OrderLine, "id-1")
        return ol.orderid

    # @app.route("/allocate", methods=["POST"])
    # def allocate_endpoint():
    #     batches = db_session.get(Batch, "some-id")
    #     line = model.OrderLine(
    #         request.json["orderid"],
    #         request.json["sku"],
    #         request.json["qty"],
    #     )

    #     batchref = model.allocate(line, batches)
    #     return model.allocate(line, batches)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
