def handler(request):
    return {
        "statusCode": 200,
        "headers": {"content-type": "text/plain"},
        "body": "Vercel Python function alive"
    }
