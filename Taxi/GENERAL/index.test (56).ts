import {escapeMarkdownV1} from './index';

describe('package "telegram"', () => {
    it('should correct replace symbols for markdown v1', () => {
        expect(escapeMarkdownV1('[TEST]: *`[_')).toBe('\\[TEST]: \\*\\`\\[\\_');
    });
});
