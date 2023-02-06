import {uuid} from 'casual';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {CODES} from '@/src/constants';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {ImportSpreadsheetTooManyCells, ImportSpreadsheetTooManyRows} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {runResolveWorker} from 'server/routes/api/v1/import/products/resolve';
import {config} from 'service/cfg';

import {resolveBulkActionsHandler} from './resolve-bulk-actions';

jest.mock('server/routes/api/v1/import/products/resolve', () => ({
    ...jest.requireActual('server/routes/api/v1/import/products/resolve'),
    runResolveWorker: jest.fn()
}));

describe('bulk resolve', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;
    let mock: jest.Mock;
    let originalRowsLimit: number;
    let originalCellsLimit: number;

    afterAll(() => {
        jest.unmock('server/routes/api/v1/import/resolve');
        jest.resetModules();

        config.import.maxSpreadsheetRows = originalRowsLimit;
        config.import.maxSpreadsheetCells = originalCellsLimit;
    });

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {product: {canEdit: true}, canBulk: true}});
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
        mock = (runResolveWorker as jest.Mock).mockImplementationOnce(() => {});

        originalRowsLimit = config.import.maxSpreadsheetRows;
        originalCellsLimit = config.import.maxSpreadsheetCells;

        config.import.maxSpreadsheetRows = 100;
        config.import.maxSpreadsheetCells = config.import.maxSpreadsheetRows * 10;
    });

    afterEach(() => {
        mock.mockClear();
    });

    it('should throw on exceeding rows limit', async () => {
        const body = Array.from({length: config.import.maxSpreadsheetRows + 2}, () => ['']);
        await expect(
            resolveBulkActionsHandler.handle({
                context,
                data: {body, params: {bulkKey: uuid}}
            })
        ).rejects.toThrow(ImportSpreadsheetTooManyRows);
    });

    it('should throw on exceeding cells limit', async () => {
        const maxCols = Math.ceil(config.import.maxSpreadsheetCells / config.import.maxSpreadsheetRows);
        const row = Array.from({length: maxCols + 1}, () => '');
        const body = Array.from({length: config.import.maxSpreadsheetRows + 1}, () => row);

        await expect(
            resolveBulkActionsHandler.handle({
                context,
                data: {body, params: {bulkKey: uuid}}
            })
        ).rejects.toThrow(ImportSpreadsheetTooManyCells);
    });

    it('should ignore headers and insignificant columns (id, fullness)', async () => {
        const maxCols = Math.ceil(config.import.maxSpreadsheetCells / config.import.maxSpreadsheetRows);
        const headers = ['id', CODES.FULLNESS, 'attributeCode#confirmed'].concat(
            Array.from({length: maxCols}, () => '')
        );
        const row = Array.from({length: headers.length}, () => '');
        const rows = Array.from({length: config.import.maxSpreadsheetRows}, () => row);
        const body = [headers, ...rows];

        expect(body.length).toBeGreaterThan(config.import.maxSpreadsheetRows);
        expect(headers.length * rows.length).toBeGreaterThan(config.import.maxSpreadsheetCells);

        await expect(
            resolveBulkActionsHandler.handle({
                context,
                data: {body, params: {bulkKey: uuid}}
            })
        ).resolves.toEqual({success: true});
    });
});
