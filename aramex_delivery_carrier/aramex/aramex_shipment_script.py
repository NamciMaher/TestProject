#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from suds.client import Client
"""
# Shipment creation method
-----------------------------------------
1. ShipmentCreationRequest
    1.1. ClientInfo
    1.2. Transaction
    1.3. Shipments
    1.4. LabelInfo
2. ShipmentCreationResponse
    2.1 Transaction
    2.2 Notifications
    2.3 HasErrors
    2.4 Shipments

# Label Printing Method
------------------------------------------
1. LabelPrintingRequest
    1.1. ClientInfo
    1.2. Transaction
    1.3. ShipmentNumber
    1.4. ProductGroup
    1.5. OriginEntity
    1.6. LabelInfo 
2. LabelPrintingResponse
    2.1 Transaction
    2.2 Notifications
    2.3 HasErrors
    2.4 ShipmentNumber
"""

# 1. ClientInfo
# ------------------
client = Client("https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc?singleWsdl")
print(client)
ClientInfo = client.factory.create('ClientInfo')

# setting client credentials
ClientInfo.UserName = "	daf@wamia.tn"
ClientInfo.Password = "sX63Vp74F##KiaX"
ClientInfo.Version = "v1.0"
ClientInfo.AccountNumber = "140411"
ClientInfo.AccountPin = "453316"
ClientInfo.AccountEntity = "TUN"
ClientInfo.AccountCountryCode = "TN"

# 2. Transaction
# ------------------
# setting values for transaction
Transaction = client.factory.create("Transaction")


Transaction.Reference1 = "S00043"
Transaction.Reference2 = ""
Transaction.Reference3 = ""
Transaction.Reference4 = ""
Transaction.Reference5 = ""


# 3. Shipments
# ------------------
# setting values for Shipments(ArrayOfShipment)

Shipment = client.factory.create('Shipment')
Shipper = client.factory.create('Party')
Consignee = client.factory.create('Party')
ShipperPartyAddress = client.factory.create('Address')
ShipperContact = client.factory.create('Contact')
ConsigneePartyAddress = client.factory.create('Address')
ConsigneeContact = client.factory.create('Contact')

# assigning values to Shippper party address and contact info
ShipperPartyAddress.Line1 = "Avenue Yasser Arafat, Sahloul Sousse"
ShipperPartyAddress.Line2 = "Immeuble Mehdi, 3éme Etage 1506005/X/A/M/000"
ShipperPartyAddress.City = "Sousse"
ShipperPartyAddress.City = "Sousse"
# ShipperPartyAddress.StateOrProvinceCode = "Amman"
ShipperPartyAddress.PostCode = "4054"
ShipperPartyAddress.CountryCode = "TN"

# ShipperContact.Department = ""
ShipperContact.PersonName = "Demo Shipper"
ShipperContact.CompanyName = "STE WAMIA"
ShipperContact.PhoneNumber1 = "+21622003387"
# ShipperContact.PhoneNumber1Ext = ""
# ShipperContact.PhoneNumber2 = ""
# ShipperContact.PhoneNumber2Ext = ""
ShipperContact.CellPhone = "+21622003387"
ShipperContact.EmailAddress = "contact@wamia.tn"
# ShipperContact.Type = ""


# assigning values to consignee party address and contact info
ConsigneePartyAddress.Line1 = "7, rue Abou Al Hassan Al Amiri, Cité Ibn Cina, Al Ouardia 7"
ConsigneePartyAddress.Line2 = "Sahab - Industrial Area"
ConsigneePartyAddress.Line3 = False
ConsigneePartyAddress.City = "EL OUERDIA"
ConsigneePartyAddress.StateOrProvinceCode = "Tunis"
# ConsigneePartyAddress.StateOrProvinceCode = "1000"
ConsigneePartyAddress.PostCode = "18503"
ConsigneePartyAddress.CountryCode = "TN"

# ConsigneeContact.Department = ""
ConsigneeContact.PersonName = "Demo Receiver"
ConsigneeContact.Title = False
ConsigneeContact.CompanyName = "Test"
ConsigneeContact.PhoneNumber1 = "+21622003383"
# ConsigneeContact.PhoneNumber1Ext = ""
# ConsigneeContact.PhoneNumber2 = ""
# ConsigneeContact.PhoneNumber2Ext = ""
# ConsigneeContact.FaxNumber = None
ConsigneeContact.CellPhone = "+21622003383"
ConsigneeContact.EmailAddress = "aramex-customer@test.com"
# ConsigneeContact.Type = ""

# assigning values to shipper
Shipper.Reference1 = "My Company (San Francisco)"
Shipper.Reference2 = ""
Shipper.AccountNumber = "20016"
Shipper.PartyAddress = ShipperPartyAddress
Shipper.Contact = ShipperContact

# assignig values to Consignee
Consignee.Reference1 = "Aramax Shipping Demo customer"
Consignee.Reference2 = ""
Consignee.AccountNumber = ""
Consignee.PartyAddress = ConsigneePartyAddress
Consignee.Contact = ConsigneeContact

Weight = client.factory.create("Weight")
Weight.Value = 3.55
Weight.Unit = "KG"
Details = client.factory.create("ShipmentDetails")

dimensions = client.factory.create("Dimensions")
dimensions.Length = 1
dimensions.Width = 10
dimensions.Height = 10
dimensions.Unit = "CM"
Shipment.Dimensions = dimensions

Details.ActualWeight = Weight
Details.ChargeableWeight = Weight

Details.DescriptionOfGoods = "Clothes"
Details.GoodsOriginCountry = "US"
Details.NumberOfPieces = 1
Details.ProductGroup = "DOM"
Details.ProductType = "OND"
Details.PaymentType = "C"
Details.PaymentOptions = ""
Details.PaymentOptions = ""


amount = client.factory.create("Money")
amount.CurrencyCode = "USD"
amount.Value = 0.0

Details.CustomsValueAmount = amount
Details.CashOnDeliveryAmount = amount
Details.InsuranceAmount = amount
Details.CashAdditionalAmount = amount
Details.CollectAmount = amount
Details.Services = "SIG"

item = client.factory.create('ShipmentItem')
item.PackageType = "BOX"
item.Quantity = 1
item.Weight = Weight
item.Comments = "NO COMMENTS"
Details.Items = [item,]





# assigning values to shipment(nested fields defined above)
Shipment.Reference1 = "WH/OUT/00016"
Shipment.Reference2 = "S00043"
Shipment.Reference3 = ""
Shipment.Shipper = Shipper
Shipment.Consignee = Consignee
Shipment.ShippingDateTime = "2022-04-07"
Shipment.DueDate = "2022-04-07"
Shipment.Comments = "No comments define"
Shipment.PickupLocation = "Reception"
Shipment.OperationsInstructions = ""
Shipment.AccountingInstrcutions = ""
Shipment.Details = Details
Shipment.TransportType_x0020_ = 0
Shipment.PickupGUID = ""

Shipments = client.factory.create('ArrayOfShipment')
Shipments.Shipment = [Shipment,]

LabelInfo = client.factory.create('LabelInfo')
LabelInfo.ReportID = 9202
LabelInfo.ReportType = "RPT"

print('----------------------------------------------------------------------------------------------------------')
# print(ClientInfo)
# print(Transaction)
# print(Shipment)
# print(LabelInfo)
print('----------------------------------------------------------------------------------------------------------')
response = client.service.CreateShipments(ClientInfo, Transaction, Shipments, LabelInfo)
print(response)
print('----------------------------------------------------------------------------------------------------------')
