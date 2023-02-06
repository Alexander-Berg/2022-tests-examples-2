import {get, set} from 'lodash';

import HistoryManager, {DEFAULT_CONFIG, IStorage} from '../HistoryManager';

class Storage implements IStorage {
    private _data: any;

    public get = (key: string) => {
        return get(this._data, key);
    }

    public set = (key: string, data: any) => {
        return set(this._data, key, data);
    }
}

let historyManager: HistoryManager<string>;

describe('HistoryManager', function () {
    beforeEach(() => {
        historyManager = new HistoryManager<string>(new Storage());
    });

    test('push', () => {
        const data = 'str_1';
        const item = historyManager.push(data);

        expect(item.data).toBe(data);
        expect(item.meta).toHaveProperty('timestamp');
        expect(historyManager.length).toBe(1);
    });

    test('no items', () => {
        expect(historyManager.current).toBe(undefined);
        expect(historyManager.prev()).toBe(undefined);
        expect(historyManager.next()).toBe(undefined);
        expect(historyManager.hasPrev()).toBe(false);
        expect(historyManager.hasNext()).toBe(false);
    });

    test('push inside limmit', () => {
        let limmit = DEFAULT_CONFIG.limmit * 2;
        while (limmit--) {
            historyManager.push(`str_${limmit}`);
        }

        expect(historyManager.length).toBe(DEFAULT_CONFIG.limmit);
        expect(historyManager.current.data).toBe(`str_${limmit + 1}`);
    });

    test('navigation', () => {
        const data1 = 'str_1';
        const data2 = 'str_2';
        historyManager.push(data1);
        historyManager.push(data2);

        expect(historyManager.current.data).toBe(data2);
        expect(historyManager.prev().data).toBe(data1);
        expect(historyManager.next().data).toBe(data2);
    });

    test('prev and next inside range', () => {
        historyManager.push('1');
        historyManager.push('2');
        let length = historyManager.length * 2;

        while (length--) {
            historyManager.prev();
        }

        expect(historyManager.hasPrev()).toBe(false);
        expect(historyManager.hasNext()).toBe(true);

        while (length++ < historyManager.length * 2) {
            historyManager.next();
        }

        expect(historyManager.hasPrev()).toBe(true);
        expect(historyManager.hasNext()).toBe(false);
    });

    test('no sibling duplicates', () => {
        historyManager.push('1');
        historyManager.push('1');
        historyManager.push('2');
        historyManager.push('1');

        expect(historyManager.length).toBe(3);
        expect(historyManager.current.data).toBe('1');
        expect(historyManager.prev().data).toBe('2');
        expect(historyManager.prev().data).toBe('1');
    });
});
