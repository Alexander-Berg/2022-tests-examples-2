import {showWithLeadZero, getTimerSeconds, getTimerMinutes} from '../timer.js';

const ONE_SECOND = 1000;
const ONE_MINUTE = ONE_SECOND * 60;

describe('Component: Timer', () => {
    it('should return number with lead zero', () => {
        expect(showWithLeadZero('6')).toBe('06');
    });

    it('should return number without lead zero', () => {
        expect(showWithLeadZero('50')).toBe('50');
    });

    it('should return timer seconds', () => {
        const startTime = Number(new Date());
        const endTime = startTime + ONE_SECOND * 30;

        expect(getTimerSeconds(startTime, endTime)).toBe(30);
    });

    it('should return empty timer ', () => {
        const startTime = Number(new Date());
        const endTime = startTime - ONE_SECOND * 30;

        expect(getTimerSeconds(startTime, endTime)).toBe(0);
    });

    it('should return timer minutes', () => {
        const startTime = Number(new Date());
        const endTime = startTime + ONE_MINUTE * 30;

        expect(getTimerMinutes(startTime, endTime)).toBe(30);
    });

    it('should return timer minutes', () => {
        const startTime = Number(new Date());
        const endTime = startTime - ONE_MINUTE * 30;

        expect(getTimerMinutes(startTime, endTime)).toBe(0);
    });
});
