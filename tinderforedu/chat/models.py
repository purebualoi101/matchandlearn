from django.db import models

class Savechat(models.Model):
    name = models.TextField(max_length=200, blank=True)
    chat = models.TextField(max_length=200000000000000, blank=True)