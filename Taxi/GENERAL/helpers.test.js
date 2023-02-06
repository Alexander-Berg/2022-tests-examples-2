const {getI18nWithFallback} = require('./helpers');

describe('tariff disclaimer helpers', () => {
    it('getI18nWithFallback отрабатывает в нужной последовательности', () => {
        const mockPrint = jest.fn(() => '');
        const i18n = {
            print: mockPrint
        };

        const i18nFallback = getI18nWithFallback(i18n, {zoneName: 'moscow'}, 'econom', false);

        i18nFallback('keyname');
        expect(mockPrint).toHaveBeenNthCalledWith(1, 'keyname.no-service', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(2, 'keyname.moscow.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(3, 'keyname.null.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(4, 'keyname.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(5, 'keyname.moscow', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(6, 'keyname.null', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(7, 'keyname', undefined);
        expect(mockPrint).toHaveBeenCalledTimes(7);
    });

    it('getI18nWithFallback отрабатывает в нужной последовательности с метазоной', () => {
        const mockPrint = jest.fn(() => '');
        const i18n = {
            print: mockPrint
        };

        const i18nFallback = getI18nWithFallback(
            i18n,
            {zoneName: 'moscow', metaZoneName: 'belarusArea'},
            'econom',
            false
        );

        i18nFallback('keyname');
        expect(mockPrint).toHaveBeenNthCalledWith(1, 'keyname.no-service', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(2, 'keyname.moscow.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(3, 'keyname.belarusArea.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(4, 'keyname.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(5, 'keyname.moscow', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(6, 'keyname.belarusArea', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(7, 'keyname', undefined);
        expect(mockPrint).toHaveBeenCalledTimes(7);
    });

    it('getI18nWithFallback с корп ключами отрабатывает в нужной последовательности', () => {
        const mockPrint = jest.fn(() => '');
        const i18n = {
            print: mockPrint
        };

        const i18nFallback = getI18nWithFallback(i18n, {zoneName: 'moscow'}, 'econom', true);

        i18nFallback('keyname');
        expect(mockPrint).toHaveBeenNthCalledWith(1, 'keyname.no-service.corp', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(2, 'keyname.moscow.econom.corp', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(3, 'keyname.null.econom.corp', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(4, 'keyname.econom.corp', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(5, 'keyname.moscow.corp', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(6, 'keyname.null.corp', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(7, 'keyname.corp', undefined);

        expect(mockPrint).toHaveBeenNthCalledWith(8, 'keyname.no-service', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(9, 'keyname.moscow.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(10, 'keyname.null.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(11, 'keyname.econom', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(12, 'keyname.moscow', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(13, 'keyname.null', undefined);
        expect(mockPrint).toHaveBeenNthCalledWith(14, 'keyname', undefined);
        expect(mockPrint).toHaveBeenCalledTimes(14);
    });
});
