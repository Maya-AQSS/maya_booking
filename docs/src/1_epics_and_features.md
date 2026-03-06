# Desglose de Epics y Features: Maya Booking (Módulo de Odoo v19)

## Epic 1: Gestión de Infraestructura y Elementos Reservables

* **F-01.1**: Gestión de Ubicaciones (Sedes y Edificios)
* **F-01.2**: Gestión de Espacios Completos (Cabinas, Salas, Despachos)
* **F-01.3**: Gestión de Puestos de Trabajo Individuales
* **F-01.4**: Integración con Módulo de Inventario para Equipamiento Prestable
* **F-01.5**: Gestión de Servicios de Apoyo (Pool de profesionales capacitados)

## Epic 2: Motor de Reservas y Disponibilidad

* **F-02.1**: Interfaz de búsqueda de recursos y calendario de selección
* **F-02.2**: Lógica de solapamientos, repetición semanal y cálculo de franjas (1 min)
* **F-02.3**: Gestión de bloqueos anidados (Espacio Completo vs Puestos Individuales)
* **F-02.4**: Cancelación y modificación de reservas (con envío de correo a afectados)
* **F-02.5**: Liberación masiva de espacios por finalización de estudios
* **F-02.6**: Carga masiva de reservas (vía CSV / horarios) para Tutorías Colectivas

## Epic 3: Control de Ocupación, Informes y Auditoría

* **F-03.1**: Vista semanal de ocupación global y ficha de detalle del espacio
* **F-03.2**: Generación y consulta de QR para validación in-situ de ocupación
* **F-03.3**: Panel de informes y estadísticas (ocupación por franja, enseñanza, usuario)

## Epic 4: Seguridad y Reglas de Negocio (Roles)

* **F-04.1**: Control de acceso y visibilidad de reservas por Rol
* **F-04.2**: Restricciones temporales de reservas (antelación y número de semanas) configurables
* **F-04.3**: Permisos directos obligatorios (elementos sólo reservables por Equipo Directivo)
