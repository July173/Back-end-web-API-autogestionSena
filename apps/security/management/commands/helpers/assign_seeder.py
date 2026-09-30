"""
Modular seeder for Assign Domain:
Modalities, Enterprises, Bosses, HumanTalent, Requests, Instructor Assignments, and Follow-up Visits.
"""
import datetime
from apps.assign.entity.models.Enterprise import Enterprise
from apps.assign.entity.models.Boss import Boss
from apps.assign.entity.models.HumanTalent import HumanTalent
from apps.assign.entity.models.ModalityProductiveStage import ModalityProductiveStage
from apps.assign.entity.models.RequestAsignation import RequestAsignation
from apps.assign.entity.models.AsignationInstructor import AsignationInstructor
from apps.assign.entity.models.VisitFollowing import VisitFollowing
from apps.assign.entity.enums.request_state_enum import RequestState


def seed_assign_domain(stdout, style, instructor_1, instructor_2, apprentices):
    stdout.write(style.NOTICE('  [3/3] Sembrando Dominio de Asignación y Seguimiento...'))

    # 1. Modalidades de Etapa Productiva
    mod_contrato, _ = ModalityProductiveStage.objects.get_or_create(
        name_modality='Contrato de Aprendizaje',
        defaults={'description': 'Práctica formativa mediante vinculación con empresa patrocinadora'}
    )
    mod_vinculo, _ = ModalityProductiveStage.objects.get_or_create(
        name_modality='Vínculo Laboral',
        defaults={'description': 'El aprendiz desempeña funciones relacionadas con su programa en su trabajo'}
    )
    mod_pasantia, _ = ModalityProductiveStage.objects.get_or_create(
        name_modality='Pasantía / Práctica',
        defaults={'description': 'Convenio institucional para actividades prácticas'}
    )
    mod_proyecto, _ = ModalityProductiveStage.objects.get_or_create(
        name_modality='Proyecto Productivo',
        defaults={'description': 'Desarrollo de solución tecnológica o empresarial avalada por el SENA'}
    )

    # 2. Empresas
    ent_nefrouros, _ = Enterprise.objects.get_or_create(
        nit_enterprise='900123456-1',
        defaults={'name_enterprise': 'Nefrouros S.A.S. - Sede Neiva', 'locate': 'Carrera 16 No. 5-30, Neiva, Huila', 'email_enterprise': 'talento@nefrouros.com'}
    )
    ent_tech, _ = Enterprise.objects.get_or_create(
        nit_enterprise='901234567-2',
        defaults={'name_enterprise': 'TechSolutions Colombia S.A.S.', 'locate': 'Calle 8 No. 12-40, Neiva, Huila', 'email_enterprise': 'contacto@techsolutions.com.co'}
    )
    ent_banco, _ = Enterprise.objects.get_or_create(
        nit_enterprise='890903938-8',
        defaults={'name_enterprise': 'Bancolombia S.A.', 'locate': 'Carrera 5 No. 10-25, Neiva Centro', 'email_enterprise': 'sena.practicas@bancolombia.com'}
    )

    # 3. Jefes Inmediatos y Talento Humano
    boss_1, _ = Boss.objects.get_or_create(
        enterprise=ent_nefrouros,
        name_boss='Ing. Mauricio Perdomo',
        defaults={'phone_number': 3154445566, 'email_boss': 'mperdomo@nefrouros.com', 'position': 'Líder de Sistemas e Infraestructura'}
    )
    boss_2, _ = Boss.objects.get_or_create(
        enterprise=ent_tech,
        name_boss='Ing. Katherine Dussán',
        defaults={'phone_number': 3165556677, 'email_boss': 'kdussan@techsolutions.com.co', 'position': 'Tech Lead & Scrum Master'}
    )

    HumanTalent.objects.get_or_create(
        enterprise=ent_nefrouros,
        name='Dra. Natalia Charry',
        defaults={'email': 'coordinaciontalentohumanojr@itmsas.net', 'phone_number': 3102944906}
    )
    HumanTalent.objects.get_or_create(
        enterprise=ent_tech,
        name='Lic. Paola Andrade',
        defaults={'email': 'th@techsolutions.com.co', 'phone_number': 3123456789}
    )

    # 4. Solicitudes de Asignación
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=60)
    end_date = start_date + datetime.timedelta(days=180)

    # Solicitud 1: Aprendiz Principal (Demo) - ASIGNADO
    req_1, _ = RequestAsignation.objects.get_or_create(
        apprentice=apprentices[0],
        defaults={
            'enterprise': ent_nefrouros,
            'modality_productive_stage': mod_contrato,
            'boss': boss_1,
            'request_date': start_date,
            'date_start_production_stage': start_date,
            'date_end_production_stage': end_date,
            'request_state': RequestState.ASIGNADO
        }
    )

    # Asignación de instructor 1 para Solicitud 1
    asig_1, _ = AsignationInstructor.objects.get_or_create(
        request_asignation=req_1,
        defaults={'instructor': instructor_1, 'date_asignation': start_date}
    )

    # Visitas para Asignación 1
    VisitFollowing.objects.get_or_create(
        asignation_instructor=asig_1,
        visit_number=1,
        defaults={
            'name_visit': 'Visita 1: Concertación de Plan de Trabajo',
            'state_visit': 'APROBADA',
            'scheduled_date': start_date + datetime.timedelta(days=15),
            'date_visit_made': start_date + datetime.timedelta(days=15),
            'observations': 'Concertación inicial exitosa. Funciones asignadas en soporte y desarrollo de integraciones REST.',
            'observation_state_visit': 'Cumplimiento del 100% de los acuerdos iniciales.'
        }
    )
    VisitFollowing.objects.get_or_create(
        asignation_instructor=asig_1,
        visit_number=2,
        defaults={
            'name_visit': 'Visita 2: Seguimiento Parcial',
            'state_visit': 'APROBADA',
            'scheduled_date': start_date + datetime.timedelta(days=90),
            'date_visit_made': start_date + datetime.timedelta(days=90),
            'observations': 'Avance óptimo en bitácoras quincenales. El aprendiz demuestra sólidas competencias técnicas.',
            'observation_state_visit': 'Seguimiento al 50% de etapa práctica aprobado sin observaciones disciplinarias.'
        }
    )
    VisitFollowing.objects.get_or_create(
        asignation_instructor=asig_1,
        visit_number=3,
        defaults={
            'name_visit': 'Visita 3: Evaluación Final',
            'state_visit': 'PROGRAMADA',
            'scheduled_date': end_date - datetime.timedelta(days=10),
            'observations': 'Pendiente presentación de proyecto de innovación y paz y salvo de la empresa.',
            'observation_state_visit': 'Fecha acordada con jefe inmediato y aprendiz.'
        }
    )

    # Solicitud 2: Aprendiz 2 - ASIGNADO con Instructor 2
    if len(apprentices) > 1:
        req_2, _ = RequestAsignation.objects.get_or_create(
            apprentice=apprentices[1],
            defaults={
                'enterprise': ent_tech,
                'modality_productive_stage': mod_vinculo,
                'boss': boss_2,
                'request_date': start_date + datetime.timedelta(days=10),
                'date_start_production_stage': start_date + datetime.timedelta(days=15),
                'date_end_production_stage': end_date,
                'request_state': RequestState.ASIGNADO
            }
        )
        asig_2, _ = AsignationInstructor.objects.get_or_create(
            request_asignation=req_2,
            defaults={'instructor': instructor_2, 'date_asignation': start_date + datetime.timedelta(days=15)}
        )
        VisitFollowing.objects.get_or_create(
            asignation_instructor=asig_2,
            visit_number=1,
            defaults={
                'name_visit': 'Visita 1: Concertación de Plan de Trabajo',
                'state_visit': 'APROBADA',
                'scheduled_date': start_date + datetime.timedelta(days=25),
                'date_visit_made': start_date + datetime.timedelta(days=25),
                'observations': 'Plan de trabajo en desarrollo frontend con React concertado.',
                'observation_state_visit': 'Aprobada.'
            }
        )

    # Solicitud 3: Aprendiz 3 - SIN_ASIGNAR (para probar bandeja de asignación del Coordinador)
    if len(apprentices) > 2:
        RequestAsignation.objects.get_or_create(
            apprentice=apprentices[2],
            defaults={
                'enterprise': ent_banco,
                'modality_productive_stage': mod_contrato,
                'request_date': today - datetime.timedelta(days=5),
                'date_start_production_stage': today + datetime.timedelta(days=10),
                'date_end_production_stage': today + datetime.timedelta(days=190),
                'request_state': RequestState.SIN_ASIGNAR
            }
        )

    # Solicitud 4: Aprendiz 4 - VERIFICANDO
    if len(apprentices) > 3:
        RequestAsignation.objects.get_or_create(
            apprentice=apprentices[3],
            defaults={
                'enterprise': ent_tech,
                'modality_productive_stage': mod_pasantia,
                'request_date': today - datetime.timedelta(days=3),
                'date_start_production_stage': today + datetime.timedelta(days=15),
                'date_end_production_stage': today + datetime.timedelta(days=195),
                'request_state': RequestState.VERIFICANDO
            }
        )

    stdout.write(style.SUCCESS('  [OK] Modalidades, Empresas, Solicitudes y Visitas de Seguimiento sembradas.'))
