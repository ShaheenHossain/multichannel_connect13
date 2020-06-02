# -*- coding: utf-8 -*-

from odoo import fields ,models, api, _


ActionOn = (
	('variant','Variant'),
	('template','Template'),
	('product','Product'),
	('tag','Tag'),
	('category','Category'),
	('order','Order'),
	('customer','Customer'),
	('shipping','Shipping'),
	('attribute','Attribute'),
	('attribute_value','Attribute Value'),
)
ActionType = (
	('import','Import'),
	('export','Export')
)
Status = (
	('error','Error'),
	('success','Success')
)


class ChannelSynchronization(models.Model):
	_name="channel.synchronization"
	_rec_name="action_on"
	_inherit = ['channel.mappings']


	status = fields.Selection(
		selection = Status,
		string='Status',
		required=True
	)
	action_on =  fields.Selection(
		selection = ActionOn,
		string='Action On',
		required=True
	)
	ecomstore_refrence = fields.Char(
		string = 'Store ID'
	)
	odoo_id = fields.Text(
		string = 'Odoo ID'
	)
	action_type = fields.Selection(
		selection = ActionType,
		string='Action Type'
	)
	summary = fields.Text(
		string = 'Summary',
		required=True
	)
	@api.model
	def cron_clear_history(self):
		for rec in self.search([('status','=','success')]):
			rec.unlink()
