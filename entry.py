import aiohttp
from blog import create_app
import asyncio
import argparse
from blog.settings import load_config

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("Using uvloop.")
except ImportError:
    print('No uvloop avaible.')

parser = argparse.ArgumentParser(description="blog")
parser.add_argument('--host', help='host', default='0.0.0.0')
parser.add_argument('--port', help='port', default=8080)
parser.add_argument('--reload', action='store_true', help='Autoreload config')

parser.add_argument('--config', type=argparse.FileType('r'), help='Path to config file')

args = parser.parse_args()

app = create_app(config=load_config(args.config))

if args.reload:
    print('Start with config reload')
    import aioreloader
    aioreloader.start()

if __name__ == '__main__':

    aiohttp.web.run_app(app, host=args.host, port=args.port)

