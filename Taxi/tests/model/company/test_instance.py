async def test_instance(tap, dataset):
    with tap.plan(9):

        company = dataset.Company({
            'title': 'A1',
            'products_scope': ['russia', 'israel'],
            'ownership': 'franchisee',
            'vat_no': '12345',
            'deduction_tax_id': '54321',
            'instance_erp': 'fr',
        })
        tap.ok(company, 'Объект создан')
        tap.ok(await company.save(), 'сохранение')
        tap.ok(await company.save(), 'обновление')

        tap.eq(company.title, 'A1', 'title')
        tap.eq(company.products_scope, ['russia', 'israel'], 'products_scope')
        tap.eq(company.ownership, 'franchisee', 'ownership')
        tap.eq(company.vat_no, '12345', 'vat_no')
        tap.eq(company.deduction_tax_id, '54321', 'deduction_tax_id')
        tap.eq(company.instance_erp, 'fr', 'instance_erp')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        company = await dataset.company()
        tap.ok(company, 'Объект создан')
