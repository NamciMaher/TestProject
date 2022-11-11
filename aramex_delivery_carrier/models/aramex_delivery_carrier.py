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
import logging
from odoo.exceptions import Warning ,ValidationError, UserError
from urllib3.exceptions import HTTPError
from datetime import datetime
_logger = logging.getLogger(__name__)
try:
	from suds.client import Client
except:
	raise Warning("Please install suds: pip3 install suds-py3")
import itertools
# import os
# 
# this_file_dir = os.path.dirname(__file__)

# rate_cal_service_url = str("file:" + this_file_dir.replace("/models", "/") +"aramex/aramex-rates-calculator-wsdl.wsdl")
rate_cal_service_url = "https://ws.aramex.net/ShippingAPI.V2/RateCalculator/Service_1_0.svc?wsdl"
# shipping_service_live_wsdl = str("file:" + this_file_dir.replace("/models","/") +"aramex/shipping-services-api-wsdl.wsdl")
shipping_service_live_wsdl = "https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc?singleWsdl"
# shipping_service_dev_wsdl = str("file:" + this_file_dir.replace("/models","/") +"aramex/shipping-services-api-dev-wsdl.wsdl")
shipping_service_dev_wsdl = "https://ws.dev.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc?singleWsdl"
#Aramex Related things
rat_cal_client = Client(rate_cal_service_url, cache=None)
aramex_tracking_link = "https://www.aramex.com/express/track-results-multiple.aspx?ShipmentNumber="


class DeliveryCarrier(models.Model):
	_inherit="delivery.carrier"

	aramex_username = fields.Char(string="User Name")
	aramex_password = fields.Char(string="Password")
	aramex_account_no = fields.Char(string="Aramex Account Number")
	aramex_account_pin = fields.Char(string="Account Pin")
	aramex_account_entity = fields.Char(string="Account Entity")
	aramex_account_country_code = fields.Char(string="Account Country Code")	
	
	
	def get_soap_client(self):
		# config = self._get_config(key="aramex.config.settings")
		config=self.wk_get_carrier_settings(['aramex_username','aramex_password','aramex_account_no','aramex_account_pin','aramex_account_entity','aramex_account_country_code','prod_environment'])
		if not config.get('prod_environment'):
			shipping_service_url = shipping_service_dev_wsdl
		else:
			shipping_service_url = shipping_service_live_wsdl
		return Client(shipping_service_url, cache=None)

	def create_aramex_address(self, partner_id):
	

		ctx = dict(self._context)		
		partner_type = ctx["partner_type"] if ctx.get("partner_type") else False
		aramex_address_obj = self.get_soap_client().factory.create('Address')
		if not partner_id:
			return aramex_address_obj
		aramex_address_obj.Line1 = partner_id.street.strip() if partner_id.street else ""
		aramex_address_obj.Line2 = partner_id.street2.strip() if partner_id.street2 else ""
		aramex_address_obj.Line3 = ""
		aramex_address_obj.City = partner_id.city
		if partner_id.state_id:
			aramex_address_obj.StateOrProvinceCode = partner_id.state_id.code
		aramex_address_obj.PostCode = partner_id.zip
		aramex_address_obj.CountryCode = partner_id.country_id.code
		return aramex_address_obj

	def create_aramex_dimensions(self, order=None, pickings=None, packaging_id=None, package=None):       
		# enter dimension for packages 
		ctx = dict(self._context)
		aramex_dimensions_obj = self.get_soap_client().factory.create('Dimensions')
		if order :
			package_items = self.wk_get_order_package(order=order)
			items=self.wk_group_by('packaging_id',package_items)
			length = 0
			width = 0
			height = 0
			for Dict in package_items:
				height = Dict['height'] if Dict.get('height',False) and height<Dict['height'] else 1
				width = Dict['width'] if Dict.get('width',False) and width<Dict['width'] else 1
				length = Dict['length'] if Dict.get('length',False) and width<Dict['length'] else 1
			aramex_dimensions_obj.Length = length
			aramex_dimensions_obj.Width = width
			aramex_dimensions_obj.Height = height
			aramex_dimensions_obj.Unit = 'IN' if self.delivery_uom == 'LB' else 'CM'
		elif self.aramex_sender_multi_ship:
			aramex_dimensions_obj.Length = int(package.length) or 1
			aramex_dimensions_obj.Width = int(package.width)	or 1
			aramex_dimensions_obj.Height = int(package.height)	or 1
			aramex_dimensions_obj.Unit = 'IN' if self.delivery_uom == 'LB' else 'CM'
		else:
			aramex_dimensions_obj.Length = self.aramex_consignment_length or 1						
			aramex_dimensions_obj.Width = self.aramex_consignment_width or 1
			aramex_dimensions_obj.Height = self.aramex_consignment_height or 1
			aramex_dimensions_obj.Unit = 'IN' if self.delivery_uom == 'LB' else 'CM'

		return aramex_dimensions_obj
	
	def create_aramex_weight(self, order=None, pickings=None, packaging_id=None, package=None):			
		# here to change the weight of shipmenet as per the package 
		weight = 0
		ctx = dict(self._context)
		aramex_weight_obj = self.get_soap_client().factory.create('Weight')
		if not order and not pickings:
			return aramex_weight_obj
		product_uom_obj = self.env['uom.uom']
		items = order.order_line if order else pickings.move_ids
		for line in items:
			if order and line.state == 'cancel':
				continue
			if order and (not line.product_id or line.is_delivery):
				continue
			q = self._get_default_uom()._compute_quantity(line.product_uom_qty, self.uom_id)
			# q = product_uom_obj._compute_qty_obj(
				# self._get_default_uom(), line.product_uom_qty, self.uom_id)
			weight += (line.product_id.weight or 0.0) * q
			
		aramex_weight_obj.Unit = self.delivery_uom
		if weight :
			aramex_weight_obj.Value = weight
		else:
			raise Warning(_("Product weight must be greater than zero."))
		return aramex_weight_obj

	def get_total_cover_amount(self,order=None):
		amount = 0
		package_items = self.wk_get_order_package(order=order)
		items=self.wk_group_by('packaging_id',package_items)
		for Dict in package_items:
			amount+= Dict['wk_cover_amount'] if Dict.get('wk_cover_amount',False) else 0
		
		return amount
	
	def create_aramex_amount(self, amount_type, order=None, pickings=None, package=None):
	#  Need to update for multiple shipments only 
		ctx = dict(self._context)
		aramex_amount_obj = self.get_soap_client().factory.create('Money')
		if amount_type == "CashOnDeliveryAmount" :
			aramex_amount_obj.Value = pickings.sale_id.amount_total if pickings else 0.0
			aramex_amount_obj.CurrencyCode = "TND" # For Cash on delivery, the currency must be in USD
		elif amount_type == "InsuranceAmount" :
			aramex_amount_obj.Value = package.cover_amount if package else self.get_total_cover_amount(order=order) if order else 0.0 
			aramex_amount_obj.CurrencyCode = self.company_id.currency_id.name
		elif amount_type == "CustomsValueAmount" :
			aramex_amount_obj.Value = pickings.sale_id.amount_total if pickings else 0.0
			aramex_amount_obj.CurrencyCode = self.company_id.currency_id.name
		else:
			aramex_amount_obj.Value = 0.0
			aramex_amount_obj.CurrencyCode = self.company_id.currency_id.name
		return aramex_amount_obj


	def create_aramex_shipment_item(self, order=None, pickings=None, packaging_id=None, package=None):    
		# made changes by extracting values from packages not from pickings 
		ctx = dict(self._context)
		aramex_items_obj = self.get_soap_client().factory.create('ShipmentItem')
		if not order and not pickings:
			return aramex_items_obj
		aramex_items_obj.PackageType = 'Box'
		qty = 0
		items = order.order_line if order else pickings.move_ids
		for line in items:
			if line.product_id.type in ["consu", 'product']:
				qty += line.product_uom_qty
		pick_quantity=0
		if package and pickings:
			quant_ids=package.read(['quant_ids'])[0]['quant_ids']
			for quant_id in quant_ids:
				pick_quantity += self.env['stock.quant'].browse([quant_id]).quantity
		aramex_items_obj.Quantity = pick_quantity if pickings and package else qty
		aramex_items_obj.Comments = "There is no comments."
		aramex_items_obj.Reference = ""
		if order:
			aramex_items_obj.Weight = self.create_aramex_weight(order=order)
		else :
			aramex_items_obj.Weight = self.create_aramex_weight(pickings=pickings, packaging_id=packaging_id, package=package) if package and packaging_id else self.create_aramex_weight(pickings=pickings)
			
		return aramex_items_obj

	def create_aramex_shipment_details(self, order=None, pickings=None, packaging_ids=None, packaging_id=None, package=None):   # here to add the package data except picking data
		ctx = dict(self._context)
		aramex_shipment_details_obj = self.get_soap_client().factory.create('ShipmentDetails')
		if not order and not pickings:
			return aramex_shipment_details_obj
		aramex_shipment_details_obj.Dimensions = self.create_aramex_dimensions(order=order, pickings=pickings, packaging_id=packaging_id, package=package)      	
		# Arguments transfer for package     
		# Need to discuss in case of single shipment
		aramex_shipment_details_obj.ActualWeight = self.create_aramex_weight(order=order) if order else self.create_aramex_weight(pickings=pickings, packaging_id=packaging_id, package=package)    
		# data to be fetched from package		
		aramex_shipment_details_obj.ChargeableWeight = self.create_aramex_weight(order=order) if order else self.create_aramex_weight(pickings=pickings, packaging_id=packaging_id, package=package)
		aramex_shipment_details_obj.ProductGroup = self.aramex_product_group.code if self.aramex_product_group else "EXP"
		aramex_shipment_details_obj.ProductType = self.aramex_product_type.code if self.aramex_product_type else "PDX"
		aramex_shipment_details_obj.PaymentType  = self.aramex_payment_method.code if self.aramex_payment_method else "P"
		aramex_shipment_details_obj.PaymentOptions = ""
		aramex_shipment_details_obj.Services  = pickings.x_studio_many2one_field_wtJRP.code if  pickings.x_studio_many2one_field_wtJRP else "CODS"
		aramex_shipment_details_obj.NumberOfPieces = 1 if order else 1 if self.aramex_sender_multi_ship else sum([len(packages) for packaging,packages in packaging_ids.items()]) if packaging_ids  else 1     # need to approve
		aramex_shipment_details_obj.DescriptionOfGoods  = pickings.note if pickings else "Goods description is not defined."
		aramex_shipment_details_obj.GoodsOriginCountry  = self.env.user.country_id.code
		if pickings.x_studio_many2one_field_wtJRP.code  == 'CODS' :
			aramex_shipment_details_obj.CashOnDeliveryAmount = self.create_aramex_amount(amount_type="CashOnDeliveryAmount",pickings=pickings) 
		aramex_shipment_details_obj.InsuranceAmount = self.create_aramex_amount(amount_type="InsuranceAmount" ,order=order, package=package, pickings=pickings)   	# need to update
		if pickings.x_studio_many2one_field_wtJRP.code  == 'RTRN,CODS' :
			aramex_shipment_details_obj.CashOnDeliveryAmount = self.create_aramex_amount(amount_type="CashOnDeliveryAmount",pickings=pickings) 
		aramex_shipment_details_obj.InsuranceAmount = self.create_aramex_amount(amount_type="InsuranceAmount" ,order=order, package=package, pickings=pickings)   
		if self.aramex_product_type.is_dutiable:
			aramex_shipment_details_obj.CustomsValueAmount = self.create_aramex_amount(amount_type="CustomsValueAmount", pickings = pickings)	
		# below two amount types are never populated, need for create request?
		aramex_shipment_details_obj.CashAdditionalAmount = self.create_aramex_amount(amount_type="CashAdditionalAmount", pickings=pickings, package=package)
		
		aramex_shipment_details_obj.CollectAmount = self.create_aramex_amount(amount_type="CollectAmount", pickings=pickings, package=package)
		
		aramex_shipment_details_obj.Items = self.create_aramex_shipment_item(order=order) if order else self.create_aramex_shipment_item(pickings=pickings, packaging_id=packaging_id, package=package) if self.aramex_sender_multi_ship else list(itertools.chain(*[[self.create_aramex_shipment_item(pickings=pickings, packaging_id=packaging_id, package=package) for package in packages] for packaging_id,packages in packaging_ids.items()]))
		# need to update this also  for picking           
		# # here to make changes for multiple packages.

		return aramex_shipment_details_obj

	def create_aramex_transaction(self, order=None, pickings=None):
		ctx = dict(self._context)
		aramex_transaction_obj = self.get_soap_client().factory.create('Transaction')
		if not order and not pickings:
			return aramex_transaction_obj
		aramex_transaction_obj.Reference1 = order.name if order else pickings.name
		aramex_transaction_obj.Reference2 = ''
		aramex_transaction_obj.Reference3 = ''
		aramex_transaction_obj.Reference4 = ''
		aramex_transaction_obj.Reference5 = ''

		return aramex_transaction_obj

	def create_aramex_client_info(self):
		# config = self._get_config(key="aramex.config.settings")
		config=self.wk_get_carrier_settings(['aramex_username','aramex_password','aramex_account_no','aramex_account_pin','aramex_account_entity','aramex_account_country_code','prod_environment'])
		aramex_client_info_obj = self.get_soap_client().factory.create('ClientInfo')
		aramex_client_info_obj.AccountCountryCode = config.get('aramex_account_country_code')
		aramex_client_info_obj.AccountEntity = config.get('aramex_account_entity')
		if not config.get('prod_environment') and self._context.get("called_by_rate_calculator", False):
			pass
		else:
			aramex_client_info_obj.AccountNumber = config.get('aramex_account_no')
			aramex_client_info_obj.AccountPin = config.get('aramex_account_pin')
		aramex_client_info_obj.UserName = config.get('aramex_username')
		aramex_client_info_obj.Password = config.get('aramex_password')
		aramex_client_info_obj.Version = 'v1'
		return aramex_client_info_obj

	def create_aramex_contact(self, partner_id):
		ctx = dict(self._context)
		contact_type = ctx["contact_type"] if ctx.get("contact_type", False) else False
		aramex_contact_obj = self.get_soap_client().factory.create('Contact')
		if not partner_id:
			return aramex_contact_obj
		aramex_contact_obj.Department = ""
		aramex_contact_obj.PersonName  = partner_id.name
		aramex_contact_obj.Title = partner_id.title.name if partner_id.title else ""
		aramex_contact_obj.CompanyName = partner_id.parent_id.name if partner_id.parent_id else "Odoo"
		aramex_contact_obj.PhoneNumber1 = partner_id.phone 
		aramex_contact_obj.PhoneNumber1Ext = ""
		aramex_contact_obj.PhoneNumber2  = ""
		aramex_contact_obj.PhoneNumber2Ext = ""
		aramex_contact_obj.CellPhone = partner_id.mobile
		aramex_contact_obj.EmailAddress = partner_id.email
		aramex_contact_obj.Type = ""
		return aramex_contact_obj

	def create_aramex_party(self, partner_id):
		# Used for shipper and Consignee
		# config = self._get_config(key="aramex.config.settings")
		config=self.wk_get_carrier_settings(['aramex_username','aramex_password','aramex_account_no','aramex_account_pin','aramex_account_entity','aramex_account_country_code','prod_environment'])
		ctx = dict(self._context)
		party_type = ctx["party_type"] if ctx.get("party_type", False) else False
		aramex_party_obj = self.get_soap_client().factory.create('Party')
		if not partner_id:
			return aramex_party_obj

		aramex_party_obj.Reference1 = partner_id.name
		aramex_party_obj.Reference2 = partner_id.ref or ""
		if party_type == 'sender':
			aramex_party_obj.AccountNumber = config.get('aramex_account_no')
		else:
			aramex_party_obj.AccountNumber = ""
		aramex_party_obj.PartyAddress = self.with_context(partner_type = party_type).create_aramex_address(partner_id)
		aramex_party_obj.Contact = self.with_context(contact_type = party_type).create_aramex_contact(partner_id)
		return aramex_party_obj

	def create_aramex_shipment(self, order=None, pickings=None, packaging_ids=None, packaging_id=None, package=None):
		ctx = dict(self._context)		
		now = datetime.now().strftime("%Y-%m-%d")
		aramex_shipment_obj = self.get_soap_client().factory.create('Shipment')
		if not order and not pickings:
			return aramex_shipment_obj
		aramex_shipment_obj.Shipper = self.with_context(party_type="sender").create_aramex_party(pickings.picking_type_id.warehouse_id.partner_id)
		aramex_shipment_obj.Consignee = self.with_context(party_type="receiver").create_aramex_party(pickings.partner_id)		
		aramex_shipment_obj.Reference1 =  pickings.name if pickings else order.picking_ids[0].name if order.picking_ids else "No Picking For" + order.name
		aramex_shipment_obj.Reference2 =  pickings.sale_id.name if pickings else order.name
		aramex_shipment_obj.Reference3 = ""
		aramex_shipment_obj.TransportType_x0020_ = 0
		aramex_shipment_obj.ShippingDateTime = now
		aramex_shipment_obj.DueDate = now
		aramex_shipment_obj.PickupLocation =  "Reception"  #Need to discuss
		aramex_shipment_obj.PickupGUID = ''
		aramex_shipment_obj.Comments =  'No comments define'
		aramex_shipment_obj.AccountingInstrcutions = ''
		aramex_shipment_obj.OperationsInstructions = ''
		aramex_shipment_obj.Details = self.create_aramex_shipment_details(order=order) if order else self.create_aramex_shipment_details(pickings=pickings, packaging_id=packaging_id, package=package) if self.aramex_sender_multi_ship else self.create_aramex_shipment_details(pickings=pickings, packaging_ids=packaging_ids)
		return aramex_shipment_obj

	def create_aramex_array_of_shipment(self, order=None, pickings=None, packaging_ids=None):
		sender_multi_ship = self.aramex_sender_multi_ship
		ctx = dict(self._context)
		aramex_array_of_shipment_obj = self.get_soap_client().factory.create('ArrayOfShipment')
		if not order and not pickings:
			return aramex_array_of_shipment_obj
		if order:
			aramex_array_of_shipment_obj.Shipment = [self.create_aramex_shipment(order=order)]
		else:
			aramex_array_of_shipment_obj.Shipment = [self.create_aramex_shipment(pickings=pickings,packaging_ids=packaging_ids)] if not sender_multi_ship else list(itertools.chain(*[[self.create_aramex_shipment(pickings=pickings, packaging_id=packaging_id ,package=package) for package in packages] for packaging_id , packages in packaging_ids.items()]))

		return aramex_array_of_shipment_obj

	def create_aramex_label_info(self, report_type="RPT"):
		ctx = dict(self._context)
		aramex_label_info_obj = self.get_soap_client().factory.create('LabelInfo')
		aramex_label_info_obj.ReportID = 9824
		aramex_label_info_obj.ReportType = report_type  #Can be 'URL' or 'RPT'
		return aramex_label_info_obj

	def aramex_set_shipping_price(self, order=None, pickings=None):
		# Code for rate calculation
		rate= None
		if self.delivery_type == "aramex":
			rate = 6
		return rate

	def aramex_rate_shipment(self, orders):
		# self.wk_validate_object_fields(orders.warehouse_id.partner_id,['name','phone','mobile','email','street','city', 'zip', 'country_id'])
		# self.wk_validate_object_fields(orders.partner_shipping_id if orders.partner_shipping_id else orders.partner_id,['name','phone','mobile','email','street','city', 'zip', 'country_id'])
		response = {
			"price": self.aramex_set_shipping_price(order=orders) or 0,
			"error_message": None,
			"warning_message": None,
			"success": True,
		}
		return response

	def aramex_send_shipping(self, pickings):
		# validate details of sender
		# self.wk_validate_object_fields(pickings.picking_type_id.warehouse_id.partner_id,['name','phone','mobile','email','street','city', 'zip', 'country_id'])
		# validate details of recepient
		# self.wk_validate_object_fields(pickings.partner_id,['name','phone','mobile','email','street','city', 'zip', 'country_id'])
		# validate aramex credentials 
		# if all validations successful then proceed
		
		for obj in self:
			now = datetime.now().strftime("%Y-%m-%d")
			ctx = obj._context.copy()
			error_msg =""
			packaging_ids = obj.wk_group_by_packaging(pickings=pickings)
			try:
				clientobj = obj.create_aramex_client_info()
				transactionobj = obj.create_aramex_transaction(pickings.sale_id)
				labelinfoobj = obj.create_aramex_label_info('RPT')
				Shipments_obj = obj.create_aramex_array_of_shipment(pickings=pickings,packaging_ids=packaging_ids)
				result = obj.get_soap_client().service.CreateShipments(clientobj, transactionobj, Shipments_obj, labelinfoobj)
				shipment_id = []
				Labels = []
				if result.Shipments:
					for ship in result.Shipments.ProcessedShipment:
						shipment_id.append(str(ship.ID))
						label_url = ship.ShipmentLabel.LabelFileContents if ship.ShipmentLabel else ""
						Labels.append(label_url)

						if label_url:
							pickings.label_genrated = True
							pickings.aramex_shipping_label = label_url

					if Labels:
						pickings.get_aramex_shipping_label(Labels,shipment_id)
				if result.HasErrors:
					if result.Shipments:
						for x in result.Shipments.ProcessedShipment[0].Notifications.Notification:
							error_msg += x.Code + " " + x.Message + "\n"
					else:
						for x in result.Notifications.Notification:
							error_msg += x.Code + " " + x.Message + "\n"
				if error_msg:
					raise Warning(error_msg)
				total_weight = 0
				for ship_weight in Shipments_obj.Shipment:
					total_weight += ship_weight.Details.ActualWeight.Value
				shipping_weight_value = total_weight
				shipping_weight_uom = Shipments_obj.Shipment[0].Details.ActualWeight.Unit
				for product_uom_obj in obj.env["uom.uom"].search([]):
					if shipping_weight_uom == "LB" and product_uom_obj.name.upper() in ["LB", "LB(S)"] :
						pickings.shipment_uom_id = product_uom_obj
					if shipping_weight_uom == "KG" and product_uom_obj.name.upper() in  ["KG", "KG(S)"]:
						pickings.shipment_uom_id = product_uom_obj
				pickings.weight_shipment = float(shipping_weight_value)

				result = {
					'exact_price':  obj.aramex_set_shipping_price(order=pickings.sale_id) if pickings.sale_id else obj.aramex_set_shipping_price(pickings=pickings),
					'tracking_number': (','.join(shipment_id)),
					'weight' : shipping_weight_value,
				}
				return result
			except HTTPError as e:
				_logger.info(
					"---HTTPError---in---Aramax-send-shipping----%r-------------------", e)
				raise UserError(e)
			except Exception as e:
				_logger.info(
					"---Exception---in---Aramax-send-shipping----%r-------------------", e)
				raise UserError(e)


	@api.model
	def aramex_get_tracking_link(self,pickings):
		track_url = aramex_tracking_link + pickings.carrier_tracking_ref
		return track_url

			
	def aramex_cancel_shipment(self,pickings):
		raise ValidationError('This feature is not supported by Aramex.....')
