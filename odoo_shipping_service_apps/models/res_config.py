# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import fields ,models
ComputeWeight = [
    ('volume','Using Volumetric Weight'),
    ('weight','Using Weight')
]
class res_config_settings(models.TransientModel):
	_inherit='res.config.settings'

	module_hermes_delivery_carrier=fields.Boolean(
		string= "Hermes Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_hermes_delivery_carrier'
	)
	module_acs_shipping_integration=fields.Boolean(
		string = "ACS Courier Settings",config_parameter='odoo_shipping_service_apps.default_module_acs_shipping_integration'
	)
	module_apc_shipping_integration=fields.Boolean(
		string = "APC Overnight Settings",config_parameter='odoo_shipping_service_apps.default_module_apc_shipping_integration'
	)
	module_fedex_delivery_carrier=fields.Boolean(
		string = "FedEx Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_fedex_delivery_carrier'
	)
	module_usps_delivery_carrier=fields.Boolean(
		string = "USPS Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_usps_delivery_carrier'
	)
	module_ups_delivery_carrier=fields.Boolean(
		string = "UPS Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_ups_delivery_carrier'
	)
	module_dhl_delivery_carrier=fields.Boolean(
		string = "DHL Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_dhl_delivery_carrier'
	)
	module_auspost_delivery_carrier = fields.Boolean(
		string = "Australia Post Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_auspost_delivery_carrier'
	)
	module_dhl_intraship_delivery_carrier=fields.Boolean(
		string = "DHL Intraship Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_dhl_intraship_delivery_carrier'
	)
	module_aramex_delivery_carrier = fields.Boolean(
		string = "Aramex Shipping Service",config_parameter='odoo_shipping_service_apps.default_module_aramex_delivery_carrier'
	)
	module_canada_post_shipping_integration = fields.Boolean(
		string = "Canada Post Shipping Integration",config_parameter='odoo_shipping_service_apps.default_module_canada_post_shipping_integration'
	)
	
	compute_weight = fields.Selection(
		selection = ComputeWeight,
		default='weight',
		string= 'Compute Weight'
	)