import time
import locale
import requests
import xml.etree.ElementTree as ElementTree

BODY_TER= """
<?xml version="1.0" encoding="UTF-8"?>
 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
   <soapenv:Body>
     <GetActiveTerminals xmlns="http://tempuri.org/">
     <Auth><Login>yadtaxi2020</Login><Password>LA3sUW92kuffL6S</Password></Auth></GetActiveTerminals>
   </soapenv:Body>
 </soapenv:Envelope>
"""

BODY_CANCEL = """
<?xml version="1.0" encoding="UTF-8"?>
 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
   <soapenv:Body>
     <RefuseOrder xmlns="http://tempuri.org/">
     <OrderId>3291967</OrderId>
     <Auth><Login>yadtaxi2020</Login><Password>LA3sUW92kuffL6S</Password></Auth></RefuseOrder>
   </soapenv:Body>
 </soapenv:Envelope>
"""

BODY_INFO = """
<?xml version="1.0" encoding="UTF-8"?>
 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
   <soapenv:Body>
     <GetOrdersStatusHistory xmlns="http://tempuri.org/">
     <orders><int>3291967</int></orders>
     <Auth><Login>yadtaxi2020</Login><Password>LA3sUW92kuffL6S</Password></Auth></GetOrdersStatusHistory>
   </soapenv:Body>
 </soapenv:Envelope>
"""

BODY_CREATE = """
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soapenv:Body>
<RegisterOrderExtended xmlns="http://tempuri.org/">
<order xmlns="strizh-logistic.ru/services/v2/sinc/RegionOrder">
<OrderIdImport>inventive</OrderIdImport>
 <User>
 <FIO>Wilhelm Alexey</FIO>
 <Phone>+79166266016</Phone>
 <Email/>
 </User>
 <StockId>d6336b16-1b8d-4329-9876-8fe39948cce7</StockId>
 <Address>
 <FullAddress>Moscow, Baumanskaya street</FullAddress>
 <Latitude>55.797842</Latitude>
 <Longitude>37.612084</Longitude>
 <Region>Москва</Region>
 <City>Москва</City>
 <AddressComment>comment</AddressComment>
 </Address>
 <Items>
 <Item>
 <Article>DH6757-100-7.5</Article>
 <Name>919EA2989A98</Name>
 <Count>1</Count>
 <Price>9799</Price>
 <AssessedCost>9799</AssessedCost>
 <NDS>20</NDS>
 <SellerInn>7701402303</SellerInn>
 <Barcode/>
 <BarcodePackage>B280B5BC8F</BarcodePackage>
 <MarkingCode>010019523810420721?K&amp;MMaprkh,ER</MarkingCode>
 </Item>
 </Items>
 <barcodes>
 <PieceBarcode>
 <piece>1</piece>
 <barcode>B280B5BC8F</barcode>
 </PieceBarcode>
 </barcodes>
 <PiecesOfFreight>1</PiecesOfFreight>
 <Weight>0.000</Weight>
 <Volume>1.000</Volume>
 <TotalCost>0</TotalCost>
 <DeliveryCost>350</DeliveryCost>
 <NDSDelivery>20</NDSDelivery>
 <IsPartialGiveoutDisabled>0</IsPartialGiveoutDisabled>
 <AssessedCost>9799</AssessedCost>
 <SettingId>801</SettingId>
 <DesiredDeliveryDate>2021-10-09</DesiredDeliveryDate>
 <TimeDeliveryFrom>15-00</TimeDeliveryFrom>
 <TimeDeliveryTo>20-00</TimeDeliveryTo>
 <DeliveryPlaceId>1</DeliveryPlaceId>
 <SourcePlaceId>1</SourcePlaceId>
 <SelfDelivery>0</SelfDelivery>
 <PayType>1</PayType>
 <Comment>B280B5BC8F</Comment>
 </order>
    <Auth><Login>yadtaxi2020</Login><Password>LA3sUW92kuffL6S</Password></Auth></RegisterOrderExtended>
  </soapenv:Body>
</soapenv:Envelope>"""
 

# BODY = """<?xml version="1.0" encoding="UTF-8"?>
# <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
#   <soapenv:Body>
#     <GetActiveTerminals xmlns="http://tempuri.org/">
#     <Auth><Login>yadtaxi2020</Login><Password>LA3sUW92kuffL6S</Password></Auth></GetActiveTerminals>
#   </soapenv:Body>
# </soapenv:Envelope>
# """

BODY_REG = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soapenv:Body>
    <RegisterWarehouse xmlns="http://tempuri.org/">
    <warehouse>
    <StockIdImport>1</StockIdImport>
    <StockName>a</StockName>
    <Address>Moscow</Address>
    <Latitude>55.751310</Latitude>
    <Longitude>37.584613</Longitude>
    <PhoneNumber>89778703475</PhoneNumber>
    <ContactPersonName>Alexey</ContactPersonName>
    <Email>alexeyvilmost@gmail.com</Email>
    <Comment>comment</Comment>
    </warehouse>
    <Auth><Login>yadtaxi2020</Login><Password>LA3sUW92kuffL6S</Password></Auth></RegisterWarehouse>
  </soapenv:Body>
</soapenv:Envelope>
"""

if __name__ == '__main__':
    before = time.time()
    payload = BODY_TER
    print(payload)
    r = requests.post(
        'https://yandex-delivery.landpro.site/soap/topdelivery-test',
        #'http://adminka.strizh-logistic.ru/services/v2/sinc.asmx',
        data=payload,
        timeout=10,
        headers={
            'Content-Type': 'text/xml; charset=utf-8',
        }
    )
    print(r.status_code, r.text, r.request.headers)
    r.raise_for_status()
    print(time.time() - before)