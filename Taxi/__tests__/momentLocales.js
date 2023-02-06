import _ from 'lodash';
import momentLocales from '../momentLocales';

const momentLanguages = {
    hy: 'hy-am'
};

const {getMomentLanguage, getMomentLanguages} = momentLocales(momentLanguages);

describe('momentLocales', () => {
    it('Should be return lang as is', () => {
        expect(getMomentLanguage('en')).toEqual('en');
        expect(getMomentLanguage('ru')).toEqual('ru');
        expect(getMomentLanguages(['en', 'ru'])).toEqual(['en', 'ru']);
    });

    it('Should be return specific lang for moment', () => {
        expect(getMomentLanguages(_.keys(momentLanguages))).toEqual(_.values(momentLanguages));
    });
});
