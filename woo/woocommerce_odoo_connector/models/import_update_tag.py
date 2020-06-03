from odoo import api,fields,models
from odoo.tools.translate import _
from odoo.exceptions import UserError




class MultiChannelSale(models.Model):
    _inherit = "multi.channel.sale"

    @api.multi
    def import_all_tags(self):
        message=''
        woocommerce = self.get_woocommerce_connection()
        tags = self.env['tags.feed']
        tags_list=[]
        tag_map_data = self.env['channel.tag.mappings']

        count = 0
        try:
            i = 1
            while (i):
                url = 'products/tags?page=' + str(i)
                tag_data=woocommerce.get(url).json()
                if 'errors' in tag_data:
                    raise UserError(_("Error : " + str(tag_data['errors'][0]['message'])))
                else:
                    if tag_data:
                        i = i + 1
                        for tag in tag_data:
                            if not tag_map_data.search([('store_tag_id','=',tag['id']),('channel_id.id','=',self.id)]) and not tags.search([('store_id','=',tag['id']),('channel_id.id','=',self.id)]):
                                count+=1
                                tag_feed={
                                    'name':tag['name'],
                                    'store_id':tag['id'],
                                    'channel_id': self.id,
                                }
                                tag_rec=tags.create(tag_feed)
                                self._cr.commit()
                                tags_list.append(tag_rec)
                    else:
                        i = 0
            feed_res = dict(create_ids=tags_list, update_ids=[])
            self.env['channel.operation'].post_feed_import_process(self, feed_res)
            message += str(count) + " Tags(s) Imported!"
            return self.display_message(message)

        except Exception as e:
            raise UserError(_("Error : " + str(e)))
