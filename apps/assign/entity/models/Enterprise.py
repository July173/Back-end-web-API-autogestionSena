from django.db import models


class Enterprise(models.Model):
    class Meta:
        db_table = 'enterprise'

    boss = models.OneToOneField('assign.Boss', on_delete=models.CASCADE, related_name='enterprise')
    name_enterprise = models.CharField(max_length=100)
    locate = models.CharField(max_length=255)
    nit_enterprise = models.CharField(max_length=20)
    email_enterprise = models.EmailField(max_length=100)
    active = models.BooleanField(default=True)
    delete_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name_enterprise
