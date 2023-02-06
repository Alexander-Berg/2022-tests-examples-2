class ReplicationService:
    def __init__(self):
        self.billing_id = '123'

    def get_billing_id(self):
        return {'billing_id': self.billing_id, 'client_id': 'client_id'}

    def get_contract(self):
        return [
            {'ID': 123, 'IS_ACTIVE': 1, 'SERVICES': [668, 123]},
            {'ID': 234, 'IS_ACTIVE': 0, 'SERVICES': [668, 123]},
            {'ID': 345, 'IS_ACTIVE': 1, 'SERVICES': [555, 718]},
            {'ID': 456, 'IS_ACTIVE': 1, 'SERVICES': [636]},
        ]
