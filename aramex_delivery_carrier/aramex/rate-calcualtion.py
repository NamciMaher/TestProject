import os, xml, logging
# from SOAPpy import WSDL
from suds.client import Client
from datetime import datetime, timedelta

now =  datetime.today().date()

# logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# url = "http://localhost/shipping-services-api-wsdl.wsdl"
path = os.getcwd()
client = Client('file:'+path+'/aramex-rates-calculator-wsdl.wsdl', cache=None)
# print client
# client.sd[0].service.setlocation('https://ws.dev.aramex.net/shippingapi/shipping/service_1_0.svc')  	#Https

PartyAddress = client.factory.create('Address') #Used in party (shipper)
PartyAddress.Line1 =  '123'
PartyAddress.Line2 =  ''
PartyAddress.Line3 =  ''
PartyAddress.City =  'Riyadh'
PartyAddress.StateOrProvinceCode =  'RUH'
PartyAddress.PostCode =  '11190'
PartyAddress.CountryCode =  'SA'


PartyAddress2 = client.factory.create('Address') #Used in party (shipper)
PartyAddress2.Line1 =  '123'
PartyAddress2.Line2 =  ''
PartyAddress2.Line3 =  ''
PartyAddress2.City =  'Riyadh'
PartyAddress2.StateOrProvinceCode =  'RUH'
PartyAddress2.PostCode =  '14610'
PartyAddress2.CountryCode =  'SA'


Dimensions_obj = client.factory.create("Dimensions") #Used in ShipmetDetails 
Dimensions_obj.Length = 0.0
Dimensions_obj.Width = 0.0
Dimensions_obj.Height = 0.0
Dimensions_obj.Unit = 'CM'

ActualWeight_obj = client.factory.create("Weight") #Used in ShipmetDetails 
ActualWeight_obj.Value = 0.4
ActualWeight_obj.Unit = 'KG'

CashOnDeliveryAmount_obj = client.factory.create("Money") #Used in ShipmetDetails 
CashOnDeliveryAmount_obj.Value = 0.0
CashOnDeliveryAmount_obj.CurrencyCode = 'SAR'

InsuranceAmount_obj = client.factory.create("Money") #Used in ShipmetDetails 
InsuranceAmount_obj.Value = 0.0
InsuranceAmount_obj.CurrencyCode = 'SAR'

CollectAmount_obj = client.factory.create("Money") #Used in ShipmetDetails 
CollectAmount_obj.Value = 0.0
CollectAmount_obj.CurrencyCode = 'SAR'

CashAdditionalAmount_obj = client.factory.create("Money") #Used in ShipmetDetails 
CashAdditionalAmount_obj.Value = 0.0
CashAdditionalAmount_obj.CurrencyCode = 'SAR'

CustomsValueAmount_obj = client.factory.create("Money") #Used in ShipmetDetails 
CustomsValueAmount_obj.Value = 0.0
CustomsValueAmount_obj.CurrencyCode = 'SAR'


Items_obj = client.factory.create("ShipmentItem") #Used in ShipmetDetails 
Items_obj.PackageType = 'Box'
Items_obj.Quantity = 1
Items_obj.Weight = ActualWeight_obj
Items_obj.Comments = 'Docs'
Items_obj.Reference = ""

deliveryobj = client.factory.create('DeliveryInstructions')
deliveryobj.Option = '1'
deliveryobj.Reference = 'SO001'

shipmentDetails_obj = client.factory.create("ShipmentDetails")
shipmentDetails_obj.Dimensions = Dimensions_obj
shipmentDetails_obj.ActualWeight = ActualWeight_obj
shipmentDetails_obj.ChargeableWeight = ActualWeight_obj
shipmentDetails_obj.ProductGroup = "DOM"
shipmentDetails_obj.ProductType = "OND"
shipmentDetails_obj.PaymentType  = "P"
shipmentDetails_obj.PaymentOptions = ""
shipmentDetails_obj.Services  = ""
shipmentDetails_obj.NumberOfPieces = 1
shipmentDetails_obj.DescriptionOfGoods  = "Clothes, Electronic Gadgets"
shipmentDetails_obj.GoodsOriginCountry  = "SA"
shipmentDetails_obj.CashOnDeliveryAmount = CashOnDeliveryAmount_obj
shipmentDetails_obj.InsuranceAmount = InsuranceAmount_obj
shipmentDetails_obj.CollectAmount = CollectAmount_obj
shipmentDetails_obj.CashAdditionalAmount = CashAdditionalAmount_obj
shipmentDetails_obj.CustomsValueAmount = CustomsValueAmount_obj
# shipmentDetails_obj.DeliveryInstructions = deliveryobj
shipmentDetails_obj.Items = Items_obj


transactionobj = client.factory.create('Transaction')
transactionobj.Reference1 = 'SO122'
transactionobj.Reference2 = ''
transactionobj.Reference3 = ''
transactionobj.Reference4 = ''
transactionobj.Reference5 = ''



Live_clientobj = client.factory.create('ClientInfo')
Live_clientobj.AccountCountryCode = 'SA'
Live_clientobj.AccountEntity = 'RUH'
# Live_clientobj.AccountNumber = '4004636'
# Live_clientobj.AccountPin = '432432'
Live_clientobj.UserName = 'testingapi@aramex.com'
Live_clientobj.Password = 'R123456789$r'
Live_clientobj.Version = '1.0' #'v1.0


origin_address = PartyAddress
destinatio_address = PartyAddress2
print shipmentDetails_obj
rate = client.service.CalculateRate(Live_clientobj, transactionobj,origin_address, destinatio_address, shipmentDetails_obj)
print rate.TotalAmount.CurrencyCode
print rate.TotalAmount.Value
print rate