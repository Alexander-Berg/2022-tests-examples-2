import { EntityBase } from '@shared/entity/entity-base';
import { SelectQueryBuilder } from 'typeorm';
import { convertParamToCursor, DataFormat } from '../converter';
import { runPaginatedQuery } from '../query';

const mockRepository = jest.fn(() => ({
    createQueryBuilder: jest.fn(() => ({
        take: jest.fn().mockReturnThis(),
        andWhere: jest.fn().mockReturnThis(),
        orderBy: jest.fn().mockReturnThis(),
        getManyAndCount: jest.fn().mockReturnValueOnce([[], 0]),
    })),
}));

describe('pagination', () => {
    it('run empty query', async () => {
        const queryBuilder = mockRepository().createQueryBuilder();

        await runPaginatedQuery(queryBuilder as unknown as SelectQueryBuilder<EntityBase>, {
            dataFormat: DataFormat.date,
            extractValueForCursor: () => undefined,
            limit: 10,
            orderColumn: 'product.createdAt',
        });

        expect(queryBuilder.andWhere).not.toBeCalled();
        expect(queryBuilder.orderBy).toHaveBeenCalledWith('product.createdAt', 'DESC');
    });

    it('run query with after cursor', async () => {
        const queryBuilder = mockRepository().createQueryBuilder();

        const cursorAfter = convertParamToCursor(DataFormat.date, new Date('2012-12-12'));

        await runPaginatedQuery(queryBuilder as unknown as SelectQueryBuilder<EntityBase>, {
            dataFormat: DataFormat.date,
            extractValueForCursor: () => undefined,
            limit: 10,
            cursorAfter: cursorAfter,
            orderColumn: 'product.createdAt',
        });

        expect(queryBuilder.orderBy).toHaveBeenCalledWith('product.createdAt', 'DESC');
        expect(queryBuilder.andWhere).toHaveBeenCalledWith('product.createdAt < :cursorKey', {
            cursorKey: new Date('2012-12-12'),
        });
    });

    it('run query with before cursor', async () => {
        const queryBuilder = mockRepository().createQueryBuilder();

        const cursorBefore = convertParamToCursor(DataFormat.date, new Date('2012-12-12'));

        await runPaginatedQuery(queryBuilder as unknown as SelectQueryBuilder<EntityBase>, {
            dataFormat: DataFormat.date,
            extractValueForCursor: () => undefined,
            limit: 10,
            cursorBefore: cursorBefore,
            orderColumn: 'product.createdAt',
        });

        expect(queryBuilder.orderBy).toHaveBeenCalledWith('product.createdAt', 'ASC');
        expect(queryBuilder.andWhere).toHaveBeenCalledWith('product.createdAt > :cursorKey', {
            cursorKey: new Date('2012-12-12'),
        });
    });
});
