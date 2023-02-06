import {getLocale} from '../../../../common';
import {setAddressesSuggest} from '../';

jest.mock('../../../../common', () => ({
    getLocale: jest.fn(() => 'ru')
}));
jest.mock('../', () => ({
    setAddressesSuggest: jest.fn()
}));

import {getSuggest} from '../get_suggest';

describe('Action: getSuggest', () => {
    afterEach(() => {
        getLocale.mockClear();
        setAddressesSuggest.mockClear();
    });

    it('should get suggest', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            settings: {
                lang: 'ru'
            }
        }));
        const entry = 'entry';

        global.$.getJSON = jest.fn(() => {
            return {
                done: jest.fn((successFn) => {
                    successFn({});
                })
            };
        });

        getSuggest(entry)(dispatch, getState);

        expect($.getJSON).toBeCalled();
        expect($.getJSON).toBeCalledWith('https://suggest-maps.yandex.net/suggest-geo?callback=?', {
            fullpath: 1,
            lang: 'ru',
            n: 5,
            part: entry,
            search_type: 'addr',
            v: 7
        });
        expect(getLocale).toBeCalled();
        expect(setAddressesSuggest).toBeCalled();
    });

    it('should get suggest with empty settings', () => {
        const dispatch = jest.fn();
        const getState = jest.fn(() => ({}));
        const entry = 'entry';

        global.$.getJSON = jest.fn(() => {
            return {
                done: jest.fn((successFn) => {
                    successFn({});
                })
            };
        });

        getSuggest(entry)(dispatch, getState);

        expect($.getJSON).toBeCalled();
        expect($.getJSON).toBeCalledWith('https://suggest-maps.yandex.net/suggest-geo?callback=?', {
            fullpath: 1,
            lang: 'ru',
            n: 5,
            part: entry,
            search_type: 'addr',
            v: 7
        });
        expect(getLocale).toBeCalled();
        expect(setAddressesSuggest).toBeCalled();
    });
});
