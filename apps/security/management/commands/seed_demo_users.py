"""
Master management command to seed demonstration data for Autogestión SENA.
Orchestrates domain-specific seeders (Security, General SENA, Assign) atomically.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.security.management.commands.helpers.security_seeder import seed_security_domain
from apps.security.management.commands.helpers.general_seeder import seed_general_domain
from apps.security.management.commands.helpers.assign_seeder import seed_assign_domain


class Command(BaseCommand):
    help = 'Seeds initial demonstration accounts, permissions, institutional SENA hierarchy and requests'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=== INICIANDO SIEMBRA INTEGRAL DE DATOS DEMO AUTOGESTIÓN SENA ==='))

        try:
            with transaction.atomic():
                # 1. Seguridad, permisos y cuentas demo
                roles_dict, doc_cc = seed_security_domain(self.stdout, self.style)

                # 2. Regionales, Centros, Sedes, Programas, Fichas, Instructores y Aprendices
                instructor_1, instructor_2, apprentices = seed_general_domain(self.stdout, self.style, doc_cc)

                # 3. Modalidades, Empresas, Solicitudes y Visitas de Seguimiento
                seed_assign_domain(self.stdout, self.style, instructor_1, instructor_2, apprentices)

            self.stdout.write(self.style.SUCCESS('\n[OK] Siembra integral finalizada con exito! Todos los modulos estan activos.'))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] Error durante la siembra de datos: {str(exc)}'))
            raise exc
