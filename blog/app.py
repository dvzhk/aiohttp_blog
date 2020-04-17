from aiohttp import web
from .routes import setup_routes
import aiohttp_jinja2
import jinja2
import asyncpgsa
import aiohttp_debugtoolbar
from aiohttp_cache import setup_cache

async def create_app(config: dict):
    app = web.Application()
    if config.get('aiohttp_debugtoolbar'):
        aiohttp_debugtoolbar.setup(app, intercept_redirects=False)

    #Создаем новый ключ для конфига
    app['config'] = config

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
