# Requisitos módulo de reservas

La aplicación se desarrolla como módulo de Odoo v19

El sistema debe permitir la gestión completa (Alta, Baja y Modificación - CRUD) de todos los elementos descritos a continuación por parte de los roles vicedirector de Medios Tecnológicos y Medios tecnológicos. Cada elemento reservable debe tener una lista de roles que le permitan ser reservados, así, por defecto todos serán reservables por el rol profesor, pero algunos solo lo serán por el rol equipo directivo y no por el de profesor. Además, cada elemento reservable podrá generar un código QR para la consulta de su ocupación.

## Gestión de ubicaciones (Sedes y Edificios)

Es el nivel macro de la infraestructura. Las ubicaciones actúan como contenedores de los espacios físicos. Un usuario no reserva una ubicación, sino los espacios que hay dentro de ella.

* Sedes iniciales a configurar: Edificio Berenguer, Edificio Principal, Girola, IES 26 y Complejo (el sistema debe permitir añadir/borrar/modificar nuevas en el futuro).

## Categorías de elementos reservables

Dentro del sistema, el usuario podrá reservar tres tipologías de elementos:

### Espacios Físicos (Infraestructura de trabajo)

Contenidos dentro de una Ubicación, se estructuran en dos niveles operativos:

* **Espacios completos**: Inicialmente serán los siguientes, pero se podrán añadir nuevos en un futuro (al reservar este nivel, se bloquea el uso total del recinto y de los puestos de trabajo individuales que contenga):

  * Cabinas: Espacios destinados principalmente a impartir Tutorías Colectivas (TC) o Tutorías Individuales (TI), dotados de ordenador, cámara y monitores.

  * Salas de grabación: Espacios insonorizados o adaptados específicamente para la creación de contenidos audiovisuales.

  * Salas de reuniones: Espacios diseñados para el trabajo colaborativo de equipos docentes o comisiones.

  * Despachos: Espacios compartidos que contienen múltiples puestos de trabajo.

* **Puestos de trabajo individuales**: Puestos específicos dentro de un espacio mayor (ej. Puesto 98 que está en el despacho 0.1). Si se reserva un puesto, el sistema marcará el espacio padre como "parcialmente ocupado", permitiendo a otros usuarios reservar los puestos restantes.

### Equipamiento (Materiales prestables)  

Bienes muebles y recursos tecnológicos (ej. cámaras, tablets, micrófonos).

* **Integración con Inventario**: Estos elementos no se crearán en el módulo de reservas, sino que el sistema leerá del Módulo de Inventario. Al marcar un objeto como "Prestable" en el inventario, aparecerá automáticamente en el listado de reservas.

* **Ubicación Base**: Cada material estará asignado a un Espacio Físico Completo (ej. Conserjería, Despacho 1.2) para su recogida y devolución.

* **Condición de movilidad**: La reserva de estos objetos será independiente. Si un recurso tecnológico está anclado o vinculado permanentemente a un espacio concreto (ej. una pantalla interactiva fija), no será reservable desde aquí (ni aparecerá); el usuario deberá reservar el "Espacio físico" que lo contiene.

### Servicios de Apoyo  

Asistencia profesional requerida para el desarrollo de la actividad académica (ej. Asesoramiento TIC, Soporte Audiovisual, Traducción, Orientación…).

* **Gestión por capacidad (Pool de horas)**: El usuario reserva el "Servicio" genérico, no a una persona concreta. El sistema tendrá parametrizados a los profesionales (equipo de medios audiovisuales, técnicos, etc.) y las horas semanales que ofertan para dicho servicio.

* **Asignación Personalizada**: El usuario dispondrá de un desplegable para indicar una "Persona"

* **Concurrencia**: La disponibilidad horaria del servicio vendrá dictada por el número de profesionales activos en esa franja. El sistema permitirá tantas reservas simultáneas del mismo servicio como profesionales haya disponibles en dicho momento.

## Atributos de los distintos elementos

### Ubicación

* Nombre  

* Descripción: Usos permitidos, normas de acceso y cualquier información relevante.

* Fotografías: Imágenes representativas del edificio.

* Plano y Localización: Imagen del plano de distribución interior y enlace/vista integrada de Google Maps.

* Horario de apertura: Franjas horarias en las que el edificio está operativo (las reservas de sus espacios interiores nunca podrán exceder este horario).

* Etiquetas: se le podrá asignar distintas etiquetas a cada elemento, para poder filtrar por cualquiera de ellas en la ventana de reservas.

### Espacios completos

* Nombre

* Descripción: Usos permitidos, normas de acceso y cualquier información relevante.

* Fotografía: Imagen del espacio.

* Fotografía 360º.

* Plano: Imagen del plano de la ubicación en el que se indica dónde está el espacio.

* Horario de reservas: Franjas horarias en las que se puede reservar el recurso.

* Ubicación: que referencia a Ubicación

* Etiquetas: se le podrá asignar distintas etiquetas a cada elemento, para poder filtrar por cualquiera de ellas en la ventana de reservas.

### Puestos de trabajo individuales

* Nombre

* Descripción: Usos permitidos, normas de acceso y cualquier información relevante.

* Fotografía: Imagen del puesto.

* Plano: Imagen del plano de la ubicación en el que se indica dónde está el puesto.

* Espacio: que referencia a Espacios completos

* Etiquetas: se le podrá asignar distintas etiquetas a cada elemento, para poder filtrar por cualquiera de ellas en la ventana de reservas.

* Reservable directamente: Si se puede reservar el elemento o está integrado en un espacio como una cabina, en este caso se reserva la cabina y este puesto NO se podría reservar y no aparecería.

### Servicios de Apoyo  

* Nombre

* Descripción: Qué servicio se va a prestar: Asesoramiento TIC, Soporte Audiovisual, Traducción, Orientación…), ubicación del servicio o si se traslada el servicio al puesto de la persona que le reserva.

* Imagen descriptiva: Imagen del servicio.

* Plano: Imagen del plano de la ubicación en el que se indica dónde se efectúa el servicio o si es al puesto del que reserva.

* Etiquetas: se le podrá asignar distintas etiquetas a cada elemento, para poder filtrar por cualquiera de ellas en la ventana de reservas.

## Interfaz de reservas

Para hacer una reserva el usuario debe elegir la ubicación y el espacio/puesto/ servicio de apoyo, de manera que, cuando lo elija pueda ver todos los recursos disponibles para dicha elección, e incluso poder buscar dentro de la lista el elemento que busca (que utilizará el campo nombre o si se marca un check utilizará también las etiquetas para la búsqueda). Una vez encontrado y seleccionado el recurso, podrá seleccionar fecha y hora de inicio y fecha y hora de final, y podrá modificar tanto la hora de inicio como la de fin manualmente en rangos de 1 minuto.

 Todos los bloques seleccionados se podrán confirmar para las fechas seleccionadas y que se repitan todas las semanas hasta cierta fecha y con el mismo comentario.  

En la reserva se debe fijar un motivo de la reserva y quedará registrado quién lo ha reservado. En los bloques No disponibles aparecerá la información de quien lo ha reservado y el motivo.

Además, deberá existir una vista mientras no se selecciona un recurso concreto, en el que se visualizará la ocupación de todos los recursos de la categoría en la semana seleccionada:

Hay que tener en cuenta las siguientes restricciones:

Restricciones configurables a nivel de aplicación:  

* Antelación con que se puede reservar un elemento (no afectarán al equipo directivo)

* Máximo de semanas a reservar (no afectarán al equipo directivo)

* El equipo directivo podrá anular o modificar reservas, aunque sean de otras personas, les llegará un correo cuando esto se produzca.

* Se debe validar que en la repetición semanal no se solapa en ningún momento la reserva.

* El usuario puede anular cualquier reserva que haya efectuado él.

* Cuando se selecciona un elemento a reservar debe mostrarse la ficha de dicho elemento con toda la información (puesto de trabajo, espacio… con todo lo que incluye) (puede ser en una pestaña, en una especie de tooltip o en un enlace que abra una ventana emergente)

Esta interfaz de ficha se podría emplear también para el alta de los distintos elementos (ubicaciones, espacios…).

* Debe existir una forma rápida de reservar todas las cabinas o cualquier espacio para las distintas materias. Se podría obtener de los horarios de los profesores, o mediante un csv o cualquier sistema que permita reservar rápidamente los espacios para las TCs.

* Se debe poder liberar de golpe los espacios (Cabinas) reservadas a ciertos estudios (2º de ciclos, 2º de bachillerato), para cuando finalicen esos estudios (también se podría utilizar sencillamente las fechas de finalización de reservas cuando se dan de alta y no haría falta esta funcionalidad.

## Roles  

Los roles afectados por esta aplicación serían:

* Equipo directivo: acceso total al uso y reservas.

* Vicedirección de Medios Tecnológicos: gestión total (alta, baja y modificación)

* Medios Tecnológicos: gestión total (alta, baja y modificación)

* Profesor: reservas

## Informes

* Estadísticas de ocupación de los distintos espacios por día de la semana, por mes, por franja horaria.

* Estadísticas de ocupación por enseñanza.

* Estadísticas de reservas por usuario, qué espacios ha reservado, cantidad y horas totales.

## Vista de consulta

Cada elemento reservable podrá generar un código QR que se pondrá en un lugar visible para que cualquier usuario pueda consultar el estado de ocupación y quién lo ha reservado, para poder contactar con él en caso de que sea necesario, solo en la vista diaria aparecerá esa información o en la vista semanal/mensual al pinchar sobre la franja ocupada.
