from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.datastructures import Headers
from app import create_app

# Create the Flask app once at cold-start
flask_app = create_app()

def handler(request):
    """
    Vercel Python function handler that forwards the incoming request to the
    Flask WSGI application and returns a dict compatible with Vercel's expected
    response shape.

    This uses Werkzeug's EnvironBuilder to construct a WSGI environment from
    the incoming `request` object, then uses Response.from_app to run the
    Flask app and capture the response.
    """
    # Extract common pieces from the Vercel request object. The `request`
    # object provided by Vercel's runtime behaves similarly to Flask's
    # Request: it exposes method, headers, path, args, and get_data(). We
    # defensively extract attributes so this works in the Vercel runtime.
    try:
        method = request.method
        path = request.path
        query_string = request.query_string if hasattr(request, 'query_string') else ''
        headers = Headers(request.headers) if hasattr(request, 'headers') else Headers()
        data = request.get_data() if hasattr(request, 'get_data') else (request.body if hasattr(request, 'body') else None)
    except Exception:
        # Fallback for unexpected request shapes
        method = 'GET'
        path = '/'
        query_string = ''
        headers = Headers()
        data = None

    builder = EnvironBuilder(path=path, method=method, headers=headers, data=data, query_string=query_string)
    env = builder.get_environ()

    # Run the Flask app against the WSGI environment
    response = Response.from_app(flask_app, env)

    # Prepare a Vercel-compatible response dict
    result = {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }
    return result
