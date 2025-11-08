from django.db import models

class RequestState(models.TextChoices):
    ASIGNADO = 'ASIGNADO', 'Asignado'
    SIN_ASIGNAR = 'SIN_ASIGNAR', 'Sin Asignar'
    RECHAZADO = 'RECHAZADO', 'Rechazado'