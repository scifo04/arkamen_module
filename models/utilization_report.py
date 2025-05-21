from odoo import models, fields, api
from odoo.exceptions import ValidationError

class UtilizationReportInternal(models.TransientModel):
    _name = 'arkamen.utilization.report.internal'
    _description = 'Laporan Utilisasi SDM Internal'

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
                    'skill_level': skill_level_label,
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
        }
        
        return action_internal
    
class UtilizationReportExternal(models.TransientModel):
    _name = 'arkamen.utilization.report.external'
    _description = 'Laporan Utilisasi SDM Eksternal'

    start_date = fields.Date(string="Tanggal Mulai", required=True, default=fields.Date.today)
    end_date = fields.Date(string="Tanggal Selesai", required=True, default=fields.Date.today)
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("Tanggal mulai harus lebih awal daripada tanggal selesai.")
    
    def action_generate_report(self):
        self.env['arkamen.utilization.report.external.line'].search([]).unlink()
        
        allocations = self.env['arkamen.allocate'].search([
            ('start_date', '<=', self.end_date),
            ('end_date', '>=', self.start_date)
        ])
        
        for allocation in allocations:
            project = allocation.project
            vendor = self.env['arkamen.vendor'].search([('project', '=', project.id)], limit=1)
            vendor_name = vendor.vendor_name if vendor else ''
            
            for user in allocation.external_user:
                self.env['arkamen.utilization.report.external.line'].create({
                    'report_id': self.id,
                    'employee_name': user.full_name,
                    'tariff': user.tariff,
                    'work_review': user.work_review_ids,
                    'project': project.project_name,
                    'vendor': vendor_name,
                    'start_date': allocation.start_date,
                    'end_date': allocation.end_date,
                    'allocation_percentage': allocation.allocation_percentage,
                })
        
        action_external = {
            'name': 'Data Utilisasi Karyawan Ektsernal',
            'type': 'ir.actions.act_window',
            'res_model': 'arkamen.utilization.report.external.line',
            'view_mode': 'list',
            'domain': [('report_id', '=', self.id)],
        }
        
        return action_external
    
class UtilizationReportInternalLine(models.TransientModel):
    _name = 'arkamen.utilization.report.internal.line'
    _description = 'Baris Laporan Utilisasi Karyawan Internal'
    
    report_id = fields.Many2one('arkamen.utilization.report.internal', string="Report")
    employee_name = fields.Char(string="Nama Karyawan")
    skill_level = fields.Char(string="Skill Level")
    project = fields.Char(string="Proyek yang Dikerjakan")
    vendor = fields.Char(string="Vendor Proyek")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    allocation_percentage = fields.Integer(string="Allocation Percentage (%)")

class UtilizationReportExternalLine(models.TransientModel):
    _name = 'arkamen.utilization.report.external.line'
    _description = 'Baris Laporan Utilisasi Karyawan Eksternal'
    
    report_id = fields.Many2one('arkamen.utilization.report.external', string="Report")
    employee_name = fields.Char(string="Nama Karyawan")
    tariff = fields.Integer(string="Tariff")
    project = fields.Char(string="Proyek yang Dikerjakan")
    work_review = fields.Char(string="Work Review")
    vendor = fields.Char(string="Vendor Proyek")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    allocation_percentage = fields.Integer(string="Allocation Percentage (%)")