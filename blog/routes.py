from .views import frontend

def setup_routes(app):
    """Setup routes for app."""

    app.router.add_route('GET', '/', frontend.index, name='index')
    app.router.add_route('GET', '/post/{slug}', frontend.post_view, name='read_post')

    app.router.add_view('/create', frontend.PostCreate, name='create_post')
    app.router.add_view('/post/{slug}/update', frontend.PostUpdate, name='post_update')
    app.router.add_view('/post/{slug}/delete', frontend.PostDelete, name='delete_post')

    app.router.add_route('GET', '/categories/', frontend.categories_list_view, name='category_list')
    app.router.add_route('GET', '/categories/{slug}', frontend.category_view, name='category_view')

    app.router.add_view('/category/create', frontend.CategoryCreate, name='create_category')
    app.router.add_view('/categories/{slug}/update', frontend.CategoryUpdate, name='category_update')
    app.router.add_view('/categories/{slug}/delete', frontend.CategoryDelete, name='delete_category')


