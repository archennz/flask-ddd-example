import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from model import Base

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    # TODO: fix the config
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
    
    db = SQLAlchemy(model_class=Base)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    db.init_app(app)
    
    from model import OrderLine

    with app.app_context():
        db.create_all()
    # these are the routes
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route("/allocate", methods=["POST"])
    def allocate_endpoint():
        pass

    @app.route("/test", methods=["GET"])
    def test_get():
        ol = OrderLine(orderid = "id-1", sku = "sku-1", qty=5)
        db.session.add(ol)
        db.session.commit()
        return 'Ok'

    @app.route("/orderline/<id>", methods=["GET"])
    def test_get_2(id):
        ol = db.session.get(OrderLine, id)
        return ol.orderid
    return app
