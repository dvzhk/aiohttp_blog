from sqlalchemy import (
    Table, Text, VARCHAR, MetaData, Column, Integer, DateTime, ForeignKey)
from sqlalchemy.orm import mapper, relationship
import datetime
import re
from .utils import slugify
meta = MetaData()

posts = Table(
    'posts', meta,
    Column('id', Integer, primary_key=True),
    Column('title', VARCHAR(255), index=True, nullable=False),
    Column('body', Text, index=True, nullable=False),
    Column('date_pub', DateTime, nullable=False, index=True, default=datetime.datetime.now()),
    Column('slug', VARCHAR(255), nullable=False),
    Column('category_id', Integer, ForeignKey('categories.id'), nullable=True)
)


categories = Table(
    'categories', meta,
    Column('id', Integer, primary_key=True),
    Column('category', VARCHAR(30), nullable=False, index=True, unique=True),
    Column('slug', VARCHAR(30), nullable=False, index=True, unique=True)
)


class PostObj(object):
    def __init__(self, title, body, category_id):
        self.id = id
        self.title = title
        self.body = body
        self.category_id = category_id
        self.date_pub = datetime.datetime.now()
        if self.title:
            self.slug = self.gen_slug()

    def gen_slug(self):
        timestamp = datetime.datetime.timestamp(datetime.datetime.now())
        return slugify(self.title) + "_" + str(int(timestamp))

    def __repr__(self):
        return f"<PostObj({self.id}, {self.title}, {self.body[:15]})>"


class CategoryObj(object):
    def __init__(self, category):
        self.category = category
        self.slug = slugify(self.category)

    def __repr__(self):
        return f"<CategoryObj({self.category}, {self.slug})>"


category_mapper = mapper(CategoryObj, categories)
post_mapper = mapper(PostObj, posts)
