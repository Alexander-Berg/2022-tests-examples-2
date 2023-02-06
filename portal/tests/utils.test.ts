import {
    extractTickets,
    sortVersions
} from '../lib/utils';
import {expect} from 'chai';

describe('utils', () => {
    describe('extractTickets', () => {
        it('выбирает коммиты без знака', () => {
            const res = extractTickets([
                {
                    message: 'SOME-123: qweqwe qwe'
                },
                {
                    message: 'SOME-234: qweqwe qwe\nmultistring'
                },
                {
                    message: 'WTF-0: skip it'
                },
                {
                    message: 'WTF-1: skip it'
                },
                {
                    message: 'skip it too'
                },
                {
                    message: 'SOME-2334: qweqwe qwe\nmultistring\nticket key in TEXT-123'
                },
                {
                    message: 'SOME-111:with no space\n\tSOME-133not here'
                }
            ]);
            expect(res).to.deep.equal([
                'SOME-111',
                'SOME-123',
                'SOME-2334',
                'SOME-234',
                'TEXT-123'
            ], res);
        });

        it('выбирает коммиты с нужным знаком', () => {
            const res = extractTickets([
                {
                    mark: '=',
                    message: 'SOME-123: qweqwe qwe'
                },
                {
                    mark: '*',
                    message: 'SOME-234: qweqwe qwe\nmultistring'
                },
                {
                    mark: '=',
                    message: 'SOME-2334: qweqwe qwe\nmultistring\nticket key in TEXT-123'
                },
                {
                    mark: '*',
                    message: 'SOME-111:with no space\n\tSOME-133not here'
                }
            ], '=');
            expect(res).to.deep.equal([
                'SOME-123',
                'SOME-2334',
                'TEXT-123'
            ], res);
        });
    });

    describe('sortVersions', () => {
        it('semver', () => {
            expect(sortVersions([
                '0.0.1',
                '0.1.1',
                '0.10.1',
                '0.1.10',
                '1.0.0',
                '0.1',
                '0.0.a'
            ])).to.deep.equal([
                '0.0.1',
                '0.0.a',
                '0.1',
                '0.1.1',
                '0.1.10',
                '0.10.1',
                '1.0.0'
            ]);
        });

        it('даты', () => {
            expect(sortVersions([
                '2019-01-12',
                '2019-01-13',
                '2018-01-13',
                '2018-11-13'
            ])).to.deep.equal([
                '2018-01-13',
                '2018-11-13',
                '2019-01-12',
                '2019-01-13'
            ]);
        });

        it('даты с префиксами', () => {
            expect(sortVersions([
                'qwe-2019-01-12',
                'qwe-2019-01-13',
                'qwe-2017-03-13',
                'qwe-2018-11-13',
                'rty-2019-01-12',
                'rty-2017-01-13',
                'rty-2018-04-13',
                'rty-2018-11-13'
            ])).to.deep.equal([
                'qwe-2017-03-13',
                'qwe-2018-11-13',
                'qwe-2019-01-12',
                'qwe-2019-01-13',
                'rty-2017-01-13',
                'rty-2018-04-13',
                'rty-2018-11-13',
                'rty-2019-01-12'
            ]);
        });

        it('версии разной длинны', () => {
            expect(sortVersions([
                'qwe-2019-01-12',
                'qwe-2019-01-13-1',
                'qwe-2019-01-13-1.bugfix2',
                'qwe-2019-01-13-2.bugfix2',
                'qwe-2017-03-13',
                'qwe-2019-01-13-2',
                'qwe-2019-01-13-1.bugfix',
                'qwe-2018-11-13'
            ])).to.deep.equal([
                'qwe-2017-03-13',
                'qwe-2018-11-13',
                'qwe-2019-01-12',
                'qwe-2019-01-13-1',
                'qwe-2019-01-13-1.bugfix',
                'qwe-2019-01-13-1.bugfix2',
                'qwe-2019-01-13-2',
                'qwe-2019-01-13-2.bugfix2'
            ]);
        });
    });
});
