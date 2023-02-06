// eslint-disable-next-line node/no-extraneous-require
const sinon = require('sinon');
const Stat = require('../lib/stat.js');
describe('stat', () => {
    let stat;

    const testParams = {
        logger: console,
        yandexuid: 1234567,
        hostname: 'testhost.name',
        ClckBase: 'https://testhost.name/mockclck',
        RequestId: '123.456.789.001',
        statRoot: 'testroot',
        dev: false,
        HomepageNoArgs: 'https://testpageno.args',
        adb: 0
    };

    function getSaved() {
        return stat._paths;
    }

    beforeEach(() => {
        stat = new Stat(testParams);
    });

    describe('setCounter', () => {
        it('flags.no_blockdisplay', () => {
            stat.setCounter('some.path', '', {noBlockDisplay: true});
            stat.setCounter('some.path1', 'https://ya.ru', {noBlockDisplay: true});
            stat.setCounter('some.path2', 'https://external.site', {noBlockDisplay: true});
            stat.setCounter('some.path3', '', {customParams: 'xxx', noBlockDisplay: true});
            stat.setCounter('some.path4', 'https://ya.ru', {customParams: 'xxx', noBlockDisplay: true});
            stat.setCounter('some.path5', 'https://external.site', {customParams: 'xxx', noBlockDisplay: true});
            stat.setCounter('some.path6', '', {customParams: {x: 1}, noBlockDisplay: true});
            stat.setCounter('some.path7', 'https://ya.ru', {customParams: {x: 1}, noBlockDisplay: true});
            stat.setCounter('some.path8', 'https://external.site', {customParams: {x: 1}, noBlockDisplay: true});

            expect(getSaved()).to.deep.equal({});
        });

        it('ничего не делает без пути', () => {
            expect(stat.setCounter('')).to.deep.equal({});
            expect(stat.setCounter('', 'https://ya.ru')).to.deep.equal({});

            expect(getSaved()).to.deep.equal({});
        });

        describe('редиректные счётчики', () => {
            function asssertOurCounter(res, path) {
                expect(res).to.have.all.keys('id', 'our', 'url');

                expect(res.id).to.equal('testroot.' + path);
                expect(res.our).to.equal(true);

                expect(res.url).to.match(new RegExp('^https://testhost.name/mockclck/redir/dtype=clck/lid=testroot.' +
                    path + '/sid=123.456.789.001/rnd=\\d+/table=morda/antiadb=[01]/\\*data=url%3Dhttps%253A%252F%252Fya.ru$'));
            }

            function asssertOuterCounter(res, path) {
                expect(res).to.have.all.keys('id', 'our', 'url');

                expect(res.id).to.equal('testroot.' + path);
                expect(res.our).to.equal(false);

                expect(res.url).to.match(/^https:\/\/testhost.name\/mockclck\/redir\//);

                expect(res.url).to.not.contain(path);
            }

            it('наши домены', () => {
                asssertOurCounter(stat.setCounter('some.path', 'https://ya.ru'), 'some.path');

                asssertOurCounter(stat.setCounter('some.path2', 'https://ya.ru', {customParams: 'xxx'}), 'some.path2');

                asssertOurCounter(stat.setCounter('some-path', 'https://ya.ru', {
                    customParams: {
                        q: 42,
                        x: 'xxx'
                    }
                }), 'some-path');

                expect(getSaved()).to.deep.equal({
                    'some.path': 0,
                    'some.path2': {id: 'xxx'},
                    'some-path': {q: 42, x: 'xxx'}
                });
            });

            it('внешние домены', () => {
                asssertOuterCounter(stat.setCounter('some.path', 'https://external.site'), 'some.path');

                asssertOuterCounter(stat.setCounter('some.path2', 'https://external.site', {customParams: 'xxx'}), 'some.path2');


                asssertOuterCounter(stat.setCounter('some-path', 'https://external.site', {
                    customParams: {
                        q: 42,
                        x: 'xxx'
                    }
                }), 'some-path');

                expect(getSaved()).to.deep.equal({
                    'some.path': 0,
                    'some.path2': {id: 'xxx'},
                    'some-path': {q: 42, x: 'xxx'}
                });
            });

        });

        it('обычные счётчики', () => {
            expect(stat.setCounter('some.path')).to.deep.equal({
                id: 'testroot.some.path',
                our: true,
                url: ''
            });

            expect(stat.setCounter('some.path2', '', {customParams: 'xxx'})).to.deep.equal({
                id: 'testroot.some.path2',
                our: true,
                url: ''
            });


            expect(stat.setCounter('some-path', '', {customParams: {q: 42, x: 'xxx'}})).to.deep.equal({
                id: 'testroot.some-path',
                our: true,
                url: ''
            });

            expect(getSaved()).to.deep.equal({
                'some.path': 0,
                'some.path2': {id: 'xxx'},
                'some-path': {q: 42, x: 'xxx'}
            });
        });
    });

    describe('fullpath', () => {
        it('добавляет рут', () => {
            stat.fullpath('some.path').should.equal('testroot.some.path');
            stat.fullpath('some-path2').should.equal('testroot.some-path2');
        });

        it('Возвращает BADID, если path не верный', () => {
            stat.fullpath('some..path').should.equal('BADID');
            stat.fullpath('some(qq=42)').should.equal('BADID');
        });
    });

    describe('save', () => {
        it('без параметров', () => {
            stat.save('some.path');
            expect(getSaved()).to.deep.equal({
                'some.path': 0
            });
        });

        it('с параметром-примитивом', () => {
            stat.save('some.path', 42);
            stat.save('some.path2', 'qwe');
            expect(getSaved()).to.deep.equal({
                'some.path': {id: 42},
                'some.path2': {id: 'qwe'}
            });
        });

        it('с параметром-объектом', () => {
            stat.save('some.path', {q: 42, z: 'xxx'});
            expect(getSaved()).to.deep.equal({
                'some.path': {q: 42, z: 'xxx'}
            });
        });

        it('игнорирует дубликаты', () => {
            stat.save('some.path', 42);
            stat.save('some.path');
            stat.save('some.path', 'qwe');
            expect(getSaved()).to.deep.equal({
                'some.path': {id: 42}
            });
        });
    });

    describe('report', () => {
        let log;
        let stat2;
        beforeEach(() => {
            log = sinon.stub();
            stat2 = new Stat({
                ...testParams,
                blockdisplayLogger: {
                    info: log
                }
            });
        });

        it('выводит накопленные блоки', () => {
            stat2.save('some.path');
            stat2.save('some-path', 42);
            stat2.save('some.path2', {x: 42, q: 'xxx'});

            stat2.report({});
            log.should.have.been.calledWith({
                blocks: 'testroot.some.path	0\t' +
                    'testroot.some-path\t1\tid=42\t' +
                    'testroot.some.path2\t2\tx=42\tq=xxx'
            });
        });

        it('выводит параметры', () => {
            stat2.report({
                params: {
                    xxx: 'y',
                    dashed_param: 'param=param; param\tparam; param\\param'
                }
            });
            log.should.have.been.calledWith({
                xxx: 'y',
                dashed_param: 'param=param; param\tparam; param\\param',
                blocks: ''
            });
        });

        it('выводит переданные блоки', () => {
            stat2.report({
                blocks: ['v1.qwe\t2\tx=y\tqqq=444', 'some.qwe\t0']
            });

            log.should.have.been.calledWith({
                blocks: 'v1.qwe\t2\tx=y\tqqq=444\tsome.qwe\t0'
            });
        });

        it('объединяет блоки', () => {
            stat2.save('some.path');
            stat2.save('some-path', 42);
            stat2.save('some.path2', {x: 42, q: 'xxx'});

            stat2.report({
                blocks: ['v1.qwe\t2\tx=y\tqqq=444', 'some.qwe\t0']
            });

            log.should.have.been.calledWith({
                blocks: 'v1.qwe\t2\tx=y\tqqq=444\t' +
                    'some.qwe\t0\t' +
                    'testroot.some.path	0\t' +
                    'testroot.some-path\t1\tid=42\t' +
                    'testroot.some.path2\t2\tx=42\tq=xxx'
            });
        });
    });
});
