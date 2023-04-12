from django.db import models


class action_log(models.Model):
    owner = models.CharField(max_length=255, primary_key=True)
    status = models.CharField(max_length=255)
    action_code = models.CharField(max_length=255)
    action_detail = models.CharField(max_length=255)
    