from wtforms_alchemy import ModelForm
from wtforms.fields import SelectField
from wtforms.validators import InputRequired
from .db import PostObj, CategoryObj



class CategoryForm(ModelForm):
    class Meta:
        model = CategoryObj
        only = ['category']


class PostForm(ModelForm):
    class Meta:
        model = PostObj
        exclude = ['slug']
    category = SelectField('Category', [InputRequired()], coerce=int)









