from django.db import models

class Boss(models.Model):
    
    class Metta:
        db_table = 'boss'
    
    enterprise = models.OneToOneField('assign.Enterprise', on_delete=models.CASCADE, related_name='boss')
    name_boss = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email_boss = models.EmailField(max_length=100)
    position = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    delete_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name_boss
