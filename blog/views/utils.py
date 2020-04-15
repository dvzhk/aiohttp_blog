import aiohttp
from sqlalchemy import select
from aiohttp_jinja2 import template, render_template
from .. import db, forms
from datetime import datetime

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


class PostViewDeleteGETMixin:
    delete_route = None
    view_route = None
    html_template = ""

    async def get(self):
        slug = self.request.match_info['slug']
        async with self.request.app['db'].acquire() as conn:
            query = select([db.posts]).where(db.posts.c.slug == slug)
            result = await conn.fetch(query)
            current_post_id = result[0].get('id')
            print(result)
            category_query = select([db.categories]).where(db.categories.c.id == result[0].get('category_id'))
            category = await conn.fetch(category_query)
            print(category[0])

            context = {'obj': result[0], 'category': category[0], 'delete_route': self.delete_route,
                       'view_route': self.view_route}
            response = render_template(self.html_template, self.request, context)
            return response


class PostCreateUpdateMixin:
    action_create = False
    html_template = "404.html"
    redirect_to = 'index'
    slug = None

    async def get_choices(self):
        async with self.request.app['db'].acquire() as conn:
            query = select([db.categories.c.id, db.categories.c.category])
            categories = await conn.fetch(query)
        return categories

    async def post(self):
        data = await self.request.post()
        slug = self.request.match_info.get('slug')
        form = forms.PostForm(data)
        form.category.choices = await self.get_choices()

        if form.validate():
            title, body, category_id = data['title'], data['body'], int(data['category'])
            post_obj = db.PostObj(title, body, category_id)

            async with self.request.app['db'].acquire() as conn:
                if self.action_create:
                    await conn.execute(db.posts.insert().values(title=post_obj.title, body=post_obj.body,\
                                                                slug=post_obj.slug, date_pub=post_obj.date_pub,\
                                                                category_id=category_id))
                    location = self.request.app.router[self.redirect_to].url_for()
                else:
                    await conn.execute(db.posts.update().\
                                   where(db.posts.c.slug == slug).values(title=post_obj.title, body=post_obj.body,\
                                                                         category_id=post_obj.category_id))
                    location = self.request.app.router[self.redirect_to].url_for(slug=slug)

            raise aiohttp.web.HTTPFound(location=location)

        context = {'form': form}
        response = render_template(self.html_template, self.request, context)
        #response.headers['Content-Language'] = 'ru'
        return response

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
    html_template = None

    async def post(self):
        slug = self.request.match_info['slug']
        async with self.request.app['db'].acquire() as conn:
            await conn.execute(self.obj.delete().where(self.obj.c.slug == slug))

        location = self.request.app.router[self.redirect_route].url_for()
        raise aiohttp.web.HTTPFound(location=location)


class CategoryCreateUpdateMixin:
    action_update = False
    html_template = 'category_create_update.html'
    redirect_to = 'category_list'

    async def get(self):
        form_submit_url = self.request.url
        category = None
        category_record = None
        slug = None

        if self.action_update:
            slug = self.request.match_info['slug']
            async with self.request.app['db'].acquire() as conn:
                query = select([db.categories.c.id, db.categories.c.category]).where(db.categories.c.slug == slug)
                category_records = await conn.fetch(query)

            category_record = category_records[0]
            category = category_record.get('category')

        form = forms.CategoryForm(obj=category_record, data=category_record)
        context = {'slug': slug, 'form': form, 'category': category, 'form_submit_url': form_submit_url}
        response = render_template(self.html_template, self.request, context)
        return response

    async def post(self):
        data = await self.request.post()
        category_form = forms.CategoryForm(data)

        if category_form:
            category = data['category']
            category_obj = db.CategoryObj(category)
            async with self.request.app['db'].acquire() as conn:
                if self.action_update:
                    slug = self.request.match_info['slug']
                    await conn.execute(db.categories.update().where(db.categories.c.slug == slug).values(
                        category=category_obj.category))
                    location = self.request.app.router[self.redirect_to].url_for(slug=slug)
                else:
                    await conn.execute(db.categories.insert().values(category=category_obj.category,
                                                                     slug=category_obj.slug))
                    location = self.request.app.router[self.redirect_to].url_for()
            raise aiohttp.web.HTTPFound(location=location)
        context = {'form': category_form}
        response = render_template(self.html_template, self.request, context)
        return response


class CategoryViewDeleteMixinGETMixin:
    delete_route = None
    view_route = None
    html_template = ''

    async def get(self):
        slug = self.request.match_info['slug']
        async with self.request.app['db'].acquire() as conn:
            query = select([db.categories]).where(db.categories.c.slug == slug)
            result = await conn.fetch(query)
            category_id = result[0].get('id')
            related_posts_query = select([db.posts.c.title, db.posts.c.slug])\
                .where(db.categories.c.id == db.posts.c.category_id)
            posts_in_category = await conn.fetch(related_posts_query)

        context = {'obj': result[0], 'posts': enumerate(posts_in_category), 'number_of_commas': len(posts_in_category) - 1, \
                'delete_route': self.delete_route, 'view_route': self.view_route}
        response = render_template(self.html_template, self.request, context)
        return response