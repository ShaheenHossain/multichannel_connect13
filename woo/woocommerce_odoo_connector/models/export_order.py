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

    refund=fields.Binary(help="To check whether the refund is pending or not for the SO", default=False)
    @api.multi
    def update_all_orders(self):
        woocommerce = self.get_woocommerce_connection()
        # self.export_woocommerce_product()
        order_records = self.env['sale.order'].search([])
        count=0
        # update_order_rec=self.env['order.feed'].search([('')])
        for order in order_records:
            invoice_id=self.env['account.invoice'].search([('origin','=',order.name)])
            order_mapping=self.env['channel.order.mappings'].search([('order_name','=',order.id),('need_sync','=','yes'),('channel_id.id','=',self.id)])
            if order_mapping:
                store_id = order_mapping.store_order_id

                if order.state in('cancel'):
                    if invoice_id:
                        for invoice in invoice_id:
                            if invoice.state in ('cancel'):
                                self.refund=True
                            else:
                                self.refund=False
                    elif not invoice_id:
                        self.refund = True

                    if self.refund==True:
                        count += 1
                        order_dict={
                            'status':'cancelled'
                        }

                        order_feed=self.env['order.feed'].search([('store_id','=',store_id)])
                        order_feed.update({
                            'order_state': "cancelled"
                        })
                        try:
                            return_dict = woocommerce.put("orders/" + str(store_id), order_dict).json()
                            order.channel_mapping_ids.need_sync='no'
                            if 'message' in return_dict:
                                raise UserError(_("Can't update order , " + str(return_dict['message'])))
                        except Exception as e:
                            raise UserError(_("Can't update order , " + str(e)))
        message = str(count) + " Order(s) Updated!"
        return self.display_message(message)





