from django.db import models
from django.contrib.auth.models import User
import os

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='author')


    # author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='author')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='catergory')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tags')

    def __str__(self):
        return f'[{self.title}] :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'


