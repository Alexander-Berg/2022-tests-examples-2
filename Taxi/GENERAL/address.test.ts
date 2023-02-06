import {describe, expect, it} from 'tests/jest.globals';

import {Kind} from 'types/address';

import {getAddressTitle, getShortAddress} from './address';

describe('getShortAddress()', () => {
    it('should return short address', async () => {
        const address = getShortAddress({
            formattedAddress: '',
            components: [
                {
                    name: 'Россия',
                    kind: Kind.COUNTRY
                },
                {
                    name: 'Центральный федеральный округ',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Москва',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Москва',
                    kind: Kind.LOCALITY
                },
                {
                    name: 'улица Александра Невского',
                    kind: Kind.STREET
                },
                {
                    name: '1',
                    kind: Kind.HOUSE
                }
            ]
        });

        expect(address).toEqual('Москва, улица Александра Невского, 1');
    });

    it('should return short address with province #1', async () => {
        const address = getShortAddress({
            formattedAddress: '',
            components: [
                {
                    name: 'Россия',
                    kind: Kind.COUNTRY
                },
                {
                    name: 'Центральный федеральный округ',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Московская область',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Наро-Фоминский городской округ',
                    kind: Kind.AREA
                },
                {
                    name: 'Апрелевка',
                    kind: Kind.LOCALITY
                }
            ]
        });

        expect(address).toEqual('Московская область, Апрелевка');
    });

    it('should return short address with province #2', async () => {
        const address = getShortAddress({
            formattedAddress: '',
            components: [
                {
                    name: 'Россия',
                    kind: Kind.COUNTRY
                },
                {
                    name: 'Центральный федеральный округ',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Наро-Фоминский городской округ',
                    kind: Kind.AREA
                },
                {
                    name: 'Краснознаменск',
                    kind: Kind.LOCALITY
                },
                {
                    name: '1',
                    kind: Kind.HOUSE
                }
            ]
        });

        expect(address).toEqual('Центральный федеральный округ, Краснознаменск, 1');
    });
});

describe('getAddressTitle()', () => {
    it('should return a ymap format address', async () => {
        const address = getAddressTitle({
            formattedAddress: '',
            components: [
                {
                    name: 'Россия',
                    kind: Kind.COUNTRY
                },
                {
                    name: 'Центральный федеральный округ',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Москва',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Москва',
                    kind: Kind.LOCALITY
                },
                {
                    name: 'улица Александра Невского',
                    kind: Kind.STREET
                },
                {
                    name: '1',
                    kind: Kind.HOUSE
                }
            ]
        });

        expect(address).toEqual('улица Александра Невского, 1');
    });

    it('should return last address component', async () => {
        const address = getAddressTitle({
            formattedAddress: '',
            components: [
                {
                    name: 'Россия',
                    kind: Kind.COUNTRY
                },
                {
                    name: 'Центральный федеральный округ',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Москва',
                    kind: Kind.PROVINCE
                },
                {
                    name: 'Москва',
                    kind: Kind.LOCALITY
                },
                {
                    name: 'Апрелевка',
                    kind: Kind.LOCALITY
                }
            ]
        });

        expect(address).toEqual('Апрелевка');
    });

    it('should return the street address', async () => {
        const address = getAddressTitle({
            formattedAddress: '',
            components: [
                {
                    name: 'Россия',
                    kind: Kind.COUNTRY
                },
                {
                    name: 'М-1, новый выход на МКАД',
                    kind: Kind.STREET
                }
            ]
        });

        expect(address).toEqual('М-1, новый выход на МКАД');
    });
});
