import { formatDuration } from '../formatDuration';

describe('formatDuration', function() {
    test('should format', function() {
        expect(formatDuration(0)).toEqual('00:00');
        expect(formatDuration(10000)).toEqual('2:46:40');
        expect(formatDuration(1000)).toEqual('16:40');
        expect(formatDuration(100)).toEqual('01:40');
        expect(formatDuration(10)).toEqual('00:10');
    });
});
