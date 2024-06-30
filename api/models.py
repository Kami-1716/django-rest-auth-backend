from django.db import models

# Create your models here.

# user model with auth0Id and email

class Auth0User(models.Model):
    auth0Id = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email