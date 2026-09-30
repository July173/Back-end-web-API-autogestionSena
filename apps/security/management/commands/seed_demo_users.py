import os
from django.core.management.base import BaseCommand
from apps.security.entity.models.DocumentType import DocumentType
from apps.security.entity.models.Role import Role
from apps.security.entity.models.Person import Person
from apps.security.entity.models.User import User


class Command(BaseCommand):
    help = 'Seeds initial demonstration accounts and roles for portfolio testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Inicializando siembra de datos de prueba para demostración...'))

        # 1. Tipo de documento base
        doc_type, _ = DocumentType.objects.get_or_create(
            acronyms='CC',
            defaults={'name': 'Cédula de Ciudadanía', 'active': True}
        )

        # 2. Roles del sistema
        roles_data = [
            {'id': 1, 'type_role': 'Administrador', 'description': 'Administrador del sistema con acceso completo'},
            {'id': 2, 'type_role': 'Aprendiz', 'description': 'Aprendiz SENA con acceso a novedades y seguimiento'},
            {'id': 3, 'type_role': 'Instructor', 'description': 'Instructor SENA para control de fichas y aprendices'},
            {'id': 4, 'type_role': 'Coordinador', 'description': 'Coordinador académico y de seguimiento'},
            {'id': 5, 'type_role': 'Operador Sofia Plus', 'description': 'Operador para sincronización de datos y Excel'},
        ]

        roles_dict = {}
        for r_info in roles_data:
            role, _ = Role.objects.get_or_create(
                id=r_info['id'],
                defaults={
                    'type_role': r_info['type_role'],
                    'description': r_info['description'],
                    'active': True
                }
            )
            # Asegurar nombre correcto
            if role.type_role != r_info['type_role']:
                role.type_role = r_info['type_role']
                role.save()
            roles_dict[r_info['id']] = role

        # 3. Usuarios de prueba demo
        demo_password = os.getenv('DEMO_DEFAULT_PASSWORD', 'Sena2026*')

        demo_users = [
            {
                'email': 'admin.demo@sena.edu.co',
                'first_name': 'Admin',
                'first_last_name': 'Sistema',
                'identification': 1000000001,
                'phone': 3101111111,
                'role_id': 1,
            },
            {
                'email': 'aprendiz.demo@soy.sena.edu.co',
                'first_name': 'Aprendiz',
                'first_last_name': 'Demostración',
                'identification': 1000000002,
                'phone': 3102222222,
                'role_id': 2,
            },
            {
                'email': 'instructor.demo@sena.edu.co',
                'first_name': 'Instructor',
                'first_last_name': 'Titular',
                'identification': 1000000003,
                'phone': 3103333333,
                'role_id': 3,
            },
            {
                'email': 'coordinador.demo@sena.edu.co',
                'first_name': 'Coordinador',
                'first_last_name': 'Académico',
                'identification': 1000000004,
                'phone': 3104444444,
                'role_id': 4,
            },
            {
                'email': 'sofia.demo@sena.edu.co',
                'first_name': 'Operador',
                'first_last_name': 'Sofia',
                'identification': 1000000005,
                'phone': 3105555555,
                'role_id': 5,
            },
        ]

        for u_data in demo_users:
            person, _ = Person.objects.get_or_create(
                number_identification=u_data['identification'],
                defaults={
                    'type_identification': doc_type,
                    'first_name': u_data['first_name'],
                    'first_last_name': u_data['first_last_name'],
                    'phone_number': u_data['phone'],
                    'active': True
                }
            )

            user, created = User.objects.get_or_create(
                email=u_data['email'],
                defaults={
                    'person': person,
                    'role': roles_dict[u_data['role_id']],
                    'is_active': True,
                    'registered': False,
                }
            )

            # Actualizar datos y resetear contraseña
            user.person = person
            user.role = roles_dict[u_data['role_id']]
            user.is_active = True
            user.registered = False
            user.set_password(demo_password)
            user.save()

            status_text = 'creado' if created else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f"✓ Usuario demo {status_text}: {user.email} (Rol {roles_dict[u_data['role_id']].type_role}) - Clave: {demo_password}"
            ))

        # Opcional: Si existe bscortes40@soy.sena.edu.co, asegurar contraseña Sena2026*
        try:
            brayan_user = User.objects.filter(email='bscortes40@soy.sena.edu.co').first()
            if brayan_user:
                brayan_user.set_password(demo_password)
                brayan_user.is_active = True
                brayan_user.save()
                self.stdout.write(self.style.SUCCESS(f"✓ Usuario personal actualizado: bscortes40@soy.sena.edu.co con clave {demo_password}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Aviso usuario brayan: {e}"))

        self.stdout.write(self.style.SUCCESS('¡Siembra de cuentas demo finalizada exitosamente!'))
