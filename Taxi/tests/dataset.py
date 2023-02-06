# pylint: disable=import-error
from uuid import uuid4
from odoo.tests.common import SavepointCase
from odoo.addons.hire.backend.utils import keyword


class MainDataset(SavepointCase):
    # Create objects
    @classmethod
    def company(cls, save=False, **kwargs,):
        kwargs.setdefault('company_wid', uuid4().hex)
        kwargs.setdefault('name', f'{keyword.keyword()}')
        kwargs.setdefault('vat', uuid4().hex)

        if save:
            company = cls.env['res.company'].create(kwargs)
            kwargs['id'] = company.id
        return kwargs

    @classmethod
    def store(cls, save=False, **kwargs,):
        kwargs.setdefault('store_wid', uuid4().hex)
        kwargs.setdefault('name', f'{keyword.keyword()}')
        kwargs.setdefault('city', f'{keyword.keyword()}')
        if 'company_id' not in kwargs:
            company = cls.company(save=True)
            kwargs.setdefault('company_wid', company['company_wid'])
            kwargs.setdefault('company_id', company['id'])
        elif 'company_id' in kwargs and 'company_wid' not in kwargs:
            exist_company = cls.env['res.company'].search(
                [('id', '=', kwargs['company_id'])])
            kwargs.setdefault('company_wid', exist_company[0]['company_wid'])

        if save:
            store = cls.env['res.partner'].create(kwargs)
            kwargs['id'] = store.id
        return kwargs

    @classmethod
    def department(cls, save=False, **kwargs):
        kwargs.setdefault('staff_id', uuid4().hex)
        kwargs.setdefault('name', f'{keyword.keyword()}')

        if save:
            department = cls.env['hr.department'].create(kwargs)
            kwargs['id'] = department.id
        return kwargs
