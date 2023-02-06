const tskv = require('../lib/logger/tskv-layout');
const logConfig = {
    predefined: [
        'unixtime',
        'timestamp',
        'timezone',
        'pid',
        'level'
    ],
    always: {
        tskv_format: 'error-log-morda-node',
        xtest: 1
    }
};
describe('tskv-layout', function () {
    const getTestEvent = ({args = [], level = 'info'} = {}) => {
        return {
            startTime: new Date(123456789123),
            level,
            pid: 2345,
            data: args,
            context: {
                reqid: '345.456.567',
                somevar: -42
            }
        };
    };
    const testPrefix = 'tskv\ttskv_format=error-log-morda-node\txtest=1\t' +
        'unixtime=123456789\ttimestamp=1973-11-30 00:33:09\t' +
        'timezone=+0300\tpid=2345\tlevel=info\treqid=345.456.567\tsomevar=-42';

    it('записывает дефолтные поля', function () {
        tskv(logConfig)(getTestEvent())
            .should.equal(testPrefix);
    });

    it('склеивает все аргументы в message', function () {
        tskv(logConfig)(getTestEvent({
            args: [
                'str',
                ['array'],
                {object: false},
                false,
                -42
            ]
        }))
            .should.equal(testPrefix +
                '\tmessage=str ["array"] {"object":false} false -42');
    });

    it('раскладывает ключи первого аргумента, если это объект', function () {
        tskv(logConfig)(getTestEvent({
            args: [
                {object: false, smth: {x: 1}},
                'str',
                ['array'],
                false,
                -42
            ]
        }))
            .should.equal(testPrefix +
                '\tobject=false\tsmth={"x":1}\t' +
                'message=str ["array"] false -42');
    });

    it('экранирует спецсимволы', function () {
        tskv(logConfig)(getTestEvent({
            args: [
                {object: 'x\ty=z\n\rw=q', smth: {x: 'foo\tbar=baz'}},
                'baz\tbar=foo'
            ]
        }))
            .should.equal(testPrefix +
                '\tobject=x_y\\=z w\\=q\t' +
                'smth={"x":"foo\\tbar\\=baz"}\t' +
                'message=baz_bar\\=foo');
    });

    it('использует список predefined из конфига', function () {
        tskv({
            predefined: [
                'pid',
                'level'
            ]
        })({
            startTime: new Date(123456789123),
            level: 'error',
            pid: 2345,
            data: [
                'test'
            ]
        })
            .should.equal('tskv\tpid=2345\tlevel=error\tmessage=test');
    });

    it('логирует ошибки', function () {
        let err = new Error('error');
        err.stack = 'error at file';

        tskv({})({
            startTime: new Date(123456789123),
            level: 'error',
            pid: 2345,
            data: [
                err
            ]
        })
            .should.equal('tskv\tmessage=error\tstack=error at file');

        tskv({})({
            startTime: new Date(123456789123),
            level: 'error',
            pid: 2345,
            data: [
                {abc: 123},
                err
            ]
        })
            .should.equal('tskv\tabc=123\tmessage=error at file');

        let err2 = new Error('error');
        err2.stack = 'error at file';
        err2.source = 'my-block';
        tskv({})({
            startTime: new Date(123456789123),
            level: 'error',
            pid: 2345,
            data: [
                err2
            ]
        })
            .should.equal('tskv\tmessage=error\tstack=error at file\tsource=my-block');
    });

    it('избавляется от дубликатов', function () {
        tskv(logConfig)({
            startTime: new Date(123456789123),
            level: 'info',
            pid: 2345,
            context: {
                reqid: '345.456.567',
                somevar: -42
            },
            data: [{
                xtest: 111,
                somevar: 12,
                message: 'qq'
            }]
        }).should.equal([
            'tskv',
            'tskv_format=error-log-morda-node',
            'xtest=111',
            'unixtime=123456789',
            'timestamp=1973-11-30 00:33:09',
            'timezone=+0300',
            'pid=2345',
            'level=info',
            'reqid=345.456.567',
            'somevar=12',
            'message=qq',
            'additional={"_overriden":"xtest,somevar"}'
        ].join('\t'));
    });

    it('совмещает additional', function () {
        tskv(logConfig)({
            startTime: new Date(123456789123),
            level: 'info',
            pid: 2345,
            context: {
                reqid: '345.456.567',
                somevar: -42,
                additional: {
                    qwe: 'rty',
                    xxx: 1
                }
            },
            data: [{
                additional: {
                    asd: 'fgh',
                    xxx: 2
                },
                message: 'qq'
            }]
        }).should.equal([
            testPrefix,
            'message=qq',
            'additional={"asd":"fgh","xxx":2,"qwe":"rty","_overriden":"additional.xxx"}'
        ].join('\t'));
    });
});
