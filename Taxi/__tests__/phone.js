import omit from 'lodash/omit';
import {LOCALES_LIST} from '../../help/consts';
import {parsePhone, formatPhone} from '../phone';

const phones = [
    {
        full: '+74957397000',
        locale: 'RU',
        code: '7',
        sign: '+',
        number: '4957397000',
        formatted: '+7 (495) 739-70-00'
    },
    {
        full: '375251234567',
        locale: 'BY',
        code: '375',
        sign: '',
        number: '251234567',
        formatted: '+375 (251) 234-567'
    },
    {
        full: '+380681234567',
        locale: 'UA',
        sign: '+',
        code: '380',
        number: '681234567',
        formatted: '+380 68 123 45 67'
    },
    {
        full: '77712345678',
        locale: 'KZ',
        sign: '',
        code: '7',
        number: '7712345678',
        formatted: '+7 (771) 234-56-78'
    },
    {
        full: '995712345678',
        locale: 'GE',
        sign: '',
        code: '995',
        number: '712345678',
        formatted: '+995 712 345-678'
    }
];

describe('utils:phone', () => {
    it('should return initial str argument if matched with no locale', () => {
        const invalidNumber = '3223532434323234324242';
        expect(formatPhone(invalidNumber)).toBe(invalidNumber);
    });

    it('should correctly parse phone number and format for all existing locales at `../../help/consts.js`', () => {
        const existingLocales = LOCALES_LIST.map(({name}) => name).sort();
        const testedLocales = [];
        for (let phone of phones) {
            const parsed = parsePhone(phone.full);
            testedLocales.push(parsed.locale);
            expect(omit(parsed, 'mask')).toEqual(omit(phone, 'formatted'));
        }
        expect(testedLocales.sort()).toEqual(existingLocales);
    });

    it('should use mask with corresponding phone number length', () => {
        jest.resetModules();
        jest.mock('../../help/consts', () => {
            return {
                LOCALES_LIST: [
                    {
                        country: 'Disneyland',
                        code: '666',
                        name: 'DL',
                        phoneStarts: ['1', '12', '123', '1234'],
                        masks: {
                            2: '2: xxx xx',
                            3: '3: xxx xxx',
                            4: '4: xxx xxxx',
                            5: '+xxx (xx)-x-x-x'
                        }
                    }
                ]
            };
        });
        const format = require('../phone').formatPhone;
        expect(format('66611')).toBe('2: 666 11');
        expect(format('666121')).toBe('3: 666 121');
        expect(format('6661231')).toBe('4: 666 1231');
        expect(format('+66612366')).toBe('+666 (12)-3-6-6');
    });
});
