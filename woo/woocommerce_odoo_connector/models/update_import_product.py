#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import api,fields,models
from odoo.tools.translate import _
from datetime import datetime,timedelta
from custom.woocommerce_v11.woo.odoo_multi_channel_sale.tools import extract_list as EL
from odoo.exceptions import UserError
import logging
import re
remove_tag = re.compile(r'<[^>]+>')
_logger	 = logging.getLogger(__name__)
try:
	from woocommerce import API
except ImportError:
	_logger.info('**Please Install Woocommerce Python Api=>(cmd: pip3 install woocommerce)')


class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.model
	def wk_change_product_qty(self, product_id, qty_available, location_id):
		if qty_available and product_id.type == 'product':
			location_id = location_id and location_id or self.env.ref(
				'stock.stock_location_stock')
			inventory_wizard = self.env['stock.change.product.qty'].create({
				'product_id': product_id.id,
				'new_quantity': (qty_available),
				'location_id': location_id.id,
			})
			inventory_wizard.change_product_qty()


	@api.multi
	def update_woocommerce_products(self, woocommerce=False):
		update_rec = []
		categ = ''
		count = 0
		self.import_woocommerce_attribute()
		self.import_woocommerce_categories()
		if not woocommerce:
			woocommerce = self.get_woocommerce_connection()
		product_tmpl = self.env['product.feed']
		records = self.env['channel.template.mappings'].search([('channel_id.id','=',self.id)])
		id_string = []
		idstr =''
		i=0
		for record in records:
			idstr+=str(record.store_product_id)+','
			i +=1
			if i==10:
				id_string.append(idstr)
				i=0
				idstr=''
		if idstr not in id_string:
			id_string.append(idstr)
		for id_str in id_string:
			try:
				product_data = woocommerce.get('products?include='+id_str).json()
			except Exception as e:
				raise UserError(_("Error : "+str(e)))
			if 'message' in product_data:
				raise UserError(_("Error : "+str(product_data['message'])))
			else :
				for product in product_data:
					_logger.info("========test===2===========>%r",[product['id']])
					variants = []
					update_record = product_tmpl.search([('store_id','=',product['id']),('channel_id.id','=',self.id)])
					if update_record:
						count += 1
						update_record.state = 'update'
						# if product['downloadable'] == True or product['virtual'] == True:
						# 	continue
						if product['type'] == 'variable':
							update_record.write({'feed_variants':[(5,),]})
							variants = self.create_woocommerce_variants(woocommerce,product['id'],product['variations'])
						for category in product['categories']:
							category_id = self.env['category.feed'].search([('name','=',category['name']),('channel_id.id','=',self.id)], limit=1)
							if category_id:
								# categ = categ+str(category_id.store_id)+","
								categ = str(category_id.store_id)
						try:
							product['price']=float(product['price'])
						except:
							pass
						product_feed_dict = {'name'					: product['name'],
											'store_id'				: product['id'],
											'default_code'  		: product['sku'],
											'list_price'			: product['price'],
											'channel_id'			: self.id,
											'description_sale'		: remove_tag.sub('',product['description']),
											'qty_available'		: product['stock_quantity'],
											'feed_variants' 		: variants,
											'image_url'				: product['images'][0]['src'],
											'extra_categ_ids'		: categ,
											'weight'				: product['weight'],
											# 'weight_unit'			: 'kg',
											'length'				: product['dimensions']['length'],
											'width'					: product['dimensions']['width'],
											'height'				: product['dimensions']['height'] ,
											# 'dimension_unit'		: product['dimensions']['unit'] ,
											}
						update_record.write(product_feed_dict)
						self._cr.commit()
						update_rec.append(update_record)
					else:
						if product['downloadable'] == True or product['virtual'] == True:
							product_feed_dict['type'] = 'service'
						if product['type'] == 'variable':
							variants = self.create_woocommerce_variants(woocommerce,product['id'],product['variations'])
						count = count + 1
						for category in product['categories']:
							category_id = self.env['category.feed'].search([('name','=',category['name']),('channel_id.id','=',self.id)])
							if category_id:
								# categ = categ+str(category_id.store_id)+","
								categ = str(category_id.store_id)
						try:
							product['price']=float(product['price'])
						except:
							pass
						product_feed_dict = {'name'				: product['name'],
										'store_id'				: product['id'],
										'default_code'  		: product['sku'],
										'list_price'			: product['price'],
										# 'list_price'			: float(product['regular_price']),
										'channel_id'			: self.id,
										'description_sale'		: remove_tag.sub('',product['description']),
										'qty_available'		: product['stock_quantity'],
										'feed_variants' 		: variants,
										'image_url'				: product['images'][0]['src'],
										'extra_categ_ids'		: categ,
										'ecom_store'			: 'woocommerce',
										'weight'				: product['weight'],
										# 'weight_unit'			: 'kg',
										'length'				: product['dimensions']['length'],
										'width'					: product['dimensions']['width'],
										'height'				: product['dimensions']['height'],
										# 'dimension_unit'		: product['dimensions']['unit'],
										}
						product_rec = product_tmpl.create(product_feed_dict)
						product_rec.state = 'update'
						self._cr.commit()
						update_rec.append(product_rec)
		feed_res = dict(create_ids=[],update_ids=update_rec)
		self.env['channel.operation'].post_feed_import_process(self,feed_res)
		self.update_product_date = str(datetime.now())
		message = str(count)+" Product(s) Updated!  "
		return self.display_message(message)

	def import_stock(self,product_template,product_mapping):
		count=0
		woocommerce = self.get_woocommerce_connection()

		try:
			store_id = product_mapping.store_product_id
			product_data = woocommerce.get('products?include='+str(store_id)).json()
			if 'errors' in product_data:
				raise UserError(_("Error : " + str(product_data['errors'][0]['message'])))
			else:
				if product_data:
					for product in product_data:
						product_feed=self.env['product.feed'].search([('store_id','=',store_id)])
						if product['id'] == int(store_id):
							count+=1
							location_id=self.location_id
							product_id=product_template
							qty_available=product['stock_quantity']
							self.wk_change_product_qty(product_id, qty_available, location_id)
							product_feed_dict={
								'qty_available':qty_available
							}
							product_feed.update(product_feed_dict)
		except Exception as e:
			raise UserError(_("Error : " + str(e)))
		return count


	@api.multi
	def import_stocks(self):
		product_template=self.env['product.template'].search([])
		# active_model = self._context.get('active_model')
		count = 0
		for product in product_template:
			product_mappings = self.env['channel.template.mappings'].search(
				[('template_name', '=', product.id), ('channel_id.id', '=', self.id)])
			if product_mappings:
				count+=self.import_stock(product,product_mappings)
		message = str(count) + " Product(s) Stock Imported!"
		return self.display_message(message)