from odoo import api,fields,models
from odoo.tools.translate import _
from datetime import datetime,timedelta
from odoo.exceptions import UserError
from urllib import parse as urlparse
import os
import base64
import logging


class MultiChannelSale(models.Model):
    _inherit = "multi.channel.sale"

    @api.multi
    def update_all_orders(self):
        woocommerce = self.get_woocommerce_connection()
        # self.export_woocommerce_product()
        order_records = self.env['sale.order'].search([])
        count=0
        # update_order_rec=self.env['order.feed'].search([('')])
        for order in order_records:
            order_mapping=self.env['channel.order.mappings'].search([('order_name','=',order.id),('channel_id.id','=',self.id)])
            if order_mapping:
                store_id = order_mapping.store_order_id
                if order.state in('cancel'):
                    count+=1
                    order_dict={
                        'status':'cancelled'
                    }
                # if order.state in('draft'):
                #     count += 1
                #     order_dict = {
                #         'status': 'failed'
                #     }
                try:
                    return_dict = woocommerce.put("orders/" + str(store_id), order_dict).json()

                    if 'message' in return_dict:
                        raise UserError(_("Can't update order , " + str(return_dict['message'])))
                except Exception as e:
                    raise UserError(_("Can't update order , " + str(e)))
        message = str(count) + " Order(s) Updated!"
        return self.display_message(message)





