import io
import logging
import base64

from odoo import models

import json

_logger = logging.getLogger(__name__)

fmt = '%Y-%m-%d %H:%M:%S'
fmt_date = '%Y-%m-%d'


class OTXLSX(models.AbstractModel):
    _name = 'report.mblz_mueve.report_maintenance_request_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'report_maintenance_request_xlsx'

    def generate_xlsx_report(self, workbook, data, lines):
        for index, ot in enumerate(lines):
            sheet = workbook.add_worksheet('OT')
            sheet.set_tab_color('yellow')
            sheet.set_column(0, 8, 14)
            sheet.set_column(9, 9, 50)

            # formats
            style_cell_title = workbook.add_format({'font': 'Wheelbarrow',
                                                    'font_size': 10,
                                                    'bold': 1,
                                                    'border': 0,
                                                    'align': 'center',
                                                    'valign': 'vcenter',
                                                    'italic': False,
                                                    'font_color': 'black'
                                                    })
            style_title_ot = workbook.add_format({'font': 'Wheelbarrow',
                                                  'font_size': 12,
                                                  'bold': 1,
                                                  'border': 1,
                                                  'align': 'center',
                                                  'valign': 'vcenter',
                                                  'italic': False,
                                                  'font_color': 'black'
                                                  })
            style_title_form_general = workbook.add_format({'font': 'Wheelbarrow',
                                                            'font_size': 8,
                                                            'bold': 1,
                                                            'align': 'left',
                                                            'italic': False,
                                                            'valign': 'vcenter',
                                                            'text_wrap': True
                                                            })
            style_top_line = workbook.add_format({'font': 'Wheelbarrow',
                                                  'font_size': 8,
                                                  'bold': 1,
                                                  'left': 0,
                                                  'top': 1,
                                                  'right': 0,
                                                  'align': 'left',
                                                  'italic': False,
                                                  'valign': 'vcenter',
                                                  'text_wrap': True
                                                  })
            style1_top_4 = workbook.add_format({'font': 'Wheelbarrow',
                                                'font_size': 8,
                                                'bold': 1,
                                                'left': 1,
                                                'top': 1,
                                                'right': 0,
                                                'align': 'left',
                                                'italic': False,
                                                'valign': 'vcenter',
                                                'text_wrap': True
                                                })
            style_cell_bottom_title = workbook.add_format({'font': 'Wheelbarrow',
                                                           'font_size': 8,
                                                           'bold': 1,
                                                           'bottom': 1,
                                                           'align': 'left',
                                                           'italic': False,
                                                           'valign': 'vcenter',
                                                           'text_wrap': True
                                                           })
            style_cell_border = workbook.add_format({'font': 'Wheelbarrow',
                                                     'font_size': 8,
                                                     'bold': 1,
                                                     'border': 1,
                                                     'align': 'left',
                                                     'italic': False,
                                                     'valign': 'vcenter',
                                                     'text_wrap': True,
                                                     'bg_color': '#dcdde1',
                                                     })
            style_cell_bottom_text = workbook.add_format({'font': 'Wheelbarrow',
                                                          'font_size': 8,
                                                          'bold': 1,
                                                          'bottom': 1,
                                                          'align': 'left',
                                                          'valign': 'vcenter',
                                                          'text_wrap': True
                                                          })
            style_cell_right_date = workbook.add_format({'font': 'Wheelbarrow',
                                                         'font_size': 8,
                                                         'bold': 1,
                                                         'bottom': 1,
                                                         'align': 'right',
                                                         'valign': 'vcenter',
                                                         'text_wrap': True
                                                         })
            style_text = workbook.add_format({'font': 'Wheelbarrow',
                                              'font_size': 8,
                                              'bold': 1,
                                              'align': 'left',
                                              'valign': 'vcenter',
                                              'text_wrap': True
                                              })
            style_top_text = workbook.add_format({'font': 'Wheelbarrow',
                                                  'font_size': 8,
                                                  'bold': 1,
                                                  'top': 1,
                                                  'align': 'left',
                                                  'valign': 'vcenter',
                                                  'text_wrap': True
                                                  })
            style_right_text = workbook.add_format({'font': 'Wheelbarrow',
                                                    'font_size': 8,
                                                    'bold': 1,
                                                    'right': 1,
                                                    'top': 1,
                                                    'align': 'left',
                                                    'valign': 'vcenter',
                                                    'text_wrap': True
                                                    })
            style_text2 = workbook.add_format({'font': 'Wheelbarrow',
                                               'font_size': 8,
                                               'bold': 0,
                                               'align': 'left',
                                               'valign': 'vcenter',
                                               'text_wrap': True
                                               })
            style_border = workbook.add_format({'font': 'Wheelbarrow',
                                                'font_size': 8,
                                                'bold': 0,
                                                'border': 1,
                                                'align': 'left',
                                                'valign': 'vcenter',
                                                'text_wrap': True
                                                })
            style_aux_border = workbook.add_format({'font': 'Wheelbarrow',
                                                    'font_size': 8,
                                                    'bold': 0,
                                                    'border': 1,
                                                    'align': 'top',
                                                    'text_wrap': True
                                                    })
            style_cell_title.set_text_wrap()

            img_data = base64.b64decode(ot.company_id.logo)
            image = io.BytesIO(img_data)

            cell_width = 300.0
            image_width = 22000.0
            cols_wide = 90.0
            scale = cell_width * cols_wide / image_width
            sheet.insert_image('A1', 'logo.png', {'image_data': image, 'x_scale': scale, 'y_scale': scale})
            row = 0
            sheet.set_row(row, 20)
            sheet.merge_range(row, 0, row + 1, 9, ot.company_id.name, style_cell_title)
            row += 2
            sheet.set_row(row, 30)
            sheet.merge_range(row, 0, row, 9, "ORDEN DE TRABAJO", style_title_ot)
            row += 2
            sheet.write(row, 0, 'TIPO ORDEN:', style1_top_4)
            sheet.merge_range(row, 1, row, 4, ot.type_ot.name.upper(), style_top_text)
            sheet.merge_range(row, 5, row, 6, 'TIPO DE MANTENIMIENTO:', style_top_line)
            sheet.merge_range(row, 7, row, 9, 'CORRECTIVO' if ot.maintenance_type == 'corrective' else 'PREVENTIVO',
                              style_right_text)
            row += 1
            sheet.write(row, 0, 'ESTADO:', style_cell_bottom_title)
            sheet.merge_range(row, 1, row, 9, ot.stage_id.name.upper(), style_cell_bottom_text)
            row += 2

            sheet.write(row, 0, 'NÚMERO OT:', style_cell_bottom_title)
            sheet.merge_range(row, 1, row, 2, ot.name_seq, style_cell_bottom_text)
            sheet.merge_range(row, 3, row, 4, 'FECHA DE CREACIÓN:', style_cell_right_date)
            sheet.write(row, 5, ot.datetime_create_ot.strftime('%d-%m-%y'), style_cell_bottom_text)
            sheet.merge_range(row, 6, row, 7, 'HORA CREACIÓN:', style_cell_right_date)
            sheet.merge_range(row, 8, row, 9, ot.datetime_create_ot.strftime('%H:%M:%S'), style_cell_bottom_text)

            row += 2

            sheet.write(row, 0, 'PLACA:', style_title_form_general)
            sheet.write(row, 1, ot.equipment_id.vehicle_id.license_plate or '', style_text)
            sheet.write(row, 2, 'MODELO:', style_title_form_general)
            sheet.write(row, 3, ot.equipment_id.vehicle_id.model_id.name or '', style_text)
            sheet.write(row, 4, 'MÓVIL:', style_title_form_general)
            sheet.write(row, 5, ot.equipment_id.name or '', style_text)
            sheet.write(row, 6, 'KILOMETRAJE:', style_title_form_general)
            sheet.write(row, 7, ot.equipment_id.vehicle_id.odometer or '', style_text)

            row += 1

            sheet.write(row, 0, 'FECHA SOLICITUD:', style_title_form_general)
            sheet.write(row, 1, ot.request_date.strftime('%d-%m-%y') if ot.request_date else '', style_text)

            row += 2
            sheet.merge_range(row, 0, row, 1, 'DESCRIPCIÓN:', style_title_form_general)
            sheet.merge_range(row, 2, row, 9, ot.name.upper() if ot.name else '', style_text2)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'EMISOR:', style_title_form_general)
            sheet.merge_range(row, 2, row, 9, ot.employee_id.name.upper() if ot.employee_id else '', style_text2)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'SUPERVISOR MTTO ASIGNADO:', style_title_form_general)
            sheet.merge_range(row, 2, row, 9, ot.user_id.name.upper() if ot.user_id else '', style_text2)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'EMPRESA EXTERNA:', style_title_form_general)
            sheet.merge_range(row, 2, row, 9, '', style_text2)
            row += 1
            sheet.set_row(row, 40)
            sheet.merge_range(row, 0, row, 1, 'DIAGNÓSTICO:', style_title_form_general)
            sheet.merge_range(row, 2, row, 9, ot.description.strip().upper() if ot.description else '',
                              style_aux_border)
            row += 2
            sheet.set_row(row, 30)
            sheet.merge_range(row, 0, row, 9,
                              f"{'.' * 50} DETALLE DE ACTIVIDADES A EJECUTAR{'.' * 50}", style_title_form_general)
            row += 1
            for task in ot.task_ids:
                sheet.merge_range(row, 0, row, 1, 'CÓDIGO ESPECIALIDAD', style_cell_border)

                sheet.merge_range(row, 2, row, 9,
                                  ', '.join(map(str, task.activity_speciality_ids.mapped('name'))).upper(),
                                  style_border)
                row += 1
                sheet.merge_range(row, 0, row, 1, 'CÓDIGO DESCRIPCIÓN DE LA ACTIVIDAD', style_cell_border)
                sheet.merge_range(row, 2, row, 9, task.activity_id.name.upper() if task.activity_id else '',
                                  style_border)
                row += 1
                aux_description = ''
                if task.description:
                    aux_description = self.env['ir.fields.converter'].text_from_html(task.description)
                sheet.merge_range(row, 0, row, 1, 'CÓDIGO DESCRIPCIÓN', style_cell_border)
                sheet.merge_range(row, 2, row, 9, aux_description.upper() if aux_description else '', style_border)

                row += 1

                header_titles_1 = ['CORRELATIVO', 'CC']
                sheet.merge_range(row, 2, row, 3, 'NOMBRE', style_cell_border)
                header_titles_2 = ['SISTEMA', 'SUBSISTEMA', 'COMPONENTE', 'F INICIO', 'F TERMINACIÓN',
                                   'ACTIVIDADES EJECUTADAS']
                sheet.write_row(row, 0, header_titles_1, style_cell_border)
                sheet.write_row(row, 4, header_titles_2, style_cell_border)

                row += 1
                sheet.set_row(row, len(task.timesheet_ids) * 15)
                sheet.write_row(row, 0, [task.name_seq, task.employee_id.identification_id or ''], style_aux_border)
                sheet.merge_range(row, 2, row, 3, task.employee_id.name.upper() if task.employee_id else '',
                                  style_aux_border)
                sheet.write_row(row, 4, self._get_aux_data(task), style_aux_border)

                row += 3

    def _get_aux_data(self, task):
        data = []
        # SISTEMA
        system = ''
        for sis in task.activity_id.system_class_id.parent_ids:
            system += f"{sis.parent_id.name.upper() if sis.parent_id else ''}\n"
        data.append(system)

        # SUBSISTEMA
        subsystem = ''
        for sis in task.activity_id.system_class_id.parent_ids:
            subsystem += f"{sis.name.upper() if sis.name else ''}\n"
        data.append(subsystem)

        # COMPONENTE
        if task.activity_id.system_class_id and task.activity_id.system_class_id.name:
            data.append(task.activity_id.system_class_id.name.upper() if task.activity_id.system_class_id else '')
        else:
            data.append('')

        # F INICIO
        date_start = ''
        for ts_line in task.timesheet_ids:
            date_start += f"{ts_line.datetime_start.strftime('%d-%m-%y') if ts_line.datetime_start else ''}\n"
        data.append(date_start)

        # F TERMINACIÓN
        date_end = ''
        for ts_line in task.timesheet_ids:
            date_end += f"{ts_line.datetime_create_line.strftime('%d-%m-%y') if ts_line.datetime_create_line else ''}\n"
        data.append(date_end)

        # ACTIVIDADES EJECUTADAS
        tt = ''
        for ts_line in task.timesheet_ids:
            tt += f"{ts_line.name.upper() if ts_line.name else ''}\n"
        data.append(tt)

        return data
