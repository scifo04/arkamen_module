from odoo import models, fields, api
import json

class User(models.Model):
    _name = 'arkamen.user'
    _description = 'Arkamen User Data'

    full_name = fields.Char(string="Nama", required=True)
    contact = fields.Char(string="Contact", required=True)
    skills = fields.Text(string="List of Skills")
    availability = fields.Selection(selection=[
        ('0', 'Available'), ('1', 'Not Available')
    ], string="Availability")
    display_skills = fields.Char(string="Skills (Short)", compute="_compute_display_skills")

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
    cv = fields.Char(string="CV")
    work_review = fields.Char(string="Work Review")