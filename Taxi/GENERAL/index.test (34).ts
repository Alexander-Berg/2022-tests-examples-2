import {unlinkSync} from 'fs';
import {join as pathJoin} from 'path';
import {describe, expect, it} from 'tests/jest.globals';
import {v4 as uuidv4} from 'uuid';
import {utils, writeFile} from 'xlsx';

import {serviceResolve} from '@/src/lib/resolve';

import {AttributePrimitiveValue, parse} from './index';

const TMP = serviceResolve('storage/temp');

function createXlsx(data: (AttributePrimitiveValue | undefined)[][]): string {
    const book = utils.book_new();

    const sheet = utils.aoa_to_sheet(data);

    utils.book_append_sheet(book, sheet, 'Test');

    const filePath = pathJoin(TMP, uuidv4() + '.xlsx');

    writeFile(book, filePath);

    return filePath;
}

describe('product xlsx parser', () => {
    it('should parse simple import', async () => {
        const filePath = createXlsx([
            ['id', 'category'],
            [1000, 1],
            [undefined, 2]
        ]);

        await expect(parse(filePath)).toEqual({
            toAdd: [{category: 2}],
            toUpdate: [{id: 1000, category: 1}]
        });

        unlinkSync(filePath);
    });

    it('should parse plural attribute value', async () => {
        const filePath = createXlsx([
            ['id', 'barcode', 'barcode'],
            [1000, '4680020180720', '4607027765842']
        ]);

        await expect(parse(filePath)).toEqual({
            toAdd: [],
            toUpdate: [{id: 1000, barcode: ['4680020180720', '4607027765842']}]
        });

        unlinkSync(filePath);
    });

    it('should parse localized attribute value', async () => {
        const filePath = createXlsx([
            ['id', 'name|ru', 'name|en'],
            [1000, 'Мороженое', 'Ice cream']
        ]);

        await expect(parse(filePath)).toEqual({
            toAdd: [],
            toUpdate: [
                {
                    id: 1000,
                    name: {ru: 'Мороженое', en: 'Ice cream'}
                }
            ]
        });

        unlinkSync(filePath);
    });

    it('should ignore all expect first sheet', async () => {
        const book = utils.book_new();

        for (let i = 0; i < 5; i++) {
            const sheet = utils.aoa_to_sheet([
                ['id', 'category'],
                [1000, i]
            ]);

            utils.book_append_sheet(book, sheet, `Test ${i}`);
        }

        const filePath = pathJoin(TMP, uuidv4() + '.xlsx');

        writeFile(book, filePath);

        await expect(parse(filePath)).toEqual({
            toAdd: [],
            toUpdate: [{id: 1000, category: 0}]
        });

        unlinkSync(filePath);
    });

    it('should ignore empty raw', async () => {
        const filePath = createXlsx([
            ['id', 'name'],
            [undefined, undefined],
            [1000, 'Мороженое'],
            [undefined, undefined]
        ]);

        await expect(parse(filePath)).toEqual({
            toAdd: [],
            toUpdate: [{id: 1000, name: 'Мороженое'}]
        });

        unlinkSync(filePath);
    });

    it('should ignore empty sheet', async () => {
        const filePath = createXlsx([]);

        await expect(parse(filePath)).toEqual(null);

        unlinkSync(filePath);
    });

    it('should ignore sheet without content', async () => {
        const filePath = createXlsx([['id', 'title']]);

        await expect(parse(filePath)).toEqual(null);

        unlinkSync(filePath);
    });
});
