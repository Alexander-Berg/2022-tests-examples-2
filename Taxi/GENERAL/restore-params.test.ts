import {restoreParams} from './restore-params';

describe('restoreParams', () => {
    it('should ', () => {
        expect(restoreParams('% param %')).toBe('%param%');
        expect(restoreParams('% param%')).toBe('%param%');
        expect(restoreParams('%param %')).toBe('%param%');
        expect(restoreParams('% % param % %')).toBe('% %param% %');
        expect(restoreParams('% % param1 % % param2 % some%')).toBe('% %param1% %param2% some%');
    });
});
