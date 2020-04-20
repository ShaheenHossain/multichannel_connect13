# -*- coding: utf-8 -*-
from odoo import api,models,fields
import logging
_logger = logging.getLogger(__name__)

class ExportTemplates(models.TransientModel):
    _inherit = 'export.templates'

    @api.multi
    def submit(self):
        message=''
        if self.operation == 'export':
            message = self.channel_id.action_export_woocommerce_products()
        else:
            message = self.channel_id.action_update_woocommerce_products()
        return message
