import {getIndexesOf} from '@yandex-taxi/omnichat/src/utils/common';
import {getShortMatches, getFullMatches} from '../utils';

describe('utils', () => {
    const SEARCH_VALUE = 'SEARCH_VALUE';
    const TEXT = `${SEARCH_VALUE} 111 ${SEARCH_VALUE} 222 ${SEARCH_VALUE} 333 ${SEARCH_VALUE} 444 ${SEARCH_VALUE} 555 ${SEARCH_VALUE} 666 ${SEARCH_VALUE}`;

    const matchIndexes = getIndexesOf(SEARCH_VALUE, TEXT);

    test('getShortMatches', () => {
        expect(getShortMatches(SEARCH_VALUE, matchIndexes, TEXT)).toEqual({
            hasMore: false,
            matches: [
                ['SEARCH_VALUE', ' 111 ', 'SEARCH_VALUE', ' 222 SEARCH'],
                ['VALUE 333 ', 'SEARCH_VALUE', ' 444 ', 'SEARCH_VALUE', ' '],
                ['55 ', 'SEARCH_VALUE', ' 666 ', 'SEARCH_VALUE']
            ]
        });

        expect(getShortMatches(SEARCH_VALUE, matchIndexes, TEXT, 2)).toEqual({
            hasMore: true,
            matches: [
                ['SEARCH_VALUE', ' 111 ', 'SEARCH_VALUE', ' 222 SEARCH'],
                ['VALUE 333 ', 'SEARCH_VALUE', ' 444 ', 'SEARCH_VALUE', ' ']
            ]
        });
    });

    test('getFullMatches', () => {
        expect(getFullMatches(SEARCH_VALUE, TEXT)).toEqual([
            [
                'SEARCH_VALUE',
                ' 111 ',
                'SEARCH_VALUE',
                ' 222 ',
                'SEARCH_VALUE',
                ' 333 ',
                'SEARCH_VALUE',
                ' 444 ',
                'SEARCH_VALUE',
                ' 555 ',
                'SEARCH_VALUE',
                ' 666 ',
                'SEARCH_VALUE'
            ]
        ]);
    });
});
