#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import api,fields,models
from odoo.tools.translate import _
from datetime import datetime,timedelta
from odoo.exceptions import UserError
import logging
_logger	 = logging.getLogger(__name__)
try:
	from woocommerce import API
except ImportError:
	_logger.info('**Please Install Woocommerce Python Api=>(cmd: pip3 install woocommerce)')
class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def import_woocommerce_customers(self):
		message = ''
		list_customer = []
		count = 0
		woocommerce = self.get_woocommerce_connection()
		partner_feed_data = self.env['partner.feed']
		date = self.with_context({'name':'customer'}).get_woocommerce_import_date()
		if not date:
			return self.display_message("Please set date in multi channel configuration")
		try:
			partner_data = woocommerce.get('customers?after='+date).json()
		except Exception as e:
			raise UserError(_("Error : "+str(e)))
		if 'message' in partner_data:
			raise UserError(_("Error : "+str(partner_data['message'])))
		else :
			for partner in partner_data:
				if not partner_feed_data.search([('store_id','=',partner['id']),('channel_id.id','=',self.id)]):
					count = count +1
					partner_dict = {
								'name'		: partner['first_name'],
								'last_name'	: partner['last_name'],
								'channel_id': self.id,
								'email'		: partner['email'],
								'store_id'	: partner['id'],
					}
					partner_rec = partner_feed_data.create(partner_dict)
					self._cr.commit()
					list_customer.append(partner_rec)
			feed_res = dict(create_ids = list_customer,update_ids = [])
			self.env['channel.operation'].post_feed_import_process(self, feed_res)
			self.import_customer_date = str(datetime.now().date())
			message +=  str(count)+" Customer(s) Imported!"
			return self.display_message(message)


	@api.multi
	def import_all_woocommerce_customers(self):
		message = ''
		list_customer = []
		count = 0
		woocommerce = self.get_woocommerce_connection()
		if isinstance(woocommerce, dict):raise UserError("Could not connect with Woocommerce API!")
		# self.import_woocommerce_categories()
		pagination_info = self.pagination_info
		limit = self.api_record_limit
		if not pagination_info:
			pagination_info = {}
		else:
			pagination_info = eval(pagination_info)
		partner_feed_data = self.env['partner.feed']
		_logger.info("=====pagination _info %r",(pagination_info))
		try:
			i=pagination_info.get("import_partner_last_page",1)
			while(i):
				url = 'customers'
				# url = 'customers?page='+str(i)
				# if limit:
				# 	url += '&per_page=%s'%(limit)
				# partner_data = woocommerce.get(url)
				partner_data = woocommerce.get(url).json()
				if 'message' in partner_data:
					raise UserError(_("Error : "+str(partner_data['message'])))
				else :
					if partner_data:
						i=i+1
						list_customer = []
						for partner in partner_data:
							if not partner_feed_data.search([('store_id','=',partner['id']),('channel_id.id','=',self.id)]):
								count = count +1
								partner_dict = {
											'name'		: partner['first_name'],
											'last_name'	: partner['last_name'],
											'channel_id': self.id,
											'email'		: partner['email'],
											'store_id'	: partner['id'],
								}
								partner_rec = partner_feed_data.create(partner_dict)
								self._cr.commit()
								list_customer.append(partner_rec)
						_logger.info("=====pagination _info %r",(pagination_info))
						if limit:
							feed_res = dict(create_ids=list_customer,update_ids=[])
							res=self.env['channel.operation'].post_feed_import_process(self,feed_res)
							_logger.info("=====feed eval res%r",res)

						pagination_info["import_partner_last_page"] = i
						self.write({
							"pagination_info":pagination_info
						})
						_logger.info("=====write pagination_info%r",self.pagination_info)

						self._cr.commit()
					else:
						i=0
						pagination_info["import_partner_last_page"] = 1
						self.write({
							"pagination_info":pagination_info
						})
						_logger.info("=====write pagination_info when i==0%r",self.pagination_info)

						self._cr.commit()
			# feed_res = dict(create_ids = list_customer,update_ids = [])
			# self.env['channel.operation'].post_feed_import_process(self, feed_res)
			# self.import_customer_date = str(datetime.now().date())
			message +=  str(count)+" Customer(s) Imported!"
			return self.display_message(message)
		except Exception as e:
			raise UserError(_("Error : "+str(e)))