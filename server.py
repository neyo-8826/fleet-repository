"""Main server entrypoint"""
import falcon
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend
from falcon_cors import CORS

from auth import user_loader
from config import (
    CORS_ALLOWED_HEADERS,
    CORS_ALLOWED_METHODS,
    CORS_ALLOWED_ORIGINS
)
from resources import PayoutTimerResource


# Auth
auth_backend = BasicAuthBackend(user_loader)
auth_middleware = FalconAuthMiddleware(auth_backend)
# CORS
cors = CORS(allow_origins_list=CORS_ALLOWED_ORIGINS,
            allow_methods_list=CORS_ALLOWED_METHODS,
            allow_headers_list=CORS_ALLOWED_HEADERS)

app = falcon.API(middleware=[auth_middleware, cors.middleware])

payout = PayoutTimerResource()

app.add_route('/payouts', payout)
