from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as user_router
from app.api.profile_routes import router as profile_router
from app.api.contacts_routes import router as contacts_router
from app.api.chat_routes import router as chat_router
from app.api.updates_routes import router as updates_router
from app.api.device_routes import router as device_router
from app.core.config import settings
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version='0.1.0')

allowed_origins = [o.strip() for o in str(settings.FRONTEND_ORIGINS or '').split(',') if o.strip()]
if not allowed_origins:
    allowed_origins = ['http://127.0.0.1:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type'],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(contacts_router)
app.include_router(chat_router)
app.include_router(updates_router)
app.include_router(device_router)


@app.middleware('http')
async def security_headers(request: Request, call_next):
    proto = request.headers.get('x-forwarded-proto', request.url.scheme)
    if settings.FORCE_HTTPS and proto == 'http':
        https_url = str(request.url).replace('http://', 'https://', 1)
        return RedirectResponse(url=https_url, status_code=307)

    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


@app.get('/')
def health():
    return {'status': 'ok', 'service': settings.APP_NAME}
