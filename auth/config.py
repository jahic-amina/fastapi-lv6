import os
import uuid
from dotenv import load_dotenv

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from auth.users import User, get_user_manager

load_dotenv()

SECRET = os.getenv("SECRET_KEY", "fallback-dev-secret")

# BearerTransport — token se šalje u Authorization headeru kao "Bearer <token>"
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) * 60,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Dependency injection helperi — koriste se u routerima
current_active_user = fastapi_users.current_user(active=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)