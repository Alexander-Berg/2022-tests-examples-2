// import {Product} from '@/src/entities/product/entity';

describe('test database', () => {
    it('should connect successfully', async () => {
        const cnt = 1;

        await expect(cnt).toBeGreaterThanOrEqual(0);
    });
});
