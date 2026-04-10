# Manual de Usuario: Sistema de Reservas

Este documento describe el flujo de uso del módulo **Maya Booking** para los usuarios finales, detallando cómo visualizar los horarios y realizar la reserva de los diferentes recursos (espacios, equipos, etc.).

---

## 1. Acceso

Para comenzar a gestionar reservas, el usuario debe acceder al menú principal de la aplicación.
1. Haz clic en el menú superior **Maya | Booking**.
2. Desde la vista kanban de Tipos de Recurso selecciona la card (menos los botones) de uno de los tipos existentes.
3. Se mostrará por defecto la vista de **Calendario (Timeline)**, donde se pueden visualizar las reservas actuales agrupadas por recurso.

Las reservas confirmadas aparecen en color rojo y muestran el nombre de la persona que ha reservado junto con el motivo.

---

## 2. Realizar una Reserva

El sistema utiliza un modelo de reservas basado en **Sesiones Predefinidas** (modelo session_schedule en el módulo maya_core) asignadas al recurso.

### Paso 1: Abrir el formulario
Desde la vista del calendario (Timeline), haz docble clic sobre una de la filas existente (SINASIGNAR en caso de no haber otra) para abrir el formulario de creación.

### Paso 2: Rellenar los datos de la reserva
En el formulario modal, completa los siguientes campos:

* **Motivo / Descripción (Obligatorio):** Indica el propósito de la reserva (ej. *Reunión de departamento*, *Examen*, etc.).
* **Recurso a reservar:** Selecciona el espacio o elemento que necesitas (aquí se indica la fila dentor del timeline).
* **Fecha de Reserva:** Selecciona en el calendario el día exacto en el que deseas hacer la reserva.
* **Sesión de Inicio:** Al elegir un día y un recurso, este desplegable te mostrará *únicamente* los horarios disponibles de sesiones asignadas para ese día de la semana en concreto.
* **Nº de Sesiones Consecutivas:** Si necesitas el espacio durante más de una sesión, indica el número (ej. "2" para reservar el bloque actual y el siguiente).

> El campo *Persona que reserva* se autocompleta con tu usuario logueado y es de solo lectura. Las *Fechas y Horas de Inicio/Fin* se calculan automáticamente basándose en los horarios de las sesiones asignadas.


### Paso 3: Guardar y Confirmar
Una vez revisados los datos, haz clic en el botón morado **Guardar**. 

El sistema realizará una comprobación instantánea, si el recurso está libre en ese horario, la ventana se cerrará y tu reserva aparecerá inmediatamente en el Timeline. Si durante la creación de la reserva, o lo que fuera, se a creado otra en el mismo "slot" mostrará un mensaje de error y no te dejará solapar la reserva.

---

## 3. Modificación y Cancelación

**no está permitido arrastrar ni redimensionar las reservas con el ratón** en la vista de Timeline.

Para corregir un error se puede:
1. Hacer clic sobre la reserva en color rojo en el Timeline.
2. En el formulario que se abre, pulsar el botón **Descartar / Borrar**.
3. Volver a crear una reserva nueva con los datos correctos.