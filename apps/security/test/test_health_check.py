"""
Unit tests for Health Check & Keep-Alive endpoints.
"""
from django.test import TestCase, Client
from django.urls import reverse


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_root_endpoint_returns_200(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('service', data)
        self.assertIn('database', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['service'], 'Autogestion SENA API')

    def test_health_api_endpoint_returns_200(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data['status'], ['healthy', 'degraded'])
        self.assertEqual(data['version'], '1.0.0')
