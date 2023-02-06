col_types = {'insurance_company_name': 'String?',
             'account_date': 'String?',
             'claim_id': 'String?',
             'order_id': 'String?',
             'event_dt': 'String?',
             'client_contact_dt': 'String?',
             'all_documents_dt': 'String?',
             'payment_or_refusal_dt': 'String?',
             'client_fio': 'String?',
             'victim_role': 'String?',
             'phone_number': 'String?',
             'comment': 'String?',
             'risk_name': 'String?',
             'payment_table_point': 'String?',
             'ocr_rub': 'Double?',
             'payment_rub': 'Double?',
             'sent_to_payment_dt': 'String?',
             'status': 'String?',
             'refusal_of_compensation': 'Int64?'
             }

col_types.pop('sent_to_payment_dt')

print(col_types)