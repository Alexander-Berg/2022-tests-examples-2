import {getFirstIssueIDFromEachString} from './ticket';

describe('getFirstIssueIDFromEachString', () => {
    test('Из каждой строки должен браться только первый issueID', () => {
        const desc = 'TXI-1 TXI-2 \r\nTXI-3 TXI-4 TXI-5\nTXI-6 test';
        expect(getFirstIssueIDFromEachString(['TXI'])(desc)).toEqual(['TXI-1', 'TXI-3', 'TXI-6']);
    });
});
