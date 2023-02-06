import {createMsTimer} from '.';

describe('package "timer"', () => {
    it('should handle "createMsTimer"', () => {
        const timer = createMsTimer();
        const ms = timer();
        expect(Number.isInteger(ms)).toBeTruthy();
    });
});
