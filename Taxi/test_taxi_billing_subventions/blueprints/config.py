def new_billing_migration(attrs):
    defaults = {
        'commissions': {'enabled': {'moscow': [{'first_date': '2000-01-01'}]}},
        'subventions': {'enabled': {'moscow': [{'first_date': '2000-01-01'}]}},
        'promocodes': {'enabled': {'moscow': [{'first_date': '2000-01-01'}]}},
    }
    defaults.update(attrs)
    return defaults
