from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.
class Link(models.Model):
    url = models.URLField()
    description = models.TextField(blank=True)
    # created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    link = models.ForeignKey('graphql_api.Link', related_name='votes', on_delete=models.CASCADE)



class Quark(models.Model):
    name = models.CharField(max_length=255,blank=False)
    # Don't make it URLField: image_path could be relative path like '/img/hoge.png'.
    image_path = models.CharField(max_length=255,blank=True)
    description = models.TextField(blank=True)
    start = models.DateField(null=True,blank=True)
    end = models.DateField(null=True,blank=True)
    start_accuracy = models.CharField(max_length=10,blank=True)
    end_accuracy = models.CharField(max_length=10,blank=True)
    is_momentary = models.BooleanField(default=False,blank=True)
    url = models.URLField(blank=True)
    affiliate = models.URLField(blank=True)
    gender = models.CharField(max_length=3,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    is_exclusive = models.BooleanField(default=True,blank=True)
    wid = models.IntegerField(null=True, blank=True, validators=[MaxValueValidator(99999999)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='posted_quarks', on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='modified_quarks', on_delete=models.CASCADE)
    quark_type_id = models.ForeignKey('graphql_api.QuarkType', related_name='quarks', on_delete=models.CASCADE)

class QuarkType(models.Model):
    name = models.CharField(max_length=255,blank=False)
    # Don't make it URLField: image_path could be relative path like '/img/hoge.png'.
    image_path = models.CharField(max_length=255,blank=True)
    name_prop = models.CharField(max_length=255,blank=False)
    start_prop = models.CharField(max_length=255,blank=False)
    end_prop = models.CharField(max_length=255,blank=False)
    has_gender = models.BooleanField(default=False,blank=True)
    sort = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



