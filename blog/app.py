import aiohttp_jinja2
import jinja2
import asyncpgsa
import base64
from aiohttp import web
from aiohttp_cache import setup_cache
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from cryptography import fernet
from .routes import setup_routes
from . auth import DictionaryAuthorizationPolicy
from . users import users


async def create_app(config: dict):
    app = web.Application()

    if config.get('aiohttp_debugtoolbar'):
        import aiohttp_debugtoolbar
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    #Создаем новый ключ для конфига
    app['config'] = config

    auth_setup(app)
    setup_routes(app)
    setup_cache(app)

    #Добавляем действия выполняемые при запуске и остановке приложения
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)

    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('blog', 'templates'))

    return app


async def on_start(app):
    """Запуск при старте - соединение с БД"""
    config = app['config']
    #
    app['db'] = await asyncpgsa.create_pool(dsn=config['database_uri'])


async def on_shutdown(app):
    await app['db'].close()
    print("closed.")


def auth_setup(app):
    app['users'] = users
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    storage = EncryptedCookieStorage(secret_key, cookie_name='API_SESSION')
    setup_session(app, storage)

    policy = SessionIdentityPolicy()
    setup_security(app, policy, DictionaryAuthorizationPolicy(users))
