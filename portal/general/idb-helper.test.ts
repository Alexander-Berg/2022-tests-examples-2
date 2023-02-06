interface HelperValue {
    value: unknown;
    expire: number;
    version: string;
}
const mockStore = new Map<string, HelperValue|null>();

jest.mock('../../../../common/blocks/idb-keyval/idb-keyval', () => {
    return {
        get: jest.fn().mockImplementation(key => {
            return Promise.resolve(mockStore.get(key));
        }),
        set: jest.fn().mockImplementation((key, value) => {
            return Promise.resolve()
                .then(() => {
                    mockStore.set(key, value);
                });
        }),
        delete: jest.fn().mockImplementation(key => {
            return Promise.resolve()
                .then(() => {
                    mockStore.delete(key);
                });
        }),
        clear: jest.fn().mockImplementation(() => {
            return Promise.resolve()
                .then(() => {
                    mockStore.clear();
                });
        }),
        keys: jest.fn().mockImplementation(() => {
            throw new Error('unused');
        })
    };
});

import {
    getLayout,
    cacheLayout,
    clearLayout,
    tryClearLayout,
    updateLabelInHtml,
    setCurrentVersion,
    _layoutKey
} from './idb-helper';

function testSetStore(value = '', version = '', expire = Infinity) {
    mockStore.set(_layoutKey, {
        value,
        version,
        expire
    });
}

function testGetStore() {
    return mockStore.get(_layoutKey);
}

describe('idb-helper', () => {
    beforeEach(async() => {
        await clearLayout();
        mockStore.clear();

        setCurrentVersion('test-100');
    });

    describe('getLayout', () => {
        test('Не возвращает лейаут без версии', async() => {
            testSetStore('oldlayout');
            const res = await getLayout();

            expect(res).toBeNull();
        });

        test('Не возвращает лейаут c не правильной версией', async() => {
            testSetStore('oldlayout', 'test-99');
            const res = await getLayout();
            expect(res).toBeNull();
        });

        test('Не возвращает лейаут c не правильной версией с флагом useExpired', async() => {
            testSetStore('oldlayout', 'test-99');
            const res = await getLayout(true);
            expect(res).toBeNull();
        });

        test('Возвращает лейаут c правильной версией', async() => {
            testSetStore('oldlayout', 'test-100');
            const res = await getLayout();

            expect(res).toEqual('oldlayout');
        });

        test('Не возвращает протухший лейаут', async() => {
            testSetStore('oldlayout', 'test-100', Date.now());
            const res = await getLayout();
            expect(res).toBeNull();
        });

        test('Возвращает протухший лейаут с флагом useExpired', async() => {
            testSetStore('oldlayout', 'test-100', Date.now());
            const res = await getLayout(true);

            expect(res).toEqual('oldlayout');
        });
    });

    describe('cacheLayout', () => {
        beforeEach(() => {
            testSetStore('oldlayout');
        });

        const newExpire = Date.now() + 500000;
        const newCacheVal = {
            value: 'newlayout',
            version: 'test-100',
            expire: newExpire
        };
        const oldCacheVal =  {
            value: 'oldlayout',
            version: 'test-99',
            expire: Infinity
        };

        test('записывает кеш, если версии нет', async() => {
            await cacheLayout('newlayout', newExpire);

            expect(testGetStore()).toEqual(newCacheVal);
        });

        test('записывает кеш, если версия совпадает', async() => {
            testSetStore('oldlayout', 'test-100');
            await cacheLayout('newlayout', newExpire);

            expect(testGetStore()).toEqual(newCacheVal);
        });

        test('не записывает кеш, если версия отличается', async() => {
            testSetStore('oldlayout', 'test-99');
            await cacheLayout('newlayout', newExpire);

            expect(testGetStore()).toEqual(oldCacheVal);
        });
    });

    describe('updateLabelInHtml', () => {
        const oldContent = 'old<!--begin:qwe-->old chunk<!--end:qwe-->layout';
        const newExpire = Date.now() + 52000;
        beforeEach(() => {
            testSetStore(oldContent, 'test-100');
        });

        it('заменяет чанк, если версия совпадает', async() => {
            await updateLabelInHtml({
                label: 'qwe',
                html: 'new chunk',
                expire: newExpire
            });

            expect(testGetStore()).toEqual({
                value: 'old<!--begin:qwe-->new chunk<!--end:qwe-->layout',
                version: 'test-100',
                expire: newExpire
            });
        });

        it('заменяет чанк, если версия совпадает и лейаут протух', async() => {
            testSetStore(oldContent, 'test-100', Date.now());
            await updateLabelInHtml({
                label: 'qwe',
                html: 'new chunk',
                expire: newExpire
            });

            expect(testGetStore()).toEqual({
                value: 'old<!--begin:qwe-->new chunk<!--end:qwe-->layout',
                version: 'test-100',
                expire: newExpire
            });
        });

        it('не заменяет чанк, если версия отличается', async() => {
            testSetStore(oldContent, 'test-99');

            await updateLabelInHtml({
                label: 'qwe',
                html: 'new chunk',
                expire: newExpire
            });

            expect(testGetStore()).toEqual({
                value: 'old<!--begin:qwe-->old chunk<!--end:qwe-->layout',
                version: 'test-99',
                expire: Infinity
            });
        });
    });

    describe('cleanLayout', () => {
        beforeEach(() => {
            testSetStore('oldlayout');
        });

        test('чистит лейаут, когда версии нет', async() => {
            await tryClearLayout();
            expect(testGetStore()).toBeUndefined();
        });

        test('чистит лейаут, когда версия отличается', async() => {
            testSetStore('oldlayout', 'test-99');
            await tryClearLayout();
            expect(testGetStore()).toBeUndefined();
        });

        test('не чистит лейаут, когда версия совпадает', async() => {
            testSetStore('oldlayout', 'test-100');
            await tryClearLayout();
            expect(testGetStore()).toEqual({
                value: 'oldlayout',
                version: 'test-100',
                expire: Infinity
            });
        });
    });

    describe('in-memory кэш, если версия отличается', () => {
        const newExpire = Date.now() + 300000;
        beforeEach(async() => {
            testSetStore('old<!--begin:qwe-->old chunk<!--end:qwe-->', 'test-100');
            await getLayout();
            testSetStore('new<!--begin:qwe-->old chunk<!--end:qwe-->', 'test-101');
        });

        it('использует кэш при getLayout, если версия отличается', async() => {
            const res = await getLayout();

            expect(res).toEqual('old<!--begin:qwe-->old chunk<!--end:qwe-->');

            expect(testGetStore()).toEqual({
                value: 'new<!--begin:qwe-->old chunk<!--end:qwe-->',
                version: 'test-101',
                expire: Infinity
            });
        });

        it('использует кэш при getLayout с флагом useExpired, если версия отличается', async() => {
            const res = await getLayout(true);

            expect(res).toEqual('old<!--begin:qwe-->old chunk<!--end:qwe-->');

            expect(testGetStore()).toEqual({
                value: 'new<!--begin:qwe-->old chunk<!--end:qwe-->',
                version: 'test-101',
                expire: Infinity
            });
        });

        it('использует кэш при cacheLayout, если версия отличается', async() => {
            await cacheLayout('newlayout', newExpire);
            const res = await getLayout();

            expect(res).toEqual('newlayout');

            expect(testGetStore()).toEqual({
                value: 'new<!--begin:qwe-->old chunk<!--end:qwe-->',
                version: 'test-101',
                expire: Infinity
            });
        });

        it('использует кэш при updateLabelInHtml, если версия отличается', async() => {
            await updateLabelInHtml({
                label: 'qwe',
                html: 'new chunk',
                expire: newExpire
            });
            const res = await getLayout();

            expect(res).toEqual('old<!--begin:qwe-->new chunk<!--end:qwe-->');

            expect(testGetStore()).toEqual({
                value: 'new<!--begin:qwe-->old chunk<!--end:qwe-->',
                version: 'test-101',
                expire: Infinity
            });
        });
    });
});
