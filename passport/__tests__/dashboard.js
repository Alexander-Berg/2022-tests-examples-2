import {getData} from '../actions';

import * as extracted from '../dashboard.js';

jest.mock('../actions', () => ({
    getData: jest.fn()
}));
jest.mock('@blocks/morda/components/money', () => jest.fn());

describe('Dashboard', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            isRU: true,
            props: {
                dispatch: jest.fn(),
                dashboard: {
                    plus: {},
                    diskData: {
                        initialLoad: true
                    },
                    musicData: {
                        initialLoad: true
                    },
                    favMarketData: {
                        errors: true
                    }
                },
                person: {},
                common: {},
                settings: {
                    ua: {}
                }
            }
        };
    });
    afterEach(() => {
        getData.mockClear();
    });

    describe('getDataHandler', () => {
        it('should dispatch getData', () => {
            obj.props.settings.tld = 'ua';
            extracted.getDataHandler.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(getData).toHaveBeenCalledTimes(1);
            expect(getData).toHaveBeenCalledWith(['favMarketData', 'diskData', 'musicData']);
        });
        it('shouldnt have diskData', () => {
            obj.props.person.isSocialchik = true;
            obj.props.settings.tld = 'ua';
            extracted.getDataHandler.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(getData).toHaveBeenCalledTimes(1);
            expect(getData).toHaveBeenCalledWith(['favMarketData', 'musicData']);
        });
        it('shouldnt have musicData', () => {
            obj.props.common.isPDD = true;
            extracted.getDataHandler.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(getData).toHaveBeenCalledTimes(1);
            expect(getData).toHaveBeenCalledWith(['favMarketData', 'diskData']);
        });
        it('shouldnt dispatch any', () => {
            obj.props.dashboard = {musicData: {}, plus: {}};
            extracted.getDataHandler.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
        });
    });

    describe('isPhone', () => {
        it('should return false', () => {
            expect(extracted.isPhone.call(obj)).toBeFalsy();
            expect(extracted.isPhone.call(obj, false)).toBeFalsy();
        });
        it('should return true', () => {
            obj.props.settings.ua = {isMobile: true};
            expect(extracted.isPhone.call(obj)).toBeTruthy();
            expect(extracted.isPhone.call(obj, false)).toBeTruthy();

            obj.props.settings.ua = {isTouch: true};
            expect(extracted.isPhone.call(obj)).toBeTruthy();
            expect(extracted.isPhone.call(obj, false)).toBeTruthy();
        });
    });
});
