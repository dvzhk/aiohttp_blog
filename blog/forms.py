from wtforms_alchemy import ModelForm, ModelFieldList, QuerySelectField
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
from wtforms.fields import FormField, FieldList, SelectField, SelectMultipleField
from .db import PostObj, CategoryObj
from wtforms.validators import InputRequired
class CsrfAdd:
    csrf = True
    csrf_class = SessionCSRF
    csrf_secret = b'YorKeyHereEPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
    csrf_time_limit = timedelta(minutes=20)


class CategoryForm(ModelForm):
    class Meta:
        model = CategoryObj
        only = ['category']


class PostForm(ModelForm):
    class Meta:
        model = PostObj
        exclude = ['slug']
    category = SelectField('Category', [InputRequired()], coerce=int)









