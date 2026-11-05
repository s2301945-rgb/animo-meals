"""Bound write request bodies before FastAPI parses JSON."""
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

MAX_BODY_BYTES = 16 * 1024


class RequestBodyLimit:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if (scope['type'] != 'http' or not scope['path'].startswith('/api/')
                or scope['method'] not in ('POST', 'PUT')):
            await self.app(scope, receive, send)
            return

        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            if len(body) + len(chunk) > MAX_BODY_BYTES:
                response = JSONResponse({'detail': 'Request is too large. Shorten your input and try again.'},
                                        status_code=413)
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get('more_body', False):
                break

        async def replay():
            nonlocal body
            if body is None:
                return await receive()
            message = {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            body = None
            return message

        await self.app(scope, replay, send)
