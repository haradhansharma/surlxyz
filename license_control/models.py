from django.db import models

class Licences(models.Model):
    party_domain = models.URLField()
    # key = models.BooleanField(help_text='Do not make it true if want to allow the site and validaty still valid!')
    validaty = models.DateTimeField()

    def __str__(self):
        return self.party_domain
