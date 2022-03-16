from pprint import pprint
import io
import logging
import base64
import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning, CacheMiss

_logger = logging.getLogger(__name__)

from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang


class Rpt01XLSX(models.AbstractModel):
    _name = "report.mblz_mueve.report_mr_xlsx_01"
    _inherit = "report.report_xlsx.abstract"
    _description = "Report KPI O1"

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 14.0"}
        )
        sheet = workbook.add_worksheet(_("RPT_01"))
        # format_white = workbook.add_format({'bg_color': '#FFFFFF'})
        # sheet.write_column('A1:O1', '', format_white)

        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        style_cell_title = workbook.add_format({'font': 'Wheelbarrow',
                                                'font_size': 10,
                                                'bold': 1,
                                                'border': 0,
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'italic': False,
                                                'font_color': 'black'
                                                })

        style_cell_border = workbook.add_format({'font': 'Wheelbarrow',
                                                 'font_size': 8,
                                                 'bold': 1,
                                                 'border': 1,
                                                 'align': 'left',
                                                 'italic': False,
                                                 'valign': 'vcenter',
                                                 'text_wrap': True,
                                                 'bg_color': '#26de81',
                                                 })

        style_cell_bottom_text = workbook.add_format({'font': 'Wheelbarrow',
                                                      'font_size': 8,
                                                      'bold': 0,
                                                      'border': 1,
                                                      'align': 'left',
                                                      'valign': 'top',
                                                      'text_wrap': True,
                                                      'bg_color': '#dfe4ea',
                                                      })

        style_cell_bottom_text2 = workbook.add_format({'font': 'Wheelbarrow',
                                                       'font_size': 8,
                                                       'bold': 0,
                                                       'bottom': 0,
                                                       'align': 'left',
                                                       'valign': 'vcenter',
                                                       'text_wrap': True
                                                       })
        sheet_title = [
            _("SEQ"),
            _("EQUIPO"),
            _("CATEGORIA"),
            _("FECHA DE SOLICITUD"),
            _("FECHA ULT. MODIFICACIÓN"),
            _("FECHA DE CIERRE"),
            _("ETAPA ACTUAL"),
            _("NOMBRE DE OT"),
            _("RESPONSABLE"),

            _("TECNICO DE MTTO"),
            _("ESPECIALIDADES"),
            _("DESCRIPCION"),
            _("SISTEMA"),
            _("COMPONENTE"),

            _("PARTE DE HORAS / DESCRIPCION"),

        ]
        sheet.set_column(0, 6, 20)
        sheet.set_column(7, 7, 40)
        sheet.set_column(8, 9, 30)
        sheet.set_column(10, 11, 40)
        sheet.set_column(12, 14, 30)
        #
        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.freeze_panes(2, 0)
        sheet.set_tab_color('yellow')

        img_data = base64.b64decode(self.env.company.logo)
        image = io.BytesIO(img_data)

        cell_width = 300.0
        image_width = 22000.0
        cols_wide = 90.0
        scale = cell_width * cols_wide / image_width
        sheet.insert_image('A1', 'logo.png', {'image_data': image, 'x_scale': scale, 'y_scale': scale})
        row = 0
        sheet.set_row(row, 20)
        sheet.merge_range(row, 0, row + 1, 14, self.env.company.name, style_cell_title)

        row = 2
        sheet.write_row(row, 0, sheet_title, style_cell_border)
        row += 1
        for ot in objects:
            sheet.write_row(row, 0, [ot.name_seq, ot.equipment_id.name or '',
                                     ot.equipment_id.category_id.name or '',
                                     ot.request_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                     ot.write_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                     ot.close_date.strftime(DEFAULT_SERVER_DATE_FORMAT) if ot.close_date else '',
                                     ot.stage_id.name,
                                     ot.name, ot.user_id.name or ''
                                     ], style_cell_bottom_text)

            for idx, task in enumerate(ot.task_ids):
                if task.timesheet_ids:
                    sheet.set_row(row, len(task.timesheet_ids) * 15)
                sheet.write_row(row, 9, self._get_aux_data(task),
                                style_cell_bottom_text if idx == 0 else style_cell_bottom_text2)
                row += 1
            if not ot.task_ids:
                sheet.merge_range(row, 9, row, 14, '', style_cell_bottom_text)
                row += 1

    def _get_aux_data(self, task):
        task_description = ''
        if task.description:
            task_description = self.env['ir.fields.converter'].text_from_html(task.description)

        data = [task.employee_id.name or '',
                ', '.join(map(str, task.activity_speciality_ids.mapped('name'))).upper(),
                task_description or '']
        # SISTEMA
        system = ''
        for sis in task.activity_id.system_class_id.parent_ids:
            system += f"{sis.parent_id.name.upper() if sis.parent_id else ''}\n"
        data.append(system.strip())

        # COMPONENTE
        if task.activity_id.system_class_id and task.activity_id.system_class_id.name:
            data.append(
                task.activity_id.system_class_id.name.upper().strip() if task.activity_id.system_class_id else '')
        else:
            data.append('')

        # ACTIVIDADES EJECUTADAS
        tt = ''
        for ts_line in task.timesheet_ids:
            tt += f"{ts_line.name.upper().strip() if ts_line.name else ''}\n"
        data.append(tt)

        return data
