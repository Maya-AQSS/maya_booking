# Arquitectura y Riesgos

## Decisiones Arquitectónicas (NFRs)

1. **Módulo de Odoo v19**: La solución técnica no es standalone, sino un módulo directamente integrado sobre el Framework de Odoo v19, aprovechando sus capacidades de ORM, vistas (XML) y controladores web (Python).
2. **Dependencias a otros módulos**: Integración obligatoria con el **Módulo de Inventario** existente en Odoo para sincronizar los bienes de equipamiento (materiales prestables).
3. **Escalabilidad de consultas temporales**: Especial cuidado en la eficiencia de las validaciones de solapamiento para reservas que se repiten semanalmente.

## Análisis de Riesgos STRIDE

| Categoría | Amenaza | Mitigación Architetónica |
| --------- | -------- | ------------------------- |
| **S**poofing | Usuarios suplantando al equipo directivo para modificar reservas ajenas. | Autenticación robusta provista por Odoo v19. Uso de Access Rules (ir.model.access) y Record Rules (ir.rule) estandarizadas. |
| **T**ampering | Modificación de fechas de reservas pasadas o alteración de franjas horarias interceptando peticiones. | Validaciones server-side estrictas. Odoo ORM constraints (`_check_overlap`). |
| **R**epudiation | Un usuario reserva una sala, no se presenta y niega haberlo hecho. | Auditoría completa con `mail.thread` (chatter de Odoo) para llevar un tracking inmutable de cambios de estado y fechas de creación/modificación. |
| **I**nformation Disclosure | Acceder vía URL a los datos analíticos o CSVs de ocupación sin privilegios | Restringir el modelo de informes (`report`) al rol de Equipo Directivo o Vicedirección. |
| **D**enial of Service | Inserción de reservas concurrentes provocando contención en la base de datos de PostgreSQL (Odoo). | Manejo adecuado de `Transaction Isolation`. Constraints a nivel de base de datos (`EXCLUDE USING gist`) para prevenir dobles reservas. |
| **E**levation of Privilege | Un Profesor intentando reservar un despacho marcado como "Sólo Directiva". | Verificación de los grupos de seguridad del usuario en el método `create` o a nivel de Action Views. |
