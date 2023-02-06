def test_order(client_maker):
    client = client_maker(locale='en')
    client.init_phone(phone='random')
    client.launch()
    client.set_source([37.587997, 55.734528])
    client.order('speed-1000,wait-0')
    client.wait_for_order_status()
