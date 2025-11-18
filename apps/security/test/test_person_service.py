from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.security.services.PersonService import PersonService
import time

class RegisterApprenticeTest(TestCase):
    
    # Test para registro exitoso de aprendiz
    @patch('apps.security.services.PersonService.format_response')
    @patch('apps.general.services.AprendizService.AprendizService')
    @patch('apps.security.emails.SendEmails.enviar_registro_pendiente')
    @patch('apps.security.entity.serializers.person.PersonSerializer')
    @patch('apps.security.services.UserService.UserService')
    @patch('core.utils.Validation.validate_phone_number', return_value=(True, ''))
    @patch('core.utils.Validation.validate_document_number', return_value=(True, ''))
    @patch('core.utils.Validation.is_unique_email', return_value=True)
    @patch('core.utils.Validation.is_soy_sena_email', return_value=True)
    def test_register_apprentice_success(
        self, mock_soy_sena_email, mock_unique_email, mock_validate_doc, mock_validate_phone,
        mock_user_service, mock_person_serializer, mock_enviar_email, mock_aprendiz_service, mock_format_response
    ):
        start = time.time()
        data = {
            'email': 'test@soy.sena.edu.co',
            'number_identification': '123456',
            'phone_number': '3001234567',
            'first_name': 'Juan',
            'first_last_name': 'Pérez'
        }

        # Mock PersonSerializer
        person_instance = MagicMock()
        person_instance.id = 1
        person_instance.first_name = 'Juan'
        person_instance.first_last_name = 'Pérez'
        mock_person_serializer.return_value.is_valid.return_value = True
        mock_person_serializer.return_value.save.return_value = person_instance

        # Mock UserService
        user_instance = MagicMock()
        mock_user_service.return_value.create.return_value = user_instance

        # Mock AprendizService
        aprendiz_instance = MagicMock()
        mock_aprendiz_service.return_value.create.return_value = aprendiz_instance

        # Mock format_response para simular respuesta exitosa
        mock_format_response.return_value = {
            'success': True,
            'status_code': 201,
            'type': 'register_apprentice',
            'message': 'Usuario registrado correctamente. Tu cuenta está pendiente de activación por un administrador.'
        }

        service = PersonService()
        response = service.register_apprentice(data)

        self.assertTrue(response['success'])
        self.assertEqual(response['status_code'], 201)
        self.assertEqual(response['type'], 'register_apprentice')
        self.assertIn('Usuario registrado correctamente', response['message'])
        end = time.time()
        print(f"Tiempo de ejecución test_register_apprentice_success: {end - start:.4f} segundos")

    # Test para registro con email inválido
    @patch('apps.security.services.PersonService.format_response')
    @patch('core.utils.Validation.is_soy_sena_email', return_value=False)
    def test_register_apprentice_invalid_email(self, mock_soy_sena_email, mock_format_response):
        start = time.time()
        data = {
            'email': 'test@gmail.com',
            'number_identification': '123456',
            'phone_number': '3001234567',
            'first_name': 'Juan',
            'first_last_name': 'Pérez'
        }
        # Mock format_response para simular respuesta de email inválido
        mock_format_response.return_value = {
            'success': False,
            'status_code': 400,
            'type': 'invalid_email',
            'message': 'Solo se permiten correos institucionales (@soy.sena.edu.co)'
        }
        
        service = PersonService()
        response = service.register_apprentice(data)
        
        self.assertFalse(response['success'])
        self.assertEqual(response['status_code'], 400)
        self.assertEqual(response['type'], 'invalid_email')
        self.assertIn('Solo se permiten correos institucionales', response['message'])
        end = time.time()
        print(f"Tiempo de ejecución test_register_apprentice_invalid_email: {end - start:.4f} segundos")




# Se ejecuta el test con 

# para todos los tests de este archivo
# python manage.py test apps.security.test.test_person_service.RegisterApprenticeTest

# para un test específico
# python manage.py test apps.security.test.test_person_service.RegisterApprenticeTest.test_register_apprentice_success
# python manage.py test apps.security.test.test_person_service.RegisterApprenticeTest.test_register_apprentice_invalid_email