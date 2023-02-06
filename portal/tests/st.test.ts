import {
    parseList,
    parseCut,
    parseCommits,
    filterTaskNames,
    mergeCommits,
    parseSection,
    formatCommits,
    formatRest,
    parseSections,
    section
} from '../lib/st';

import {expect} from 'chai';
import type {CommitInfo} from '../lib/config-types';

const testContent = `ololo

==== Ресурсы

SOME_RES_TARBALL=1.234.olole-6
OTHER=1.1.1.1

==== Коммиты

<{qweqwe
- ⦻ ((https://some/path/124 SOME-345: zxc cvn))
- %%SOME-123: Qwe rty asd
dfg%%
- %%SOME-345: zxc cvn%%
- ⦿ ((https://some/path/123 SOME-345: zxc cvn))
}>

==== Задачи

<{qweqwe
- %%SOME-123%%
- %%SOME-354%%
}>

#### Примечания разработки

<{qweqwe
- %%SOME-456%% AAaaaaaaaa
qweqweqwe ertert
- %%QWE-12%% TYUTY
nnn
sdfsdf
}>`;

describe('st', () => {
    describe('parseSections', () => {
        it('#1', () => {
            const sections = parseSections(testContent, '[=#]{4}');

            expect(sections).to.be.an('array')
                .and.deep.equal([
                    {
                        header: '',
                        text: 'ololo'
                    },
                    {
                        'header': 'Ресурсы',
                        'text': 'SOME_RES_TARBALL=1.234.olole-6\nOTHER=1.1.1.1'
                    },
                    {
                        'header': 'Коммиты',
                        'text': '<{qweqwe\n- ⦻ ((https://some/path/124 SOME-345: zxc cvn))\n' +
                            '- %%SOME-123: Qwe rty asd\ndfg%%\n- %%SOME-345: zxc cvn%%\n' +
                            '- ⦿ ((https://some/path/123 SOME-345: zxc cvn))\n}>'
                    },
                    {
                        'header': 'Задачи',
                        'text': '<{qweqwe\n- %%SOME-123%%\n- %%SOME-354%%\n}>'
                    },
                    {
                        'header': 'Примечания разработки',
                        'text': '<{qweqwe\n- %%SOME-456%% AAaaaaaaaa\nqweqweqwe ertert\n- %%QWE-12%% TYUTY\nnnn\nsdfsdf\n}>'
                    }
                ]);
        });

        it('#2', () => {
            const parsed = parseSections(`ololo

==== QWEQWE

- dfgsd
- dgsdfg

#### EEE

- dfgdfg
- dfg dfg
- drgd ## 555 ##

`, '[#=]{4}');

            expect(parsed).to.deep.equal([
                {
                    header: '',
                    text: 'ololo'
                },
                {
                    header: 'QWEQWE',
                    text: '- dfgsd\n- dgsdfg'
                },
                {
                    header: 'EEE',
                    text: '- dfgdfg\n- dfg dfg\n- drgd ## 555 ##'
                }
            ]);
        });
    });

    describe('parseSection', () => {
        it('список с катом', () => {
            expect(parseSection([
                '<{Кат',
                '- один',
                '- многострочный\nпункт',
                '* три',
                '}>'
            ].join('\n'))).to.be.an('array')
                .and.deep.equal([
                    'один',
                    'многострочный\nпункт',
                    'три'
                ]);

        });

        it('список без ката', () => {
            expect(parseSection([
                '- один',
                '- многострочный\nпункт',
                '* три'
            ].join('\n'))).to.be.an('array')
                .and.deep.equal([
                    'один',
                    'многострочный\nпункт',
                    'три'
                ]);
        });

        it('не список', () => {
            expect(parseSection('Some\nlong\ntext'))
                .to.be.an('array')
                .and.deep.equal([
                    'Some\nlong\ntext'
                ]);
        });
    });

    describe('парсит списки', () => {
        it('через -', () => {
            const parsed = parseList(`
- dfgsd
- dgsdfg
`);

            expect(parsed).to.deep.equal([
                'dfgsd',
                'dgsdfg'
            ]);
        });

        it('через *', () => {
            const parsed = parseList(`
* dfgsd
* dgsdfg
`);

            expect(parsed).to.deep.equal([
                'dfgsd',
                'dgsdfg'
            ]);
        });

        it('многострочные пункты', () => {
            const parsed = parseList(`
* dfgsd
ololoe
* dgsdfg
    padded
`);

            expect(parsed).to.deep.equal([
                'dfgsd\nololoe',
                'dgsdfg\n    padded'
            ]);
        });
    });

    describe('парсит кат', () => {
        it('с заголовком', () => {
            const parsed = parseCut(`
<{title
ololo
- list
- item
}>`);
            expect(parsed).to.equal('ololo\n- list\n- item');
        });

        it('без заголовка', () => {
            const parsed = parseCut(`
<{
ololo
- list
- item
}>`);
            expect(parsed).to.equal('ololo\n- list\n- item');
        });
    });

    describe('дописывание секций', function () {
        describe('коммитов', function () {
            it.skip('тесты?', function () {
            });
        });

        describe('тасков', function () {
            it.skip('тесты?', function () {
            });
        });
    });

    describe('section', function () {
        it('создаёт озаглавленные списки', () => {
            expect(section('тест', ['foo', 'bar']))
                .to.equal('==== тест\n\n- foo\n- bar\n');
        });
        it('не создаёт список из одного элемента', () => {
            expect(section('тест', ['foo']))
                .to.equal('==== тест\n\nfoo\n');
        });

        it('создаёт список c катом для 11 и более элементов', () => {
            const list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'];
            expect(section('тест', list))
                .to.equal(`==== тест\n\n<{Развернуть\n${list.map(s => `- ${s}`).join('\n')}}>\n`);
        });

        it('создаёт список c катом для 11 и более строк', () => {
            const list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'].join('\n');
            expect(section('тест', [list]))
                .to.equal(`==== тест\n\n<{Развернуть\n${list}}>\n`);
        });
    });

    describe('formatCommits', () => {
        it('однострочные', () => {
            expect(formatCommits([{url: 'github.url/1234', message: 'Some text'}]))
                .to.deep.equal(['((github.url/1234 Some text))']);
        });

        it('многострочные', () => {
            expect(formatCommits([{url: 'github.url/1234', message: 'Some text\nwith line\nbreaks'}]))
                .to.deep.equal(['((github.url/1234 Some text))']);
        });

        it('со знаком', () => {
            expect(formatCommits([
                {mark: '*', url: 'github.url/1234', message: 'added'},
                {mark: '=', url: 'github.url/1234', message: 'equal'},
                {mark: 'x', url: 'github.url/1234', message: 'removed'},
                {mark: '-', url: 'github.url/1234', message: 'boundary'}
            ]))
                .to.deep.equal([
                    '⦿ ((github.url/1234 added))',
                    '⊜ ((github.url/1234 equal))',
                    '⦻ ((github.url/1234 removed))',
                    '⦹ ((github.url/1234 boundary))'
                ]);
        });

        it('со знаком без урла', () => {
            expect(formatCommits([{mark: '*', message: 'Some text'}]))
                .to.deep.equal(['⦿ Some text']);
        });

        it('без знака и хэша', () => {
            expect(formatCommits([{message: 'Some text'}]))
                .to.deep.equal(['Some text']);
        });
    });

    describe('formatRest', () => {
        it('однострочные', () => {
            expect(formatRest('SOME-123', 'Some text'))
                .to.equal('((https://st.yandex-team.ru/SOME-123 SOME-123)) Some text');
        });

        it('многострочные', () => {
            expect(formatRest('SOME-123', 'Some text\nwith line\nbreaks'))
                .to.equal('((https://st.yandex-team.ru/SOME-123 SOME-123)) Some text\n\twith line\n\tbreaks');
        });
    });

    describe('parseCommits', () => {
        it('со знаками', () => {
            expect(parseCommits([
                '+ ((https://some/place/face8d Тут что-то есть))',
                '⦻ ((https://some/place/034bdf HOME-0: zzzz))',
                '⊜ ((https://some/place/970c10 smth))',
                '⦿ ((https://some/place/914015 111111))',
                '⦹ ((https://some/place/11111 start))'
            ]))
                .to.deep.equal([{
                    mark: '*',
                    hash: 'face8d',
                    url: 'https://some/place/face8d',
                    message: 'Тут что-то есть'
                },
                {
                    mark: 'x',
                    hash: '034bdf',
                    url: 'https://some/place/034bdf',
                    message: 'HOME-0: zzzz'
                },
                {
                    mark: '=',
                    hash: '970c10',
                    url: 'https://some/place/970c10',
                    message: 'smth'
                },
                {
                    mark: '*',
                    hash: '914015',
                    url: 'https://some/place/914015',
                    message: '111111'
                },
                {
                    mark: '-',
                    hash: '11111',
                    url: 'https://some/place/11111',
                    message: 'start'
                }]);
        });

        it('без знаков', () => {
            expect(parseCommits(['((https://some/place/face8d Тут что-то есть))']))
                .to.deep.equal([{
                    mark: '*',
                    hash: 'face8d',
                    url: 'https://some/place/face8d',
                    message: 'Тут что-то есть'
                }]);
        });

        it('со сломаным хэшом', () => {
            expect(parseCommits(['((https://some/place/qweqwe Тут что-то есть))']))
                .to.deep.equal([{
                    mark: '*',
                    url: 'https://some/place/qweqwe',
                    hash: undefined,
                    message: 'Тут что-то есть'
                }]);
        });
    });

    describe('filterTaskNames', () => {
        const names = [
            'HOME-1',
            'HOME-2',
            'HOME-3',
            'QWE-123',
            'QWE-234',
            'QWE-555',
            'XXX-555'
        ];

        it('название очереди не передано', () => {
            expect(names.filter(filterTaskNames())).to.be.an('array')
                .and.deep.equal(names);
        });

        it('название очереди - пустая строка', () => {
            expect(names.filter(filterTaskNames(''))).to.be.an('array')
                .and.deep.equal(names);
        });

        it('название очереди - пустой массив', () => {
            expect(names.filter(filterTaskNames([]))).to.be.an('array')
                .and.deep.equal(names);
        });

        it('название очереди - строка', () => {
            expect(names.filter(filterTaskNames('HOME'))).to.be.an('array')
                .and.deep.equal([
                    'HOME-1',
                    'HOME-2',
                    'HOME-3'
                ]);

            expect(names.filter(filterTaskNames('XXX'))).to.be.an('array')
                .and.deep.equal([
                    'XXX-555'
                ]);

            expect(names.filter(filterTaskNames('OLE'))).to.be.an('array')
                .and.deep.equal([]);
        });

        it('название очереди - масссив', () => {
            expect(names.filter(filterTaskNames(['HOME', 'QWE']))).to.be.an('array')
                .and.deep.equal([
                    'HOME-1',
                    'HOME-2',
                    'HOME-3',
                    'QWE-123',
                    'QWE-234',
                    'QWE-555'
                ]);

            expect(names.filter(filterTaskNames(['XXX', 'OLA']))).to.be.an('array')
                .and.deep.equal([
                    'XXX-555'
                ]);

            expect(names.filter(filterTaskNames(['OLE', 'OLA']))).to.be.an('array')
                .and.deep.equal([]);
        });
    });

    describe('mergeCommits', () => {
        const hashToCommit = mark => hash => ({mark, hash, message: 'test'}),
            add = [1, 2, 3, 4].map(hashToCommit('*')),
            remove = [5, 6, 7, 8].map(hashToCommit('x')),
            equal = [9, 10, 11, 12].map(hashToCommit('=')),
            noSign = [13, 14, 15, 16].map(hashToCommit(''));

        it('сохраняет порядок нормальных коммитов', () => {
            expect(mergeCommits(add.slice(2), add.slice(0, 2)))
                .to.deep.equal(add);
        });

        it('сохраняет порядок нормальных и равных коммитов', () => {
            expect(mergeCommits(add.slice(2), ([] as CommitInfo[]).concat(equal, add.slice(0, 2))))
                .to.deep.equal([
                    ...equal,
                    ...add.slice(0, 2),
                    ...add.slice(2)
                ]);
        });

        it('исключает удалённые коммиты, которые были встречены в старых', () => {
            expect(mergeCommits([
                ...add.slice(2),
                ...[5, 6].map(hashToCommit('*'))
            ],
            [
                ...remove.slice(0, 2),
                ...add.slice(0, 2)
            ]))
                .to.deep.equal(add);
        });

        it('добавляет в конец удалённые коммиты, которые не были встречены в старых', () => {
            expect(mergeCommits([
                ...add.slice(2)
            ],
            [
                ...remove.slice(0, 2),
                ...add.slice(0, 2)
            ]))
                .to.deep.equal([
                    ...add,
                    ...remove.slice(0, 2)
                ]);
        });

        it('обрабатывает коммиты без знака', () => {
            expect(mergeCommits(noSign, add))
                .to.deep.equal([
                    ...add,
                    ...noSign
                ]);
        });
    });
});
