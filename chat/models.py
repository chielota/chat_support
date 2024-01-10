import uuid

from django.db import models

class Mymodel(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid_field= models.UUIDField(default=uuid.uuid4, editable=False)