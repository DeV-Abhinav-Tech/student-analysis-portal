import os
import sys

# Ensure root directory is in sys.path so app, database, attendance_agent can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app, index

class VercelRewriteMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        original_path = (
            environ.get('HTTP_X_MATCHED_PATH')
            or environ.get('HTTP_X_FORWARDED_PATH')
            or environ.get('HTTP_X_NOW_ROUTE_MATCHES')
        )
        if original_path:
            environ['SCRIPT_NAME'] = ''
            environ['PATH_INFO'] = original_path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelRewriteMiddleware(app.wsgi_app)

@app.route("/api/index")
def vercel_api_index_fallback():
    return index()
