# -*- coding: utf-8 -*-
from odoo import fields ,models, api, _

class ChannelCategoryMappings(models.Model):

	_name="channel.category.mappings"
	_inherit = ['channel.mappings']
	_rec_name = "category_name"

	store_category_id =  fields.Char(string='Store Category ID',required=True)
	odoo_category_id = fields.Integer(string='Odoo Category ID',required=True)
	category_name = fields.Many2one('product.category',string='Category')
	leaf_category = fields.Boolean(string='Leaf Category')
	_sql_constraints = [
		('channel_store_store_category_id_uniq',
		'unique(channel_id, store_category_id)',
		'Store category ID must be unique for channel category mapping!'),
		('channel_odoo_category_id_uniq',
		'unique(channel_id, odoo_category_id)',
		'Odoo category ID must be unique for channel category mapping!'),
	]
	@api.multi
	def unlink(self):
		for record in self:
			if record.store_category_id:
				match = record.channel_id.match_category_feeds(record.store_category_id)
				if match: match.unlink()
		res = super(ChannelCategoryMappings, self).unlink()
		return  res

	def _compute_name(self):
		for record in self:
			if record.category_name:
				record.name = record.category_name.name
			else:
				record.name = 'Deleted'

	@api.onchange('category_name')
	def change_odoo_id(self):
		self.odoo_category_id = self.category_name.id
