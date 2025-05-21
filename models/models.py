from odoo import models, fields, api
from odoo.exceptions import ValidationError
import json

class User(models.Model):
    _name = 'arkamen.user'
    _description = 'Arkamen User Data'
    @api.constrains('user_id')
    def _check_unique_user(self):
        for record in self:
            existing = self.search([
                ('user_id', '=', record.user_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError("One Account only.")

    full_name = fields.Char(string="Nama", required=True)
    contact = fields.Char(string="Contact", required=True)
    skills = fields.Text(string="List of Skills")
    availability = fields.Selection(selection=[
        ('0', 'Available'), ('1', 'Not Available')
    ], string="Availability")
    display_skills = fields.Char(string="Skills (Short)", compute="_compute_display_skills")
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)

    @api.depends('skills')
    def _compute_display_skills(self):
        for record in self:
            skill_list = record.get_skills_list()
            record.display_skills = ", ".join(skill_list[:3]) + ("..." if len(skill_list) > 3 else "")

    def get_skills_list(self):
        try:
            return json.loads(self.skills or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_skills_list(self, str_list):
        self.skills = json.dumps(str_list)

class InternalUser(models.Model):
    _inherit = 'arkamen.user'
    _name = 'arkamen.internaluser'
    _description = 'Arkamen Internal User Data'

    skill_level = fields.Selection(selection=[
        ('0', 'Beginner'),
        ('1', 'Intermediate'),
        ('2', 'Proficient'),
        ('3', 'Advanced'),
        ('4', 'Expert'),
    ])
    projects = fields.Text(string="Projects")

    def get_projects_list(self):
        try:
            return json.loads(self.projects or '[]')
        except json.JSONDecodeError:
            return []
    
    def set_projects_list(self, str_list):
        self.projects = json.dumps(str_list)

class ExternalUser(models.Model):
    _inherit = 'arkamen.user'
    _name = 'arkamen.externaluser'
    _description = 'Arkamen External User Data'

    tariff = fields.Integer(string="Tariff")

    cv = fields.Binary(string="CV", attachment=True)
    cv_filename = fields.Char(string="CV Filename")
    
    work_review_ids = fields.Many2many(
        'ir.attachment',
        'arkamen_externaluser_attachment_rel',
        'externaluser_id',
        'attachment_id',
        string="Work Reviews"
    )

    cv_status = fields.Char(string="CV", compute="_compute_cv_status", store=True)
    work_review_status = fields.Char(string="Work Reviews", compute="_compute_work_review_status", store=True)

    @api.depends('cv')
    def _compute_cv_status(self):
        for rec in self:
            rec.cv_status = "Available" if rec.cv else "Not Available"

    @api.depends('work_review_ids')
    def _compute_work_review_status(self):
        for rec in self:
            rec.work_review_status = "Available" if rec.work_review_ids else "Not Available"

    @api.constrains('tariff')
    def _check_tariff(self):
        for record in self:
            if record.tariff <= 0:
                raise ValidationError("Tarif karyawan outsource harus berupa integer positif")

class Project(models.Model):
    _name = 'arkamen.project'
    _description = 'Arkamen Project Data'

    project_name = fields.Char(string="Project Name")
    skills = fields.Text(string="Skills for Project")
    duration = fields.Integer(string="Project Duration (in Days)")
    budget = fields.Integer(string="Project Budget")
    description = fields.Char(string="Project Description")

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError("Durasi proyek harus berupa integer positif")

    @api.constrains('budget')
    def _check_budget(self):
        for record in self:
            if record.budget <= 0:
                raise ValidationError("Biaya proyek harus berupa integer positif")

class Vendor(models.Model):
    _name = 'arkamen.vendor'
    _description = 'Arkamen Vendor Data'

    vendor_name = fields.Char(string="Vendor Name")
    address = fields.Char(string="Vendor Address")
    contact = fields.Char(string="Vendor Contact")
    project = fields.Many2one('arkamen.project',string="Project that the Vendor works in")

class AllocateTo(models.Model):
    _name = 'arkamen.allocate'
    _description = 'Arkamen Allocation Data'

    project = fields.Many2one('arkamen.project', string="Project Allocated")
    internal_user = fields.Many2many('arkamen.internaluser',string="Allocate to Internal User")
    external_user = fields.Many2many('arkamen.externaluser',string="Allocate to External User")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    allocation_percentage = fields.Integer(string="Allocation Percentage (%)")

    @api.constrains('allocation_percentage')
    def _check_allocation_percentage(self):
        for record in self:
            if record.allocation_percentage <= 0:
                raise ValidationError("Persentase alokasi karyawan harus berupa integer positif")
            if record.allocation_percentage > 100:
                raise ValidationError("Persentase alokasi karyawan tidak boleh lebih dari 100%.")

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("Tanggal mulai harus lebih awal daripada tanggal selesai.")