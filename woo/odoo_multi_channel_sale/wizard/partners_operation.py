# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
class ImportPartners(models.TransientModel):

    _inherit = ['import.operation']
    _name = "import.partners"
    partner_ids = fields.Text(string='Partners ID(s)')

class ExportPartners(models.TransientModel):
    _inherit = ['export.operation']
    _name = "export.partners"

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )
