import {getAliasBySource} from '_pkg/utils/httpApi/utils';
import {ApiSource} from '_types/common/api';

describe('utils/httpApi', () => {
    test('getAliasBySource', async () => {
        expect(getAliasBySource(ApiSource.Python3)).toBe('/api-t/admin/');
        expect(getAliasBySource(ApiSource.Python2, 'orders')).toBe('/api-t/orders/');

        expect(getAliasBySource(ApiSource.Python2, 'orders', [{
            from: {source: ApiSource.Python2, prefix: 'orders'},
            to: {source: ApiSource.Python3, prefix: 'admin_orders/v1'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, 'orders', [{
            from: {source: ApiSource.Python2, prefix: 'orders'},
            to: {source: ApiSource.Python3, prefix: 'admin_orders/v1/'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, '/orders', [{
            from: {source: ApiSource.Python2, prefix: 'orders'},
            to: {source: ApiSource.Python3, prefix: '/admin_orders/v1'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, '/orders/', [{
            from: {source: ApiSource.Python2, prefix: 'orders'},
            to: {source: ApiSource.Python3, prefix: '/admin_orders/v1/'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, 'orders/', [{
            from: {source: ApiSource.Python2, prefix: 'orders'},
            to: {source: ApiSource.Python3, prefix: 'admin_orders/v1'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, 'orders', [{
            from: {source: ApiSource.Python2, prefix: '/orders'},
            to: {source: ApiSource.Python3, prefix: 'admin_orders/v1'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, 'orders', [{
            from: {source: ApiSource.Python2, prefix: 'orders/'},
            to: {source: ApiSource.Python3, prefix: 'admin_orders/v1'}
        }])).toBe('/api-t/admin/admin_orders/v1/');

        expect(getAliasBySource(ApiSource.Python2, 'orders', [{
            from: {source: ApiSource.Python2, prefix: '/orders/'},
            to: {source: ApiSource.Python3, prefix: 'admin_orders/v1'}
        }])).toBe('/api-t/admin/admin_orders/v1/');
    });
});
