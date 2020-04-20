# -*- coding: utf-8 -*-
{
  "name"                 :  "Woocommerce Odoo Connector",
  "summary"              :  "Woocommerce Odoo Connector integrates Odoo with Woocommerce to "
                            "manage your Woocommerce store and orders in Odoo. "
            ,
  "category"             :  "Website",
  "version"              :  "1.0.2",
  "sequence"             :  1,
  "author"               :  "Planet Odoo",
  "license"              :  "Other proprietary",
  "website"              :  "http://www.planet-odoo.com",
  "description"          :  """""",
  "depends"              :  ['odoo_multi_channel_sale'],
  "data"                 :  [
                             'views/woc_config_views.xml',
                             'data/import_cron.xml',
                             'views/inherited_woocommerce_dashboard_view.xml',
                             'wizard/import_update_wizard.xml',
                             'data/default_data.xml',
                             'security/ir.model.access.csv',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "external_dependencies":  {'python': ['woocommerce']},
}