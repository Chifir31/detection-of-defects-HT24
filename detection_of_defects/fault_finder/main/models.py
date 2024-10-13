from PIL import Image, ImageDraw
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class Photo(models.Model):
  objects = None
  id = models.IntegerField(primary_key=True)
  image = models.ImageField(upload_to='photos/')
  predict = models.CharField(max_length=20)
  x1 = models.IntegerField()
  y1 = models.IntegerField()
  x2 = models.IntegerField()
  y2 = models.IntegerField()


class Report(models.Model):
  objects = None
  serial_number = models.CharField(max_length=150)
  count_defects = models.IntegerField()
  count_photos = models.IntegerField()
  
  resume = models.CharField(max_length=30)
  dead_pixels = models.IntegerField()
  scratches = models.IntegerField()
  lock = models.IntegerField()
  chip = models.IntegerField()
  missing_screw = models.IntegerField()
  keyboard_defect = models.IntegerField()
  
