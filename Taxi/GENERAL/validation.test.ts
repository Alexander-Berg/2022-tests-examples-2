import {merge} from 'lodash';

import {GENDERS} from '../consts';

import {rusValidationSchema} from './validation';

const address = {
    street: 'xxx',
    city: 'xxx',
    house: '12',
    index: '12',
};

const model = {
    company_name: 'xxx',
    offer_agreement: true,
    company_tin: {
        company_tin: '7702070139',
        legal_address: address,
        signer_name: 'xxx',
        signer_position: 'xxx',
        signer_gender: GENDERS.Male,
        legal_form: 'Индивидуальный предприниматель',
        is_mailing_address_same: false,
        mailing_address: address,
        company_ogrn: '318619600189662',
        enterprise_name_full: 'enterprise_name_full',
        enterprise_name_short: 'enterprise_name_short',
    },
};

test('IP', () => {
    expect(rusValidationSchema.isValidSync(model)).toBe(true);
});

test('not IP', () => {
    expect(
        rusValidationSchema.isValidSync(
            merge(model, {
                company_tin: {
                    legal_form: 'Филиал юридического лица',
                },
            }),
        ),
    ).toBe(false);

    expect(
        rusValidationSchema.isValidSync(
            merge(model, {
                company_tin: {
                    legal_form: 'Филиал юридического лица',
                    company_cio: '366643001',
                },
            }),
        ),
    ).toBe(true);
});

test('same mailing address', () => {
    expect(
        rusValidationSchema.isValidSync(
            merge(model, {
                company_tin: {
                    is_mailing_address_same: true,
                    mailing_address: undefined,
                },
            }),
        ),
    ).toBe(true);
});

test('not full address', () => {
    expect(
        rusValidationSchema.isValidSync(
            merge(model, {
                company_tin: {
                    is_mailing_address_same: true,
                    legal_address: {
                        index: null,
                    },
                },
            }),
        ),
    ).toBe(false);
});
