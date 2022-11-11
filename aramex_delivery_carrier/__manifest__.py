# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Aramex Shipping Integration",
  "summary"              :  """Integrate Aramex delivery services with Odoo. Use Aramex to deliver Odoo website and backend orders for both domestic and international orders.""",
  "category"             :  "Website",
  "version"              :  "1.1.2",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Aramex-Shipping-Integration.html",
  "description"          :  """Odoo Aramex Shipping Integration
Deliver orders Odoo
Aramex shipping
Ship orders
National delivery
International shipping
Domestic shipping
Domestic delivery
Shipping prices Odoo
Aramex integration Odoo
Odoo Aramex
Aramex integrate
Use Aramex
Aramex shipping carrier
Aramex delivery Odoo
Odoo Shipping integration
Integration shipping carrier in Odoo
Odoo delivery integration
Odoo delivery methods
Delivery carrier tracking
Shipping modules odoo
Deliveries
Manage order delivery
shipping methods odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/demo_feedback?module=aramex_delivery_carrier",
  "depends"              :  [
                             'odoo_shipping_service_apps',
                             'website_sale_delivery',
                            ],
  "data"                 :  [
                             'views/aramex_delivery_carrier.xml',
                             'data/data.xml',
                             'data/delivery_demo.xml',
                             'security/ir.model.access.csv',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies": {'python': ['suds-py3']}
}
