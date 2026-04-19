/** @odoo-module **/

import {TimelineArchParser} from "../../../../web_timeline/static/src/views/timeline/timeline_arch_parser.esm";
import {TimelineRenderer} from "../../../../web_timeline/static/src/views/timeline/timeline_renderer.esm";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

// ─────────────────────────────────────────────
// 1. Patch del ArchParser: leer group_model
// ─────────────────────────────────────────────
patch(TimelineArchParser.prototype, {
    parse(arch, fields) {
    
        // Llamamos al parser original
        const archInfo = super.parse(arch, fields); 
        // Leemos el atributo group_model del nodo <timeline>
        // visitXML ya ha procesado el arch, así que lo leemos directamente
        // del nodo raíz del arch
        const timelineNode = arch.querySelector("timeline")
            ? arch.querySelector("timeline")
            : arch;
  
        if (timelineNode && timelineNode.hasAttribute("group_model")) {
            archInfo.group_model = timelineNode.getAttribute("group_model");
        } 

        return archInfo;
    },
});

// ─────────────────────────────────────────────
// 2. Patch del Renderer: usar group_model en split_groups
// ─────────────────────────────────────────────
patch(TimelineRenderer.prototype, {

    async split_groups(records) {
        // this.params viene de this.model.params, que contiene el archInfo
        const groupModel = this.params.group_model;

        if (!groupModel) {
            // Sin group_model: comportamiento original
            return super.split_groups(records);
        }

        // Leemos el booking_type_id del contexto
        const bookingTypeId = this.env.searchModel?.context.timeline_booking_type_id; 

        // Dominio: si tenemos tipo de reserva, filtramos; si no, traemos todos
        const domain = bookingTypeId
          ? [["booking_type_ids", "in", [bookingTypeId]]]
          : [];

        // Cargamos todos los recursos bookables del modelo indicado
        const allResources = await this.orm.searchRead(
            groupModel,
            domain,
            ["id", "resource_name"],
            {order: "resource_name asc"}
        );

        const groups = [];

        // Grupo para reservas sin recurso asignado en el caso de que no haya un modelo de grupo
        // Si están todos los recursos ya listados no tiene sentido esta fila
        if (!groupModel) {
          groups.push({id: -1, content: _t("<b>SIN ASIGNAR</b>"), order: -1});
        }
        
        // Todos los recursos como grupos, tengan o no reservas
        allResources.forEach((resource, index) => {
            groups.push({
                id: resource.id,
                content: resource.resource_name,
                order: index,
            });
        });

        return groups;
    },
});