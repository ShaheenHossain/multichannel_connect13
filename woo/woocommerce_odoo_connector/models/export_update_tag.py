from odoo import api,fields,models
from odoo.tools.translate import _
from odoo.exceptions import UserError




class MultiChannelSale(models.Model):
    _inherit = "multi.channel.sale"

    @api.multi
    def export_tags(self):
        mappings=self.env['channel.tag.mappings']
        tag_records=self.env['product.tags'].search([])
        woocommerce = self.get_woocommerce_connection()
        count=0
        message=''
        for record in tag_records:
            tag_mappings=mappings.search([('tag_name.id','=',record.id),('channel_id.id','=',self.id)])
            if not tag_mappings:
                tag_dict={
                    'name':str(record.name)
                }
                return_dict=woocommerce.post("products/tags", tag_dict).json()
                if 'message' in return_dict:
                    raise UserError(_("Can't export tag, " + str(return_dict['message'])))
                else:
                    if return_dict['id']:
                        count+=1
                        mapping_dict = {
                            'channel_id'	: self.id,
                            'store_tag_id'	: return_dict['id'],
                            'tag_name'		: record.id,
                            'operation'             : 'export'
                        }
                        self._create_mapping(mappings, mapping_dict)

        self._cr.commit()
        message += str(count) + " Tags(s) Exported!"
        return self.display_message(message)


