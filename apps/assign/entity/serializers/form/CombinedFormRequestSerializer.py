from rest_framework import serializers


class EmpresaSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    nombre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nit = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    direccion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    correo = serializers.EmailField(required=False, allow_null=True)
    telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class JefeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    nombre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    correo = serializers.EmailField(required=False, allow_null=True)
    telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cargo = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class TalentoHumanoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    nombre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    correo = serializers.EmailField(required=False, allow_null=True)
    telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SolicitudSerializer(serializers.Serializer):
    # Recomendado: incluir apprentice y ficha si la solicitud es de aprendiz
    apprentice = serializers.IntegerField(required=False, allow_null=True)
    ficha = serializers.IntegerField(required=False, allow_null=True)
    descripcion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_inicio_contrato = serializers.DateField(required=False, allow_null=True)
    fecha_fin_contrato = serializers.DateField(required=False, allow_null=True)
    sede = serializers.IntegerField(required=False, allow_null=True)
    modality_productive_stage = serializers.IntegerField(required=False, allow_null=True)


class CombinedFormRequestSerializer(serializers.Serializer):
    empresa = EmpresaSerializer()
    jefe = JefeSerializer()
    talentoHumano = TalentoHumanoSerializer()
    solicitud = SolicitudSerializer()
