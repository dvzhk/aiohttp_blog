import re
#from . import db, forms,
import aiohttp
from sqlalchemy import select
from aiohttp_jinja2 import template
from . import db

#from .views.shared_views import category_view_delete

def slugify(title):
    pattern = r'[^\w+]'
    slug = re.sub(pattern, '-', title.lower())
    return slug


async def post_view_delete(request, delete_route=None, view_route=None):
    slug = request.match_info['slug']
    async with request.app['db'].acquire() as conn:
        query = select([db.posts]).where(db.posts.c.slug == slug)
        result = await conn.fetch(query)
        current_post_id = result[0].get('id')
        print(result)
        category_query = select([db.categories]).where(db.categories.c.id == result[0].get('category_id'))

        category = await conn.fetch(category_query)
        print(category[0])
    return {'obj': result[0], 'category': category[0], 'delete_route': delete_route, 'view_route': view_route}


async def category_view_delete(request, delete_route=None, view_route=None):
    slug = request.match_info['slug']
    async with request.app['db'].acquire() as conn:
        query = select([db.categories]).where(db.categories.c.slug == slug)
        result = await conn.fetch(query)

        category_id = result[0].get('id')
        related_posts_query = select([db.posts.c.title, db.posts.c.slug])\
            .where(db.categories.c.id == db.posts.c.category_id)
        posts_in_category = await conn.fetch(related_posts_query)

    return {'obj': result[0], 'posts': enumerate(posts_in_category), 'number_of_commas': len(posts_in_category) - 1,\
            'delete_route': delete_route, 'view_route': view_route}

class ObjViewDelete:
    obj = None

    async def get(self, request):
        slug = request.match_info['slug']
        async with request.app['db'].acquire() as conn:
            query = select([self.obj]).where(self.obj.c.slug == slug)
            result = await conn.fetch(query)

            obj_id = result[0].get('id')
            related_obj_query = select([db.posts.c.title, db.posts.c.slug]). \
                where(db.categories.c.id == db.posts.c.category_id)
            posts_with_tag = await conn.fetch(related_obj_query)



class ObjDeleteMixin:
    """Mixin for category, post delete. "obj" might be db.posts or db.categories"""

    obj = None
    redirect_route = 'index'
    delete_route = None
    list_route = None
    GET_template_path = None

    @template(GET_template_path)
    async def get(self):
        await category_view_delete(self.request)

    async def post(self):
        slug = self.request.match_info['slug']
        async with self.request.app['db'].acquire() as conn:
            await conn.execute(self.obj.delete().where(self.obj.c.slug == slug))

        location = self.request.app.router[self.redirect_route].url_for()
        raise aiohttp.web.HTTPFound(location=location)