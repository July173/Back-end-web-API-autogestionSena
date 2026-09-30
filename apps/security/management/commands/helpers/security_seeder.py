"""
Modular seeder for Security Domain: DocumentTypes, Roles, Modules, Forms,
Permissions, RoleFormPermission matrix, and Demo Users.
"""
import os
from apps.security.entity.models.DocumentType import DocumentType
from apps.security.entity.models.Role import Role
from apps.security.entity.models.Person import Person
from apps.security.entity.models.User import User
from apps.security.entity.models.Module import Module
from apps.security.entity.models.Form import Form
from apps.security.entity.models.FormModule import FormModule
from apps.security.entity.models.Permission import Permission
from apps.security.entity.models.RoleFormPermission import RoleFormPermission


def seed_security_domain(stdout, style):
    stdout.write(style.NOTICE('  [1/3] Sembrando Dominio de Seguridad y Permisos...'))

    # 1. Tipos de documento
    doc_cc, _ = DocumentType.objects.get_or_create(acronyms='CC', defaults={'name': 'Cédula de Ciudadanía', 'active': True})
    DocumentType.objects.get_or_create(acronyms='TI', defaults={'name': 'Tarjeta de Identidad', 'active': True})
    DocumentType.objects.get_or_create(acronyms='CE', defaults={'name': 'Cédula de Extranjería', 'active': True})
    DocumentType.objects.get_or_create(acronyms='NIT', defaults={'name': 'Número de Identificación Tributaria', 'active': True})

    # 2. Roles
    roles_def = [
        (1, 'Administrador', 'Administrador del sistema con acceso completo'),
        (2, 'Aprendiz', 'Aprendiz SENA con acceso a novedades y seguimiento'),
        (3, 'Instructor', 'Instructor SENA para control de fichas y aprendices'),
        (4, 'Coordinador', 'Coordinador académico y de asignación de etapas'),
        (5, 'Operador Sofia Plus', 'Operador para sincronización de datos y Excel'),
    ]
    roles_dict = {}
    for r_id, r_name, r_desc in roles_def:
        r, _ = Role.objects.get_or_create(id=r_id, defaults={'type_role': r_name, 'description': r_desc, 'active': True})
        if r.type_role != r_name:
            r.type_role = r_name
            r.save()
        roles_dict[r_id] = r

    # 3. Módulos del sistema
    modules_def = [
        (1, 'Inicio', 'Parte inicial del sistema'),
        (2, 'Seguridad', 'Administra el sistema'),
        (3, 'Asignar seguimientos', 'Proceso de asignación y seguimiento de etapa práctica'),
    ]
    modules_dict = {}
    for m_id, m_name, m_desc in modules_def:
        m, _ = Module.objects.get_or_create(id=m_id, defaults={'name': m_name, 'description': m_desc, 'active': True})
        modules_dict[m_id] = m

    # 4. Formularios
    forms_def = [
        (1, 'Administración', 'Control de usuarios y roles', '/admin', 2),
        (2, 'Registro Masivo', 'Carga masiva de aprendices e instructores con Excel', '/mass-registration', 2),
        (3, 'Inicio', 'Página principal del sistema', '/home', 1),
        (4, 'Solicitud', 'Solicitud de aprendiz para asignación de etapa productiva', '/request-registration', 3),
        (5, 'Reasignar', 'Reasignación de instructor', '/reassign', 3),
        (6, 'Seguimiento', 'Seguimiento a aprendices en etapa práctica', '/following', 3),
        (7, 'Historial de seguimiento', 'Historial consolidado de seguimientos', '/following-history', 3),
        (8, 'Evaluar visita final', 'Evaluación de visita final de etapa productiva', '/evaluate-final-visit', 3),
        (9, 'Asignar', 'Asignación de instructor a aprendiz', '/assign', 3),
    ]
    forms_dict = {}
    for f_id, f_name, f_desc, f_path, mod_id in forms_def:
        f, _ = Form.objects.get_or_create(id=f_id, defaults={'name': f_name, 'description': f_desc, 'path': f_path, 'active': True})
        forms_dict[f_id] = f
        FormModule.objects.get_or_create(form=f, module=modules_dict[mod_id])

    # 5. Permisos
    perms_def = [(1, 'Ver', 'Visualizar datos'), (2, 'Editar', 'Editar datos'), (3, 'Registrar', 'Ingresar datos'), (4, 'Eliminar', 'Borrado')]
    perms_dict = {}
    for p_id, p_type, p_desc in perms_def:
        p, _ = Permission.objects.get_or_create(id=p_id, defaults={'type_permission': p_type, 'description': p_desc})
        perms_dict[p_id] = p

    # 6. Matriz de Permisos (RoleFormPermission)
    # Administrador: todos los formularios con permisos Ver, Editar, Registrar, Eliminar
    for f in forms_dict.values():
        for p in perms_dict.values():
            RoleFormPermission.objects.get_or_create(role=roles_dict[1], form=f, permission=p)

    # Aprendiz: Inicio (3), Solicitud (4)
    for fid in [3, 4]:
        RoleFormPermission.objects.get_or_create(role=roles_dict[2], form=forms_dict[fid], permission=perms_dict[1])
        RoleFormPermission.objects.get_or_create(role=roles_dict[2], form=forms_dict[fid], permission=perms_dict[3])

    # Instructor: Inicio (3), Seguimiento (6)
    for fid in [3, 6]:
        for pid in [1, 2, 3]:
            RoleFormPermission.objects.get_or_create(role=roles_dict[3], form=forms_dict[fid], permission=perms_dict[pid])

    # Coordinador: Inicio (3), Asignar (9), Reasignar (5), Historial (7), Evaluar (8), Masivo (2)
    for fid in [3, 9, 5, 7, 8, 2]:
        for pid in [1, 2, 3]:
            RoleFormPermission.objects.get_or_create(role=roles_dict[4], form=forms_dict[fid], permission=perms_dict[pid])

    # Operador Sofia: Inicio (3), Masivo (2)
    for fid in [3, 2]:
        for pid in [1, 2, 3]:
            RoleFormPermission.objects.get_or_create(role=roles_dict[5], form=forms_dict[fid], permission=perms_dict[pid])

    # 7. Usuarios Demo
    pwd = os.getenv('DEMO_DEFAULT_PASSWORD', 'Sena2026*')
    demo_users = [
        ('admin.demo@sena.edu.co', 'Admin', 'Sistema', 1000000001, 3101111111, 1),
        ('aprendiz.demo@soy.sena.edu.co', 'Carlos', 'Gómez Aprendiz', 1000000002, 3102222222, 2),
        ('instructor.demo@sena.edu.co', 'Ing. Javier', 'Mendoza Instructor', 1000000003, 3103333333, 3),
        ('coordinador.demo@sena.edu.co', 'Dra. Claudia', 'Ríos Coordinadora', 1000000004, 3104444444, 4),
        ('sofia.demo@sena.edu.co', 'Operador', 'Sofia SENA', 1000000005, 3105555555, 5),
        ('bscortes40@soy.sena.edu.co', 'Brayan Stid', 'Cortés Lombana', 1075300000, 3142208945, 1),
    ]
    for email, fn, ln, ident, phone, rid in demo_users:
        person, _ = Person.objects.get_or_create(
            number_identification=ident,
            defaults={'type_identification': doc_cc, 'first_name': fn, 'first_last_name': ln, 'phone_number': phone, 'active': True}
        )
        u, _ = User.objects.get_or_create(email=email, defaults={'person': person, 'role': roles_dict[rid], 'is_active': True})
        u.person = person
        u.role = roles_dict[rid]
        u.is_active = True
        u.registered = False
        u.set_password(pwd)
        u.save()

    stdout.write(style.SUCCESS('  [OK] Seguridad, permisos y usuarios demo sembrados.'))
    return roles_dict, doc_cc
