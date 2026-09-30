"""
Modular seeder for General SENA Domain:
Regional, Center, Sede, KnowledgeArea, TypeContract, Program, Ficha, Instructor, and Apprentice.
"""
import datetime
from apps.security.entity.models.Person import Person
from apps.security.entity.models.User import User
from apps.general.entity.models.Regional import Regional
from apps.general.entity.models.Center import Center
from apps.general.entity.models.Sede import Sede
from apps.general.entity.models.KnowledgeArea import KnowledgeArea
from apps.general.entity.models.TypeContract import TypeContract
from apps.general.entity.models.Program import Program
from apps.general.entity.models.Ficha import Ficha
from apps.general.entity.models.Instructor import Instructor
from apps.general.entity.models.Apprentice import Apprentice


def seed_general_domain(stdout, style, doc_cc):
    stdout.write(style.NOTICE('  [2/3] Sembrando Dominio General del SENA (Sedes, Fichas, Aprendices)...'))

    # 1. Regionales
    reg_huila, _ = Regional.objects.get_or_create(code_regional=7, defaults={'name': 'Regional Huila', 'description': 'Sede surcolombiana', 'address': 'Carrera 5 No. 8-45, Neiva'})
    reg_dc, _ = Regional.objects.get_or_create(code_regional=1, defaults={'name': 'Regional Distrito Capital', 'description': 'Sede Bogotá', 'address': 'Calle 57 No. 8-69, Bogotá'})
    Regional.objects.get_or_create(code_regional=2, defaults={'name': 'Regional Antioquia', 'description': 'Sede Medellín', 'address': 'Calle 52 No. 48-30, Medellín'})

    # 2. Centros
    center_cies, _ = Center.objects.get_or_create(code_center=7001, defaults={'name': 'Centro de la Industria, la Empresa y los Servicios (CIES)', 'address': 'Carrera 9 No. 68-50, Neiva', 'regional': reg_huila})
    center_cgmlti, _ = Center.objects.get_or_create(code_center=1004, defaults={'name': 'Centro de Gestión de Mercados, Logística y TIC', 'address': 'Carrera 30 No. 17-52, Bogotá', 'regional': reg_dc})

    # 3. Sedes
    sede_neiva, _ = Sede.objects.get_or_create(code_sede=700101, defaults={'name': 'Sede Comercio y Servicios Neiva', 'address': 'Carrera 9 No. 68-50, Neiva', 'phone_sede': 3142208945, 'email_contact': 'cies.neiva@sena.edu.co', 'center': center_cies})
    Sede.objects.get_or_create(code_sede=100401, defaults={'name': 'Sede TIC Calle 52 Bogotá', 'address': 'Calle 52 No. 13-65, Bogotá', 'phone_sede': 3101111111, 'email_contact': 'gestiontic@sena.edu.co', 'center': center_cgmlti})

    # 4. Áreas y Contratos
    ka_tic, _ = KnowledgeArea.objects.get_or_create(name='Tecnologías de la Información y Software', defaults={'description': 'Desarrollo, nube y arquitecturas'})
    ka_admin, _ = KnowledgeArea.objects.get_or_create(name='Gestión Administrativa y Financiera', defaults={'description': 'Procesos contables y administrativos'})

    tc_planta, _ = TypeContract.objects.get_or_create(name='Planta', defaults={'description': 'Personal permanente'})
    tc_ops, _ = TypeContract.objects.get_or_create(name='OPS', defaults={'description': 'Prestación de Servicios'})

    # 5. Programas
    prog_adso, _ = Program.objects.get_or_create(code_program=228106, defaults={'name': 'Tecnología en Análisis y Desarrollo de Software (ADSO)', 'description': 'Desarrollo frontend, backend, APIs y pruebas'})
    prog_redes, _ = Program.objects.get_or_create(code_program=228107, defaults={'name': 'Tecnología en Gestión de Redes de Datos', 'description': 'Infraestructura, redes y ciberseguridad'})
    prog_cont, _ = Program.objects.get_or_create(code_program=123101, defaults={'name': 'Tecnología en Gestión Contable y Financiera', 'description': 'Contabilidad corporativa y tributaria'})

    # 6. Fichas
    ficha_adso_1, _ = Ficha.objects.get_or_create(file_number=2670123, defaults={'program': prog_adso, 'type_modality': 'Presencial'})
    ficha_adso_2, _ = Ficha.objects.get_or_create(file_number=2750456, defaults={'program': prog_adso, 'type_modality': 'Virtual'})
    Ficha.objects.get_or_create(file_number=2820789, defaults={'program': prog_redes, 'type_modality': 'Presencial'})
    Ficha.objects.get_or_create(file_number=2910333, defaults={'program': prog_cont, 'type_modality': 'Presencial'})

    # 7. Instructores
    inst_user = User.objects.filter(email='instructor.demo@sena.edu.co').first()
    today = datetime.date.today()
    one_year = today + datetime.timedelta(days=365)
    instructor_primary, _ = Instructor.objects.get_or_create(
        person=inst_user.person,
        defaults={'contract_type': tc_planta, 'knowledge_area': ka_tic, 'contract_start_date': today, 'contract_end_date': one_year, 'assigned_learners': 15, 'is_followup_instructor': True}
    )

    # Segundo instructor demo
    p_inst2, _ = Person.objects.get_or_create(number_identification=1000000020, defaults={'type_identification': doc_cc, 'first_name': 'Ing. Diana', 'first_last_name': 'Torres', 'phone_number': 3118889900, 'active': True})
    instructor_secondary, _ = Instructor.objects.get_or_create(
        person=p_inst2,
        defaults={'contract_type': tc_ops, 'knowledge_area': ka_tic, 'contract_start_date': today, 'contract_end_date': one_year, 'assigned_learners': 8, 'is_followup_instructor': True}
    )

    # 8. Aprendices
    apprentice_user = User.objects.filter(email='aprendiz.demo@soy.sena.edu.co').first()
    apprentice_primary, _ = Apprentice.objects.get_or_create(
        person=apprentice_user.person,
        defaults={'ficha': ficha_adso_1}
    )

    # Más aprendices demo para que las tablas tengan volumen
    demo_apprentices = [
        ('Valentina', 'López Castro', 1000000031, 3124567890, ficha_adso_1),
        ('Andrés Felipe', 'Muñoz Pardo', 1000000032, 3135678901, ficha_adso_1),
        ('Laura Camila', 'Díaz Ortiz', 1000000033, 3146789012, ficha_adso_2),
        ('Daniel Santiago', 'Rojas Mora', 1000000034, 3157890123, ficha_adso_2),
    ]
    created_apprentices = [apprentice_primary]
    for fn, ln, num, ph, fch in demo_apprentices:
        p, _ = Person.objects.get_or_create(number_identification=num, defaults={'type_identification': doc_cc, 'first_name': fn, 'first_last_name': ln, 'phone_number': ph, 'active': True})
        app, _ = Apprentice.objects.get_or_create(person=p, defaults={'ficha': fch})
        created_apprentices.append(app)

    stdout.write(style.SUCCESS('  [OK] Sedes, Programas, Fichas, Instructores y Aprendices sembrados.'))
    return instructor_primary, instructor_secondary, created_apprentices
