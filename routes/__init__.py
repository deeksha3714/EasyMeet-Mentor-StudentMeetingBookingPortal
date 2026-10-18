"""Route modules. Each module exposes init_app(app) which registers its URLs.

Endpoint names are kept identical to the original single-file app
(e.g. "login", "mentor_dashboard"), so url_for(...) in templates still works.
"""
from . import auth, mentor, booking, waitlist


def register_routes(app):
    auth.init_app(app)
    mentor.init_app(app)
    booking.init_app(app)
    waitlist.init_app(app)
  
