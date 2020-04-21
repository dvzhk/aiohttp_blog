import aiohttp.web
from aiohttp_jinja2 import template
from sqlalchemy import select, func, or_, join, text
from aiohttp_cache import cache
from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)
from .. import db, forms
from . import utils
from .. import auth
from .. import users

#@cache()
@template('index.html')
async def index(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        query = select([db.posts.c.title, db.posts.c.body, db.posts.c.slug, db.posts.c.date_pub])
        result = await conn.fetch(query)
    return {'post_list': result, 'logged': username}


#@cache()
@template('category_list.html')
async def categories_list_view(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        # SELECT category, count(posts.id) AS "post_count" FROM categories
        # LEFT OUTER JOIN posts ON posts.category_id=categories.id GROUP BY category ORDER BY post_count DESC;
        posts_cat_join = join(db.categories, db.posts,  db.posts.c.category_id == db.categories.c.id, isouter=True)
        query = select([db.categories.c.category, db.categories.c.slug, func.count(db.posts.c.id).label('post_count')])\
            .select_from(posts_cat_join).group_by(db.categories.c.category, db.categories.c.slug)\
            .order_by(text('post_count DESC'))
        result = await conn.fetch(query)
    return {'category_list': result, 'logged': username}


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

    @cache()
    @template(html_template)
    async def get(self):
        username = await authorized_userid(self.request)
        if username:
            new_post_form = forms.PostForm()
            new_post_form.category.choices = await self.get_choices()
            return {'form': new_post_form, 'logged': username}
        else:
            response = aiohttp.web.HTTPForbidden
            raise response


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
        username = await authorized_userid(self.request)
        if username:
            self.slug = self.request.match_info['slug']
            post, category = await self.get_post_and_category()

            form = forms.PostForm(obj=post[0], data=post[0])
            form.category.choices = await self.get_choices()
            form.category.data = post[0].get('category_id')
            return {'obj': post[0], 'slug': self.slug, 'category': category, 'form': form, 'logged': username}
        else:
            raise aiohttp.web.HTTPForbidden


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
    username = await authorized_userid(request)
    text_for_search = request.query.get('text')
    async with request.app['db'].acquire() as conn:
        query = select([db.posts]).where(or_(db.posts.c.body.contains(text_for_search),
                                             db.posts.c.title.contains(text_for_search)
                                             )
                                         )
        #print(query.compile())
        result = await conn.fetch(query)
    return {'post_list': result, 'logged': username}


@template('login_template.html')
async def login(request):
    username = await authorized_userid(request)
    if request.method == 'POST':
        data = await request.post()
        user = data.get('username')
        password = data.get('password')
        if await auth.check_credentials(users.users, user, password):
            location = request.app.router['index'].url_for()
            response = aiohttp.web.HTTPFound(location=location)
            await remember(request, response, user)
            raise response
        return {'errors': "Wrong username or password.", 'username': user, 'logged': username}
    else:
        return {'logged': username}


@template('logout_template.html')
async def logout(request):
    username = await authorized_userid(request)
    if request.method == 'POST' and username:
        location = request.app.router['index'].url_for()
        response = aiohttp.web.HTTPFound(location=location)
        await forget(request, response)
        raise response
    return {'logged': username}
