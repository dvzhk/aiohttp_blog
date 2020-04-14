import aiohttp.web
from aiohttp_jinja2 import template
# Импортируем модель
from .. import db, forms, utils

from sqlalchemy import select, insert
#from .shared_views import post_view_update, tag_view_delete
#from ..db import PostObj



@template('index.html')
async def index(request):
    #site_name = request.app['config'].get('site_name')
    async with request.app['db'].acquire() as conn:
        query = select([db.posts.c.title, db.posts.c.body, db.posts.c.slug, db.posts.c.date_pub])
        result = await conn.fetch(query)
    localsv = locals()
    globalsv = globals()
    return {'post_list': result, 'localsv': localsv, 'globalsv': globalsv}


@template('post_view.html')
def post_view(request):
    return utils.post_view_delete(request)

class PostCreate(aiohttp.web.View):
    async def get_choices(self):
        async with self.request.app['db'].acquire() as conn:
            query = select([db.categories.c.id, db.categories.c.category])
            categories = await conn.fetch(query)

        return categories

    @template('post_create.html')
    async def get(self):
        new_post_form = forms.PostForm()
        new_post_form.category.choices = await self.get_choices()
        return {'form': new_post_form}

    @template('post_create.html')
    async def post(self):
        data = await self.request.post()
        new_post_created_form = forms.PostForm(data)
        new_post_created_form.category.choices = await self.get_choices()

        if new_post_created_form.validate():
            title, body, category_id = data['title'], data['body'], int(data['category'])
            new_post_obj = db.PostObj(title, body, category_id)
            async with self.request.app['db'].acquire() as conn:
                await conn.execute(db.posts.insert().values(title=new_post_obj.title, body=new_post_obj.body,\
                                                            slug=new_post_obj.slug, date_pub=new_post_obj.date_pub,\
                                                            category_id=category_id))
            location = self.request.app.router['index'].url_for()
            raise aiohttp.web.HTTPFound(location=location)
        return {'form': new_post_created_form}


class CategoryCreate(aiohttp.web.View):
    @template('category_create.html')
    async def get(self):
        new_category = forms.CategoryForm()
        return {'form': new_category}

    @template('category_create.html')
    async def post(self):
        data = await self.request.post()
        new_category_created_form = forms.CategoryForm(data)
        if new_category_created_form:
            category = data['category']
            new_category_obj = db.CategoryObj(category)
            async with self.request.app['db'].acquire() as conn:
                await conn.execute(db.categories.insert().values(category=new_category_obj.category,
                                                                 slug=new_category_obj.slug))
            location = self.request.app.router['category_list'].url_for()
            raise aiohttp.web.HTTPFound(location=location)
        return {'form': new_category_created_form}

@template('category_list.html')
async def categories_list_view(request):
    async with request.app['db'].acquire() as conn:
        query = select([db.categories.c.category, db.categories.c.slug])
        result = await conn.fetch(query)

    return {'category_list': result}

@template('category_view.html')
async def category_view(request):
    return await utils.category_view_delete(request)
    """slug = request.match_info['slug']
    async with request.app['db'].acquire() as conn:
        query = select([db.tag]).where(db.tag.c.slug == slug)
        result = await conn.fetch(query)

        tag_id = result[0].get('id')
        related_posts_query = select([db.post.c.title, db.post.c.slug]).\
            where(db.post.c.id.in_(select([db.post_tags.c.post_id]).where(db.post_tags.c.tag_id == tag_id)))
        posts_with_tag = await conn.fetch(related_posts_query)

        print(posts_with_tag)

    return {'post': result[0], 'posts': enumerate(posts_with_tag), 'number_of_commas': len(posts_with_tag)-1}
"""
async def obj_list(request, table):

    slug = request.match_info['slug']
    async with request.app['db'].acquire() as conn:
        query = select([table]).where(table.c.slug == slug)
        result = await conn.fetch(query)

    return {'post': result[0]}


class PostUpdate(aiohttp.web.View):
    @template('post_update.html')
    async def get(self):
        slug = self.request.match_info['slug']
        async with self.request.app['db'].acquire() as conn:
            query = select([db.posts]).where(db.posts.c.slug == slug)
            result = await conn.fetch(query)


            current_post_id = result[0].get('id')
            category_list_query = select([db.categories]).where(db.categories.c.id == db.posts.c.category_id)

            category_list_for_post = await conn.fetch(category_list_query)
        print(dir(result[0]))
        print(result[0].values())
        form = [1]
        form = forms.PostForm(obj=result[0], data=result[0])
        #form.tags.render_kw['class'] = 'form-group'
        #form.tags =
        #print("---=", form.tags.entries)
        print("P---=", form.title.data)
        print()
        print(dir(form))
        print()
        #print(dir(form.tags))
        #form = 1     obj=result[0]
        #print(form.id)
        print()
        print(category_list_for_post[0].keys())

        return {'obj': result[0], 'slug':slug, 'category_list_for_post': enumerate(category_list_for_post), \
                'number_of_commas': len(category_list_for_post) - 1, \
                'form': form}

    @template('post_update.html')
    async def post(self):
        data = await self.request.post()
        slug = self.request.match_info.get('slug')
        form = forms.PostForm(data)
        if form.validate():
            title, body = data['title'], data['body']
            post_obj = db.PostObj(title, body)
            async with self.request.app['db'].acquire() as conn:
                await conn.execute(db.posts.update().where(db.posts.c.slug == slug).values(title=post_obj.title,\
                                                                                         body=post_obj.body))
            location = self.request.app.router['read_post'].url_for(slug=slug)
            raise aiohttp.web.HTTPFound(location=location)
        return {'form': form}



class PostDelete(utils.ObjDeleteMixin, aiohttp.web.View):
    obj = db.posts
    redirect_route = 'index'
    delete_route = 'delete_post'
    view_route = 'read_post'
    GET_template_path = 'post_view.html'
    print(113)
    @template('post_delete.html')
    async def get(self):
        return await utils.post_view_delete(self.request, self.delete_route, self.view_route)



class CategoryUpdate(aiohttp.web.View):
    obj = db.categories
    redirect_route = 'category_list'


    def get(self):
        return utils.category_view_delete(self.request)




class CategoryDelete(utils.ObjDeleteMixin, aiohttp.web.View):
    obj = db.categories
    redirect_route = 'category_list'
    delete_route = 'delete_category'
    view_route = 'category_view'
    GET_template_path = 'category_delete.html'


    @template('category_delete.html')
    async def get(self):
        return await utils.category_view_delete(self.request, self.delete_route, self.view_route)



