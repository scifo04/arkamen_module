from odoo import models, fields, api
from odoo.exceptions import ValidationError

class UtilizationReport(models.TransientModel):
    _name = 'arkamen.utilization.report'
    _description = 'Laporan Utilisasi SDM'

    start_date = fields.Date(string="Tanggal Mulai", required=True, default=fields.Date.today)
    end_date = fields.Date(string="Tanggal Selesai", required=True, default=fields.Date.today)
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("Tanggal mulai harus lebih awal daripada tanggal selesai.")
    
    def action_generate_report(self):
        self.env['arkamen.utilization.report.internal.line'].search([]).unlink()
        self.env['arkamen.utilization.report.external.line'].search([]).unlink()
        
        allocations = self.env['arkamen.allocate'].search([
            ('start_date', '<=', self.end_date),
            ('end_date', '>=', self.start_date)
        ])
        
        for allocation in allocations:
            project = allocation.project
            vendor = self.env['arkamen.vendor'].search([('project', '=', project.id)], limit=1)
            vendor_name = vendor.vendor_name if vendor else ''
            
            for user in allocation.internal_user:
                skill_level_selection = dict(self.env['arkamen.internaluser']._fields['skill_level'].selection)
                skill_level_label = skill_level_selection.get(user.skill_level, '')
                
                self.env['arkamen.utilization.report.internal.line'].create({
                    'report_id': self.id,
                    'employee_name': user.full_name,
                    'skills': user.display_skills,
                    'skill_level': skill_level_label,
                    'project': project.project_name,
                    'vendor': vendor_name,
                    'start_date': allocation.start_date,
                    'end_date': allocation.end_date,
                    'allocation_percentage': allocation.allocation_percentage,
                })
        
        for allocation in allocations:
            project = allocation.project
            vendor = self.env['arkamen.vendor'].search([('project', '=', project.id)], limit=1)
            vendor_name = vendor.vendor_name if vendor else ''
            
            for user in allocation.external_user:
                self.env['arkamen.utilization.report.external.line'].create({
                    'report_id': self.id,
                    'employee_name': user.full_name,
                    'skills': user.display_skills,
                    'tariff': user.tariff,
                    'project': project.project_name,
                    'vendor': vendor_name,
                    'start_date': allocation.start_date,
                    'end_date': allocation.end_date,
                    'allocation_percentage': allocation.allocation_percentage,
                })
        
        action_internal = {
            'name': 'Data Utilisasi Karyawan Internal',
            'type': 'ir.actions.act_window',
            'res_model': 'arkamen.utilization.report.internal.line',
            'view_mode': 'list',
            'domain': [('report_id', '=', self.id)],
            'target': 'current',
        }
        
        return action_internal
    
class UtilizationReportInternalLine(models.TransientModel):
    _name = 'arkamen.utilization.report.internal.line'
    _description = 'Baris Laporan Utilisasi Karyawan Internal'
    
    report_id = fields.Many2one('arkamen.utilization.report', string="Report")
    employee_name = fields.Char(string="Nama Karyawan")
    skills = fields.Char(string="List of Skills")
    skill_level = fields.Char(string="Skill Level")
    project = fields.Char(string="Proyek yang Dikerjakan")
    vendor = fields.Char(string="Vendor Proyek")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    allocation_percentage = fields.Integer(string="Allocation Percentage (%)")

class UtilizationReportExternalLine(models.TransientModel):
    _name = 'arkamen.utilization.report.external.line'
    _description = 'Baris Laporan Utilisasi Karyawan Eksternal'
    
    report_id = fields.Many2one('arkamen.utilization.report', string="Report")
    employee_name = fields.Char(string="Nama Karyawan")
    skills = fields.Char(string="List of Skills")
    tariff = fields.Integer(string="Tariff")
    project = fields.Char(string="Proyek yang Dikerjakan")
    vendor = fields.Char(string="Vendor Proyek")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    allocation_percentage = fields.Integer(string="Allocation Percentage (%)")