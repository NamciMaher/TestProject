# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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

from odoo import api, fields , models,_
import base64, binascii
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import Warning ,ValidationError,UserError


class DeliveryCarrier(models.Model):
	_inherit="delivery.carrier"


	delivery_type = fields.Selection(selection_add = [('aramex','Aramex')], ondelete={'aramex': 'set default'})
	aramex_product_group = fields.Many2one(comodel_name = 'aramex.product.group', string = 'Aramex Product Group')
	aramex_product_type = fields.Many2one(comodel_name = 'aramex.product.type', string = 'Aramex Product Type')
	aramex_payment_method = fields.Many2one(comodel_name = 'aramex.payment.method', string = 'Aramex Payment Method')
	aramex_service = fields.Many2one(comodel_name = 'aramex.service',string = 'Aramex Service')
	aramex_sender_multi_ship = fields.Boolean(string = "Create Seperate Shipment for Every Package", required=True, default = 1)
	aramex_consignment_length = fields.Float(string="Consignment Length")
	aramex_consignment_width = fields.Float(string="Consignment Width")
	aramex_consignment_height = fields.Float(string="Consignment Height")

	# @api.onchange('aramex_product_group')
	# def onchange_product_group(self):
	# 	result = {}
	# 	if self.aramex_product_group and self.aramex_product_group.code == "DOM":
	# 		self.aramex_product_type = False
	# 		result['domain'] = {'aramex_product_type': [('id', 'in', self.env["aramex.product.type"].search([("code","=","OND")]).ids)]}
	# 	else :
	# 		self.aramex_product_type = False
	# 		result['domain'] = {'aramex_product_type': [('id', 'in', self.env["aramex.product.type"].search([("code","!=","OND")]).ids)]}
	# 	return result

	# @api.one
	# @api.onchange("uom_id")
	# def onchange_uom_id(self):
		# if self.delivery_type == "aramex":
			# if self.uom_id.name and self.uom_id.name.upper() in ["LB", "LB(S)"]:
				# self.delivery_uom = "LB"
			# if self.uom_id.name and self.uom_id.name.upper() in ["KG", "KG(S)"]:
				# self.delivery_uom = "KG"

	@api.model
	def create(self, vals):
		if vals.get("delivery_type", False) and vals["delivery_type"] == "aramex" and vals.get("uom_id", False):
			uom_obj = self.env["uom.uom"].browse(vals["uom_id"])
			if uom_obj and uom_obj.name.upper() not in ["LB", "LB(S)","KG", "KG(S)"]:
				raise UserError(_("Aramex Shipping support weight in KG and LB only. Select Odoo Product UoM accordingly."))
		if vals.get("delivery_type", False) and vals["delivery_type"] == "aramex" and vals.get("delivery_uom", False):
			if vals["delivery_uom"] not in ["LB","KG"]:
					raise UserError(_("Aramex Shipping support weight in KG and LB only. Select API UoM accordingly."))
		return super(DeliveryCarrier, self).create(vals)

	def write(self, vals):
		for rec in self:
			if self.delivery_type == "aramex" and vals.get("uom_id", False):
				uom_obj = self.env["uom.uom"].browse(vals["uom_id"])
				if uom_obj and uom_obj.name.upper() not in ["LB", "LB(S)","KG", "KG(S)"]:
					raise UserError(_("Aramex Shipping support weight in KG and LB only. Select Odoo Product UoM accordingly."))
			if self.delivery_type == "aramex" and vals.get("delivery_uom", False):
				if vals["delivery_uom"] not in ["LB","KG"]:
					raise UserError(_("Aramex Shipping support weight in KG and LB only. Select API UoM accordingly."))
		return super(DeliveryCarrier, self).write(vals)

class WkShippingAramexProductType(models.Model):
	_name = "aramex.product.type"
	_description = "Aramex product type"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	is_dutiable = fields.Boolean(string="Dutiable Product")
	description = fields.Text(string="Full Description")


class WkShippingAramexService(models.Model):
	_name = "aramex.service"
	_description = "Aramex Service"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	description = fields.Text(string="Full Description")

class WkShippingAramexProductGroup(models.Model):
	_name = "aramex.product.group"
	_description = "Aramex product group"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	description = fields.Text(string="Full Description")
	
class WkShippingAramexPaymentMethod(models.Model):
	_name = "aramex.payment.method"
	_description = "Aramex product method"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	description = fields.Text(string="Full Description")


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	aramex_shipping_label = fields.Char(string="Aramex Shipping Label", copy=False)
		
	def get_aramex_shipping_label(self,Label,Shipment):
		for record in self:
			attachments = []
			for item in range(len(Label)):
				attachments.append(('aramex_' +Shipment[item]+'.pdf', base64.b64decode(Label[item])))
				msg = "Label generated For Aramex Shipment "
				
			if attachments:
				record.message_post(body=msg, subject="Label For Aramex Shipment",attachments=attachments)
				return True

	def get_all_wk_carriers(self):
		res = super(StockPicking,self).get_all_wk_carriers()
		res.append('aramex')
		return res
				

class ProductPackaging(models.Model):
    _inherit = 'stock.package.type'
    package_carrier_type = fields.Selection(
    	selection_add=[('aramex', 'Aramex')], ondelete={'aramex': 'cascade'})
