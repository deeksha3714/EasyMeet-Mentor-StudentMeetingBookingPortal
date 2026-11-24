"""Application entry point: create the app, load config, register routes."""
from flask import Flask

from config import AGING_SECONDS, SECRET_KEY
from db_config import get_db_connection
from routes import register_routes
from services.waitlist_service import get_policy
from utils import query_all

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.context_processor
def inject_policy():
    return dict(policy=get_policy(), aging_seconds=AGING_SECONDS)


register_routes(app)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
