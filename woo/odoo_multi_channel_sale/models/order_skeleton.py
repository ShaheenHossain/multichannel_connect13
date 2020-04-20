# -*- coding: utf-8 -*-
from odoo import fields , models,api
class ChannelOrderMappings(models.Model):
	_name="channel.order.mappings"
	_inherit = ['channel.mappings']
	odoo_order_id = fields.Integer(string='Odoo Order ID',required=True)
	order_name = fields.Many2one('sale.order',string='Odoo Order')
	odoo_partner_id = fields.Many2one(related='order_name.partner_id')
	store_order_id =  fields.Char('Store Order ID',required=True)
	@api.multi
	def unlink(self):
		for record in self:
			match = record.store_order_id and record.channel_id.match_order_feeds(record.store_order_id)
			if match: match.unlink()
		res = super(ChannelOrderMappings, self).unlink()
		return  res



	@api.onchange('order_name')
	def change_odoo_id(self):
		self.odoo_order_id = self.order_name.id

	def _compute_name(self):
		for record in self:
			if record.order_name:
				record.name = record.order_name.name
			else:
				record.name = 'Deleted'
