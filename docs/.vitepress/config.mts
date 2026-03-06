import { defineConfig } from 'vitepress';
import { withMermaid } from 'vitepress-plugin-mermaid';  // Necesario para diagramas C4/Mermaid

export default withMermaid(
  defineConfig({
    title: "Maya Booking",
    description: "Módulo de gestión de reservas para infraestructuras y recursos en Odoo v19",
    lang: 'es-ES',

    // Para GitHub Pages
    base: '/maya_booking/',
    srcDir: './src',

    ignoreDeadLinks: true,

    mermaid: {
      theme: 'dark'
    },

    themeConfig: {
      nav: [
        { text: 'Inicio', link: '/' },
        { text: 'Proyecto', link: '/0_descripcion_proyecto' },
        { text: 'Épicas y Features', link: '/1_epics_and_features' },
        { text: 'Backlog', link: '/backlog/F-01.1' },
        { text: 'Auditoría', link: '/AUDIT_LOG' },
      ],

      sidebar: [
        {
          text: '📋 Proyecto',
          items: [
            { text: 'Descripción del Proyecto', link: '/0_descripcion_proyecto' },
            { text: 'Épicas y Features', link: '/1_epics_and_features' },
            { text: 'Arquitectura y Riesgos', link: '/2_architecture_risks' },
            { text: 'Diagramas C4', link: '/3_c4_diagrams' },
            { text: 'Registro de Auditoría', link: '/AUDIT_LOG' },
          ]
        },

        // ─────────────────────────────────────────────────
        //  BACKLOG agrupado por CAPA TÉCNICA
        // ─────────────────────────────────────────────────
        {
          text: '🖥️ Frontend',
          collapsed: false,
          items: [
            { text: 'F-02.1 Interfaz de Búsqueda', link: '/backlog/F-02.1' },
            { text: 'F-03.1 Vista Semanal Ocupación', link: '/backlog/F-03.1' },
          ]
        },
        {
          text: '⚙️ Backend',
          collapsed: false,
          items: [
            { text: 'F-01.4 Integración Inventario', link: '/backlog/F-01.4' },
            { text: 'F-02.2 Lógica Solapamientos', link: '/backlog/F-02.2' },
            { text: 'F-02.3 Bloqueos Anidados', link: '/backlog/F-02.3' },
            { text: 'F-02.5 Liberación Espacios', link: '/backlog/F-02.5' },
            { text: 'F-02.6 Carga Masiva CSV', link: '/backlog/F-02.6' },
            { text: 'F-04.1 Control de Roles', link: '/backlog/F-04.1' },
            { text: 'F-04.2 Antelación y Límites', link: '/backlog/F-04.2' },
            { text: 'F-04.3 Reserva Restringida', link: '/backlog/F-04.3' },
          ]
        },
        {
          text: '🗄️ Base de Datos',
          collapsed: false,
          items: [
            { text: 'F-03.3 Panel Estadísticas', link: '/backlog/F-03.3' },
          ]
        },
        {
          text: '� Fullstack',
          collapsed: false,
          items: [
            { text: 'F-01.1 Gestión Ubicaciones', link: '/backlog/F-01.1' },
            { text: 'F-01.2 Gestión Espacios', link: '/backlog/F-01.2' },
            { text: 'F-01.3 Gestión Puestos', link: '/backlog/F-01.3' },
            { text: 'F-01.5 Servicios de Apoyo', link: '/backlog/F-01.5' },
            { text: 'F-02.4 Cancelación y Modificación', link: '/backlog/F-02.4' },
            { text: 'F-03.2 Generación QR', link: '/backlog/F-03.2' },
          ]
        },
      ],

      socialLinks: [
        { icon: 'github', link: 'https://github.com/Maya-AQSS/maya_booking' }
      ],

      footer: {
        message: 'Maya Booking — Módulo de Reservas Odoo v19',
        copyright: 'Copyright © 2026'
      },

      search: {
        provider: 'local'
      },

      editLink: {
        pattern: 'https://github.com/Maya-AQSS/maya_booking/edit/main/docs/:path',
        text: 'Editar esta página en GitHub'
      },

      lastUpdated: {
        text: 'Última actualización',
        formatOptions: {
          dateStyle: 'short',
          timeStyle: 'short'
        }
      }
    }
  })
)
