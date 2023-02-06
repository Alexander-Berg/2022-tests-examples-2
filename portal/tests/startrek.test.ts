import {expect} from 'chai';
import sinon from 'sinon';
import nock from 'nock';
import {Project} from '../lib/config';
import {
    getStartrekIssueMock,
    getWorkflowMock
} from './mocks';
import {StartrekIssue} from '../lib/startrek';

const testContent = `ololo

==== Ресурсы

- ((some.url/1 SOME_RES_TARBALL=1.234.olole-6))
- ((some.url/2 OTHER=1.1.1.1))

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

describe('startrek', () => {
    class Noop extends StartrekIssue {
        _start() {
            return Promise.resolve({
                appVersion: '123',
                tags: ['urelease:fake'],
                relatedIssues: [],
                linkedIssues: [],
                artifacts: [],
                followers: [],
                userComments: '// Место для записей человеком',
                commits: ''
            });
        }
    }

    describe('parseExisting', () => {
        let instance, parsed;
        before(() => {
            instance = new Noop({
                project: 'noop-project',
                queue: 'SOME',
                version: '123',
                prevVersion: '122',
                refLink: 'st.to/123',
                prevRefLink: 'st.to/122',
                duty: []
            }, getWorkflowMock());
            parsed = instance._parseExisting({
                summary: '123123',
                key: {
                    id: 'SOME-123'
                },
                tags: [],
                description: testContent
            });
        });

        it('получает список коммитов', () => {
            expect(parsed.commits).to.deep.equal(`<{qweqwe
- ⦻ ((https://some/path/124 SOME-345: zxc cvn))
- %%SOME-123: Qwe rty asd
dfg%%
- %%SOME-345: zxc cvn%%
- ⦿ ((https://some/path/123 SOME-345: zxc cvn))
}>`);
        });

        it('получает список ресурсов', () => {
            expect(parsed.artifacts).to.deep.equal([
                {
                    name: 'SOME_RES_TARBALL=1.234.olole-6',
                    url: 'some.url/1',
                    type: 'resource'
                },
                {
                    name: 'OTHER=1.1.1.1',
                    url: 'some.url/2',
                    type: 'resource'
                }
            ]);
        });

        it('получает ручные заметки', () => {
            expect(parsed.userComments).to.equal('ololo');
        });
    });

    describe('виды релизов', function () {

        const writestub = sinon.stub();
        class ReadonlyIssue extends StartrekIssue {
            _writeFake: <T>(issue: T) => T

            constructor(params, workflow, writeFake) {
                super(params, workflow);

                this._writeFake = writeFake;
            }

            async _write(issue) {
                return await this._writeFake(issue);
            }
        }
        describe('обычный релиз', () => {
            let stApi;
            let workflow;
            beforeEach(() => {
                process.env.STARTREK_TOKEN = 'faketoken';
                workflow = getWorkflowMock();
                stApi = nock('https://st-api.yandex-team.ru')
                    .persist()
                    .get('/v2/issues')
                    .query(true)
                    .reply(200, () => {
                        console.log('request nocked');
                        return [];
                    });
            });

            afterEach(() => {
                nock.cleanAll();
            });

            it('обычный релиз', async () => {
                const instance = new ReadonlyIssue({
                    project: 'morda',
                    version: '1234',
                    prevVersion: '1230',
                    queue: 'HOME'
                }, workflow, issue => {
                    return issue;
                });

                await instance.getKey();
                expect(instance.kind).to.equal('normal');
            });
        });

        describe('докатка', () => {
            let stApi;
            let linkedIssues;
            let workflow;
            beforeEach(() => {
                process.env.STARTREK_TOKEN = 'faketoken';
                workflow = getWorkflowMock();
                stApi = nock('https://st-api.yandex-team.ru')
                    .persist()
                    .get('/v2/issues')
                    .query(params => {
                        if (params.query) {
                            return true;
                        } else {
                            return false;
                        }
                    })
                    .reply(200, () => {
                        console.log('request nocked');
                        return [
                            getStartrekIssueMock({
                                appVersion: '1230'
                            })
                        ];
                    })
                    .get('/v2/issues')
                    .query(true)
                    .reply(200, () => {
                        console.log('linked info');
                        return [];
                    });

                linkedIssues = nock('https://st-api.yandex-team.ru')
                    .get('/v2/issues/HOME-00000/links')
                    .query(true)
                    .reply(200, () => {
                        console.log('linked');
                        return [];
                    });

            });

            afterEach(() => {
                nock.cleanAll();
            });
            it('выглядит как докатка', async () => {
                const instance = new ReadonlyIssue({
                    project: 'morda',
                    version: '1234',
                    prevVersion: '1230',
                    queue: 'HOME'
                }, workflow, issue => {
                    return issue;
                });

                await instance.getKey();
                expect(instance.kind).to.equal('appendix');
            });

            it('конкатенирует коммиты', async() => {
                const instance = new ReadonlyIssue({
                    project: 'morda',
                    version: '1234',
                    prevVersion: '1230',
                    queue: 'HOME'
                }, workflow, issue => {
                    expect(issue.commits).to.equal([
                        '- ⦿ ((/fakecommit/1236 QWE-117: normal commit))',
                        '- ⦿ ((/fakecommit/1235 QWE-111: 2nd normal commit))',
                        '**⸻ 1230 ⸻**',
                        '<{Развернуть',
                        '- ⦿ ((/mock/1 HOME-12345: test))',
                        '- ⦿ ((/mock/2 HOME-12346: test (2)))}>'
                    ].join('\n'));
                    return issue;
                });
                await instance.getKey();
            });
        });

        describe('багфикс', () => {
            let stApi;
            let linkedIssues;
            let workflow;
            beforeEach(() => {
                process.env.STARTREK_TOKEN = 'faketoken';
                workflow = getWorkflowMock();
                stApi = nock('https://st-api.yandex-team.ru')
                    .persist()
                    .get('/v2/issues')
                    .query(params => {
                        if (params.query) {
                            return true;
                        } else {
                            return false;
                        }
                    })
                    .reply(200, () => {
                        console.log('request nocked');
                        return [
                            getStartrekIssueMock({
                                appVersion: '1230'
                            })
                        ];
                    })
                    .get('/v2/issues')
                    .query(true)
                    .reply(200, () => {
                        console.log('linked info');
                        return [];
                    });

                linkedIssues = nock('https://st-api.yandex-team.ru')
                    .get('/v2/issues/HOME-00000/links')
                    .query(true)
                    .reply(200, () => {
                        console.log('linked');
                        return [];
                    });

            });

            afterEach(() => {
                nock.cleanAll();
            });
            it('выглядит как багфикс', async () => {
                const instance = new ReadonlyIssue({
                    project: 'morda',
                    version: '1234',
                    prevVersion: '1231',
                    queue: 'HOME'
                }, workflow, issue => {
                    return issue;
                });

                await instance.getKey();
                expect(instance.kind).to.equal('bugfix');
            });

            it('отбрасывает коммиты из открытого таска', async() => {
                const instance = new ReadonlyIssue({
                    project: 'morda',
                    version: '1234',
                    prevVersion: '1231',
                    queue: 'HOME'
                }, workflow, issue => {
                    expect(issue.commits).to.equal([
                        '- ⦿ ((/fakecommit/1236 QWE-117: normal commit))',
                        '- ⦿ ((/fakecommit/1235 QWE-111: 2nd normal commit))',
                        '**⸻ 1231 ⸻**'
                    ].join('\n'));
                    return issue;
                });
                await instance.getKey();
            });
        });
    });
});