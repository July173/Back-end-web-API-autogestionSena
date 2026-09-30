"""
Unit tests for the modular demonstration data seeder.
"""
from django.test import TestCase
from django.core.management import call_command
from apps.security.entity.models import Role, User, Module, Form, RoleFormPermission
from apps.general.entity.models import Regional, Center, Sede, Program, Ficha, Apprentice, Instructor
from apps.assign.entity.models import Enterprise, ModalityProductiveStage, RequestAsignation, AsignationInstructor, VisitFollowing


class SeedDemoUsersTests(TestCase):
    def test_seed_demo_users_populates_all_domains_completely(self):
        # Ejecutar el comando orquestador de siembra
        call_command('seed_demo_users')

        # 1. Validar Dominio de Seguridad
        self.assertEqual(Role.objects.count(), 5)
        self.assertGreaterEqual(Module.objects.count(), 3)
        self.assertGreaterEqual(Form.objects.count(), 9)
        self.assertGreaterEqual(RoleFormPermission.objects.count(), 30)
        self.assertTrue(User.objects.filter(email='admin.demo@sena.edu.co').exists())
        self.assertTrue(User.objects.filter(email='aprendiz.demo@soy.sena.edu.co').exists())

        # 2. Validar Dominio General SENA
        self.assertGreaterEqual(Regional.objects.count(), 3)
        self.assertGreaterEqual(Center.objects.count(), 2)
        self.assertGreaterEqual(Sede.objects.count(), 2)
        self.assertGreaterEqual(Program.objects.count(), 3)
        self.assertGreaterEqual(Ficha.objects.count(), 4)
        self.assertGreaterEqual(Instructor.objects.count(), 2)
        self.assertGreaterEqual(Apprentice.objects.count(), 5)

        # 3. Validar Dominio de Asignación y Seguimiento
        self.assertGreaterEqual(ModalityProductiveStage.objects.count(), 4)
        self.assertGreaterEqual(Enterprise.objects.count(), 3)
        self.assertGreaterEqual(RequestAsignation.objects.count(), 4)
        self.assertGreaterEqual(AsignationInstructor.objects.count(), 2)
        self.assertGreaterEqual(VisitFollowing.objects.count(), 4)
