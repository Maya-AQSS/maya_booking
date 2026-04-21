/** @odoo-module **/

import {TimelineArchParser} from "../../../../web_timeline/static/src/views/timeline/timeline_arch_parser.esm";
import {TimelineRenderer} from "../../../../web_timeline/static/src/views/timeline/timeline_renderer.esm";
import {TimelineController} from "../../../../web_timeline/static/src/views/timeline/timeline_controller.esm";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

import {visitXML} from "@web/core/utils/xml";
import {FormViewDialog} from "@web/views/view_dialogs/form_view_dialog";
import {makeContext} from "@web/core/context";


// ─────────────────────────────────────────────
// 1. Patch del ArchParser: leer group_model
// ─────────────────────────────────────────────
patch(TimelineArchParser.prototype, {
  
    parse(arch, fields) {
        const archInfo = super.parse(arch, fields);
        visitXML(arch, (node) => {
            if (node.tagName === "timeline" && node.hasAttribute("group_model")) {
                archInfo.group_model = node.getAttribute("group_model");
            }
        });
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

patch(TimelineController.prototype, {

    async _onAdd(item, callback) {
        // Si no hay grupo válido, comportamiento original
        if (!item.group || item.group === -1) {
            return super._onAdd(item, callback);
        }

        const resourceId = item.group;

        // Convertir JS Date a float hora (9:30 → 9.5)
        const toFloatHour = (jsDate) => {
            const d = new Date(jsDate);
            return d.getHours() + d.getMinutes() / 60;
        };

        // Extraer fecha como string YYYY-MM-DD (en hora local)
        const toDateStr = (jsDate) => {
            const d = new Date(jsDate);
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, "0");
            const day = String(d.getDate()).padStart(2, "0");
            return `${y}-${m}-${day}`;
        };

        const dateStr = toDateStr(item.start);
        const startFloat = toFloatHour(item.start);
        // Si solo se hace click (sin arrastrar) end === start o es undefined
        const endFloat = item.end
            ? toFloatHour(item.end)
            : startFloat + 0.01;

        // Llamada RPC para obtener las sesiones que cubren el rango
        let sessionIds = [];
        try {
            sessionIds = await this.model.orm.call(
                "maya_booking.booking",
                "get_sessions_for_slot",
                [resourceId, dateStr, startFloat, endFloat],
            );
        } catch (e) {
            console.error("Error obteniendo sesiones:", e);
        }

        // Construir contexto combinando el del searchModel con nuestros defaults
        const context = {
            default_booking_resource_id: resourceId,
            default_booking_date: dateStr,
        };

        console.log(dateStr)

        // Many2many command 6: reemplazar con lista de ids
        if (sessionIds.length) {
            context.default_session_ids = [[6, 0, sessionIds]];
        }

        this.dialogService.add(
            FormViewDialog,
            {
                resId: false,
                context: makeContext([context], this.env.searchModel.context),
                onRecordSaved: async (record) => {
                    const new_record = await this.model.create_completed(record.resId);
                    callback(new_record);
                },
                resModel: this.model.model_name,
            },
            {onClose: () => callback()}
        );
    },
});