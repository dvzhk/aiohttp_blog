import aiohttp.web
from aiohttp_jinja2 import template, render_template
from sqlalchemy import select, insert, or_
# Импортируем модель
from .. import db, forms
from . import utils
from datetime import datetime

@template('index.html')
async def index(request):
    #site_name = request.app['config'].get('site_name')
    async with request.app['db'].acquire() as conn:
        query = select([db.posts.c.title, db.posts.c.body, db.posts.c.slug, db.posts.c.date_pub])
        result = await conn.fetch(query)
    return {'post_list': result}


@template('category_list.html')
async def categories_list_view(request):
    async with request.app['db'].acquire() as conn:
        query = select([db.categories.c.category, db.categories.c.slug])
        result = await conn.fetch(query)
    return {'category_list': result}


class PostView(utils.PostViewDeleteGETMixin, aiohttp.web.View):
    html_template = "post_view.html"


class PostDelete(utils.PostViewDeleteGETMixin, utils.ObjDeleteMixin, aiohttp.web.View):
    obj = db.posts
    redirect_route = 'index'
    delete_route = 'delete_post'
    view_route = 'read_post'
    html_template = 'post_delete.html'


class PostCreate(utils.PostCreateUpdateMixin, aiohttp.web.View):
    action_create = True
    html_template = "post_create.html"
    redirect_to = 'index'

    @template(html_template)
    async def get(self):
        new_post_form = forms.PostForm()
        new_post_form.category.choices = await self.get_choices()
        return {'form': new_post_form}


class PostUpdate(utils.PostCreateUpdateMixin, aiohttp.web.View):
    action_create = False
    html_template = "post_update.html"
    redirect_to = "read_post"
    slug = None

    async def get_post_and_category(self):
        async with self.request.app['db'].acquire() as conn:
            query = select([db.posts]).where(db.posts.c.slug == self.slug)
            post = await conn.fetch(query)

            category_query = select([db.categories]).where(db.categories.c.id == post[0].get('category_id'))
            category = await conn.fetch(category_query)
        return post, category

    @template(html_template)
    async def get(self):
        self.slug = self.request.match_info['slug']
        post, category = await self.get_post_and_category()

        form = forms.PostForm(obj=post[0], data=post[0])
        form.category.choices = await self.get_choices()
        form.category.data = post[0].get('category_id')
        return {'obj': post[0], 'slug': self.slug, 'category': category, 'form': form}


class CategoryCreate(utils.CategoryCreateUpdateMixin, aiohttp.web.View):
    action_update = False
    redirect_to = 'category_list'


class CategoryUpdate(utils.CategoryCreateUpdateMixin, aiohttp.web.View):
    action_update = True
    redirect_to = 'category_view'


class CategoryView(utils.CategoryViewDeleteMixinGETMixin, aiohttp.web.View):
    html_template = 'category_view.html'


class CategoryDelete(utils.CategoryViewDeleteMixinGETMixin, utils.ObjDeleteMixin, aiohttp.web.View):
    obj = db.categories
    redirect_route = 'category_list'
    delete_route = 'delete_category'
    view_route = 'category_view'
    html_template = 'category_delete.html'


@template('index.html')
async def search(request):
    text_for_search = request.query.get('text')
    start = datetime.now()
    async with request.app['db'].acquire() as conn:
        query = select([db.posts]).where(or_(db.posts.c.body.contains(text_for_search),
                                             db.posts.c.title.contains(text_for_search)
                                             )
                                         )
        #print(query.compile())
        result = await conn.fetch(query)
    #print(datetime.now() - start)
    #print(f'Found: {len(result)} records.')
    return {'post_list': result}