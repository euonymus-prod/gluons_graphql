from django.conf import settings
import uuid
from django.db import models
from django.core.validators import MaxValueValidator

# gluons models
class Quark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True,max_length=255,blank=False)
    # Don't make it URLField: image_path could be relative path like '/img/hoge.png'.
    image_path = models.CharField(max_length=255,blank=True)
    description = models.TextField(blank=True)
    start = models.DateField(null=True,blank=True)
    end = models.DateField(null=True,blank=True)
    start_accuracy = models.CharField(max_length=10,blank=True)
    end_accuracy = models.CharField(max_length=10,blank=True)
    is_momentary = models.BooleanField(default=False,blank=True)
    url = models.URLField(max_length=255,blank=True)
    affiliate = models.URLField(max_length=255,blank=True)
    gender = models.CharField(max_length=3,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    is_exclusive = models.BooleanField(default=True,blank=True)
    wid = models.IntegerField(null=True, blank=True, validators=[MaxValueValidator(99999999)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='posted_quarks', on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='modified_quarks', on_delete=models.CASCADE)
    quark_type = models.ForeignKey('graphql_api.QuarkType', related_name='quarks', on_delete=models.CASCADE)


class Gluon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relation = models.CharField(max_length=255,blank=False)
    prefix = models.CharField(max_length=255,blank=True)
    suffix = models.CharField(max_length=255,blank=True)
    start = models.DateField(null=True,blank=True)
    end = models.DateField(null=True,blank=True)
    start_accuracy = models.CharField(max_length=10,blank=True)
    end_accuracy = models.CharField(max_length=10,blank=True)
    is_momentary = models.BooleanField(default=False,blank=True)
    url = models.URLField(max_length=255,blank=True)
    is_private = models.BooleanField(default=False,blank=True)
    is_exclusive = models.BooleanField(default=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='posted_gluons', on_delete=models.CASCADE)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='modified_gluons', on_delete=models.CASCADE)
    gluon_type = models.ForeignKey('graphql_api.GluonType', null=True, related_name='gluons', on_delete=models.CASCADE)
    subject_quark = models.ForeignKey('graphql_api.Quark', related_name='havings', on_delete=models.CASCADE)
    object_quark = models.ForeignKey('graphql_api.Quark', related_name='belongings', on_delete=models.CASCADE)


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

class GluonType(models.Model):
    name = models.CharField(max_length=255,blank=False)
    caption = models.CharField(max_length=255,blank=False)
    caption_ja = models.CharField(max_length=255,blank=False)
    sort = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class QuarkProperty(models.Model):
    name = models.CharField(max_length=255,blank=False)
    caption = models.CharField(max_length=255,blank=False)
    caption_ja = models.CharField(max_length=255,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class QtypeProperty(models.Model):
    is_required = models.BooleanField(default=False,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quark_type = models.ForeignKey('graphql_api.QuarkType', related_name='having_quark_properties', on_delete=models.CASCADE)
    quark_property = models.ForeignKey('graphql_api.QuarkProperty', related_name='belonging_quark_types', on_delete=models.CASCADE)

class QpropertyType(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quark_property = models.ForeignKey('graphql_api.QuarkProperty', related_name='having_quark_types', on_delete=models.CASCADE)
    quark_type = models.ForeignKey('graphql_api.QuarkType', related_name='belonging_quark_properties', on_delete=models.CASCADE)

class QpropertyGtype(models.Model):
    side = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quark_property = models.ForeignKey('graphql_api.QuarkProperty', related_name='having_gluon_types', on_delete=models.CASCADE)
    gluon_type = models.ForeignKey('graphql_api.GluonType', related_name='belonging_quark_properties', on_delete=models.CASCADE)




