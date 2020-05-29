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

    order_cancel_check=fields.Binary(help="To check whether the order is cancelled or not", default=False)
    order_refund_check=fields.Binary(help="To check whether the order is cancelled or not", default=False)
    order_complete_check=fields.Binary(help="To check whether the order is cancelled or not", default=False)
    order_cancel=fields.Binary(help="To check whether the order is cancelled or not", default=False)
    order_refund=fields.Binary(help="To check whether the order is cancelled or not", default=False)

    def cancel_order(self,order,order_mapping,woocommerce):
        count=0
        invoice_id = self.env['account.invoice'].search([('origin', '=', order.name), ('type', '=', 'out_invoice')],limit=1)
        if order_mapping:
            store_id = order_mapping.store_order_id

            if order.state in ('cancel'):
                if invoice_id:
                    refund = self.env['account.invoice'].search(
                        [('origin', '=', invoice_id.number), ('type', '=', 'out_refund')], limit=1)
                    inv_tot_amt = invoice_id.amount_total
                    inv_due_amt = invoice_id.residual
                    if refund:
                        ref_tot_amt = refund.amount_total
                        ref_due_amt = refund.residual

                        if ref_tot_amt == inv_tot_amt and inv_due_amt == 0.0:
                            self.order_cancel_check = True
                elif not invoice_id:
                    self.order_cancel_check = True

                if self.order_cancel_check == True:
                    count += 1
                    order_dict = {
                        'status': 'cancelled'
                    }

                    order_feed = self.env['order.feed'].search([('store_id', '=', store_id)])
                    order_feed.update({
                        'order_state': "cancelled"
                    })
                    try:
                        return_dict = woocommerce.put("orders/" + str(store_id), order_dict).json()
                        order.channel_mapping_ids.need_sync = 'no'
                        if 'message' in return_dict:
                            raise UserError(_("Can't update order , " + str(return_dict['message'])))
                    except Exception as e:
                        raise UserError(_("Can't update order , " + str(e)))
        return count

    def refund_order(self,order,order_mapping,woocommerce):
        count=0
        invoice_id = self.env['account.invoice'].search([('origin', '=', order.name), ('type', '=', 'out_invoice')],
                                                        limit=1)
        if order_mapping:
            store_id = order_mapping.store_order_id

            if order.state in ('cancel'):
                if invoice_id:
                    refund = self.env['account.invoice'].search(
                        [('origin', '=', invoice_id.number), ('type', '=', 'out_refund')], limit=1)
                    inv_tot_amt = invoice_id.amount_total
                    inv_due_amt = invoice_id.residual
                    # inv_prod_count = invoice_id.quantity
                    if refund:
                        ref_tot_amt = refund.amount_total
                        date_created = str(refund.date_invoice)
                        reason = refund.name

                        if ref_tot_amt == inv_tot_amt and inv_due_amt == 0.0:
                            self.order_refund_check = True
                elif not invoice_id:
                    self.order_refund_check = True

                if self.order_refund_check == True:
                    count += 1
                    order_refund = {
                        'amount': str(ref_tot_amt),
                        'status': 'refunded',
                        'date_created': date_created,
                        'reason': reason
                    }
                    payment_data={
                        "enabled": True,
                    }


                    order_feed = self.env['order.feed'].search([('store_id', '=', store_id)])
                    order_feed.update({
                        'order_state': "refunded"
                    })
                    try:
                        # payment = woocommerce.put("payment_gateways/bacs", payment_data).json()
                        # if 'id' in payment:
                        #     order_data = {
                        #         'payment_method':payment['id'],
                        #         'payment_method_title':payment['method_title']
                        #     }
                        #     order_dict = woocommerce.put("orders/" + str(store_id), order_data).json()
                        return_dict = woocommerce.post("orders/" + str(store_id)+"/refunds", order_refund).json()
                        order.channel_mapping_ids.need_sync = 'no'
                        if 'message' in return_dict:
                            raise UserError(_("Can't update order , " + str(return_dict['message'])))
                    except Exception as e:
                        raise UserError(_("Can't update order , " + str(e)))
        return count

    def update_order_status(self,order,order_mapping,woocommerce):
        deliveries=self.env['stock.picking'].search([('origin','=',order.name)])
        count=0
        if order_mapping:
            store_id = order_mapping.store_order_id
            order_feed = self.env['order.feed'].search([('store_id', '=', store_id)])
            if order_feed.order_state!="completed":
                if order.state in ('sale'):
                    for delivery in deliveries:
                        if delivery.state in ('done') and order.order_line.product_uom_qty == delivery.move_lines.quantity_done:
                            self.order_complete_check=True

                if self.order_complete_check==True:
                    count += 1
                    order_dict = {
                        'status': 'completed'
                    }

                    order_feed.update({
                        'order_state': "completed"
                    })
                    try:
                        return_dict = woocommerce.put("orders/" + str(store_id), order_dict).json()
                        if 'message' in return_dict:
                            raise UserError(_("Can't update order status, " + str(return_dict['message'])))
                    except Exception as e:
                        raise UserError(_("Can't update order status, " + str(e)))
        return count



    @api.multi
    def cancel_orders(self):
        woocommerce = self.get_woocommerce_connection()
        # self.export_woocommerce_product()
        order_records = self.env['sale.order'].search([])
        active_model = self._context.get('active_model')
        count=0
        # update_order_rec=self.env['order.feed'].search([('')])

        if active_model == 'sale.order':
            active_id = self._context.get('active_id')
            order = self.env['sale.order'].search([('id','=',active_id)])
            order_mapping=self.env['channel.order.mappings'].search([('order_name','=',order.name),('need_sync','=','yes'),('channel_id.id','=',self.id)])
            if order_mapping:
                count=self.cancel_order(order, order_mapping, woocommerce)
            if count==1:
                message =" Order Cancelled!"
            else:
                message =" Order Cancellation Failed!"

            return self.display_message(message)
        else:
            for order in order_records:
                order_mapping=self.env['channel.order.mappings'].search([('order_name','=',order.id),('need_sync','=','yes'),('channel_id.id','=',self.id)])
                if order_mapping:
                    count += self.cancel_order(order, order_mapping, woocommerce)

            message = str(count) + " Order(s) Cancelled!"
            return self.display_message(message)

    @api.multi
    def refund_orders(self):
        woocommerce = self.get_woocommerce_connection()
        order_records = self.env['sale.order'].search([])
        active_model = self._context.get('active_model')
        count=0

        if active_model == 'sale.order':
            active_id = self._context.get('active_id')
            order = self.env['sale.order'].search([('id','=',active_id)])
            order_mapping = self.env['channel.order.mappings'].search(
                [('order_name', '=', order.id), ('channel_id.id', '=', self.id)])
            if order_mapping:
                count = self.refund_order(order, order_mapping, woocommerce)
            if count==1:
                message = " Order Refunded!"
            else:
                message = " Order Refund Failed!"

            return self.display_message(message)
        else:
            for order in order_records:
                order_mapping = self.env['channel.order.mappings'].search(
                    [('order_name', '=', order.id),('channel_id.id', '=', self.id)])
                if order_mapping:
                    count += self.refund_order(order, order_mapping, woocommerce)

            message = str(count) + " Order(s) Refunded!"
            return self.display_message(message)

    @api.multi
    def update_orders_status(self):
        woocommerce = self.get_woocommerce_connection()
        order_records = self.env['sale.order'].search([])
        active_model = self._context.get('active_model')
        count=0
        if active_model == 'sale.order':
            active_id = self._context.get('active_id')
            order = self.env['sale.order'].search([('id', '=', active_id)])
            order_mapping = self.env['channel.order.mappings'].search(
                [('order_name', '=', order.id), ('channel_id.id', '=', self.id)])
            if order_mapping:
                count=self.update_order_status(order, order_mapping, woocommerce)
            if count==1:
                message = " Order Status Updated!"
            else:
                message = " Order Status Update Failed!"

            return self.display_message(message)
        else:
            for order in order_records:
                order_mapping = self.env['channel.order.mappings'].search(
                    [('order_name', '=', order.id), ('channel_id.id', '=', self.id)])
                if order_mapping:
                    count +=self.update_order_status(order, order_mapping, woocommerce)
            message = str(count) + " Order(s) Status Updated!"
            return self.display_message(message)







