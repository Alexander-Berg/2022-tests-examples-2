/* eslint-disable max-len */
import {
    castArray,
    createStream,
    errorBoosterFormatter,
    ErrorBoosterFormatterOptions,
    ErrorBoosterMeta,
    errorResolver,
    Logger,
    parseYaTaxiUserHeader,
    requestResolver,
    stringifyJson,
    stringifyTskv,
    tariffEditorCommonResolver,
    taxiFormatter,
    TaxiFormatterOptions,
    TaxiKibanaMeta,
    Transport,
    WithExpressReq
} from '.';

class TestError extends Error {}

describe('package "logger"', () => {
    it('should log message', () => {
        const {transport, logs} = createTaxiArrayTransport();
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.info('foo');

        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=foo\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);

        // @ts-expect-error unexpected "bar" property
        logger.info('foo', {bar: 'baz'});

        // @ts-expect-error empty call
        logger.info();

        const child = logger.child({foo: 'bar'});
        child.info({foo: 'baz'});
        child.info({foo: 'baz', text: 'test'});

        // @ts-expect-error unknown property
        child.info({bar: 'baz'});
        // @ts-expect-error unknown property
        child.info({foo: 'baz', text_foo: 'test'});
    });

    it('should log typed message', () => {
        type Message = 'foo' | 'test';
        const {transport, logs} = createTaxiArrayTransport();
        const logger = new Logger<TaxiKibanaMeta, Message>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.info('foo');
        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=foo\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);

        // @ts-expect-error empty call
        logger.info();

        logger.info({msg: 'foo'});

        // @ts-expect-error unknown property
        logger.info({msg: 'baz'});

        // @ts-expect-error unknown property
        logger.info('baz');

        const child = logger.child({foo: 'bar'});
        child.info('test', {foo: 'bar'});

        // @ts-expect-error unknown property
        child.info('baz', {foo: 'bar'});
    });

    it('should handle log level', () => {
        let {transport, logs} = createTaxiArrayTransport();
        let logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'fatal', transport})
        });

        logger.trace('1');
        logger.debug('2');
        logger.info('3');
        logger.warn('4');
        logger.error('5');
        logger.fatal('6');

        tskvEqual(logs, [
            'tskv\tlevel=FATAL\tmsg=6\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);

        ({transport, logs} = createTaxiArrayTransport());
        logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'trace', transport})
        });

        logger.trace('1');
        logger.debug('2');
        logger.info('3');
        logger.warn('4');
        logger.error('5');
        logger.fatal('6');

        tskvEqual(logs, [
            'tskv\tlevel=TRACE\tmsg=1\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=DEBUG\tmsg=2\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=INFO\tmsg=3\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=WARN\tmsg=4\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=ERROR\tmsg=5\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=FATAL\tmsg=6\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);
    });

    it('should handle "commonMeta" and "meta"', () => {
        const {transport, logs} = createTaxiArrayTransport({
            onInvalidProperty: {accept: true},
            afterFormat: (report) => {
                delete report['hostname'];
            }
        });
        const logger = new Logger({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests', foo: 'bar', baz: 'qux'},
            stream: createStream({level: 'info', transport})
        });

        logger.info({duck: 'quack', goose: 'honk'});
        logger.info({foo: 'overridden'});

        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=\tname=test\tversion=0.0.0\tenv=tests\tfoo=bar\tbaz=qux\tduck=quack\tgoose=honk\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=INFO\tmsg=\tname=test\tversion=0.0.0\tenv=tests\tfoo=overridden\tbaz=qux\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);

        // @ts-expect-error deprecated "msg" property
        logger.info('foo', {msg: 'bar'});

        // @ts-expect-error deprecated "err" property
        logger.info(new Error('test'), {err: 'test'});
    });

    it('should handle "extendCommonMeta" method', () => {
        const {transport, logs} = createTaxiArrayTransport();
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.extendCommonMeta({acceptlang: 'ru'});
        logger.info('baz');

        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=baz\tname=test\tversion=0.0.0\tenv=tests\tacceptlang=ru\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);
    });

    it('should handle "child" method', () => {
        const {transport, logs} = createTaxiArrayTransport();
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport, resolver: tariffEditorCommonResolver()})
        });

        logger.info('OOGA', {req: {}});

        const child = logger.child<WithExpressReq<TaxiKibanaMeta>>({
            feature: 'coolFeature',
            address: 'myAddress',
            req: {
                method: 'PATCH'
            }
        });

        child.info('MOOGA');

        child.info('BOOGA', {
            address: 'momsAddress'
        });

        tskvEqual(logs, [
            'tskv\ttimestamp=2021-07-30T11:07:16+03:00\tlevel=INFO\tmsg=OOGA\tname=test\tversion=0.0.0\tenv=tests',
            'tskv\ttimestamp=2021-07-30T11:07:16+03:00\tlevel=INFO\tmsg=MOOGA\tname=test\tversion=0.0.0\tenv=tests\tfeature=coolFeature\taddress=myAddress\tmethod=PATCH',
            'tskv\ttimestamp=2021-07-30T11:07:16+03:00\tlevel=INFO\tmsg=BOOGA\tname=test\tversion=0.0.0\tenv=tests\tfeature=coolFeature\taddress=momsAddress\tmethod=PATCH'
        ]);
    });

    it('should handle "errorResolver"', () => {
        const {transport, logs} = createTaxiArrayTransport();
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport, resolver: errorResolver({errorStack: false})})
        });

        logger.info(new TestError('Test Error!'));

        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=Test Error!\tname=test\tversion=0.0.0\tenv=tests\terror_msg=Error: Test Error!\terror_code=Error\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);
    });

    it('should handle "requestResolver"', () => {
        const {transport, logs} = createTaxiArrayTransport();
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport, resolver: requestResolver()})
        });

        logger.info({
            req: {
                method: 'POST',
                url: '/foo/bar',
                headers: {
                    host: 'https://ya.ru',
                    'x-real-ip': '192.168.0.1',
                    'x-forwarded-for': '0.0.0.0'
                }
            }
        });

        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=\tname=test\tversion=0.0.0\tenv=tests\tmethod=POST\turl=/foo/bar\thost=https://ya.ru\tremote_ip=x_real_ip=192.168.0.1; x_forwarded_for=0.0.0.0\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);
    });

    it('should handle multiple transports', () => {
        const {transport: transportA, logs} = createTaxiArrayTransport();
        const {transport: transportB} = createTaxiArrayTransport({logs});
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport: [transportA, transportB]})
        });

        logger.info('foo');

        tskvEqual(logs, [
            'tskv\tlevel=INFO\tmsg=foo\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00',
            'tskv\tlevel=INFO\tmsg=foo\tname=test\tversion=0.0.0\tenv=tests\ttimestamp=2021-07-30T11:07:16+03:00'
        ]);
    });

    it('should handle error booster formatter', () => {
        const {transport, logs} = createErrorBoosterArrayTransport({
            onInvalidProperty: {drop: true}
        });
        const logger = new Logger<ErrorBoosterMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0'},
            stream: createStream({level: 'info', transport})
        });

        logger.info('test');
        logger.info({additional: {foo: 'bar'}});

        tskvEqual(logs, [
            '{"level":"info","version":"0.0.0","timestamp":1650361979824,"project":"test","message":"test"}',
            '{"level":"info","version":"0.0.0","additional":{"foo":"bar"},"timestamp":1650361979824,"project":"test","message":""}'
        ]);
    });

    it('should handle taxi formatter "assignTo" option', () => {
        const {transport, logs} = createTaxiArrayTransport({
            onInvalidProperty: {drop: {hostname: true}, assignTo: 'value'}
        });
        const logger = new Logger({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.info({foo: 'bar', baz: 'qux'});

        tskvEqual(logs, [
            'tskv\ttimestamp=2021-07-30T11:07:16+03:00\tlevel=INFO\tmsg=\tname=test\tversion=0.0.0\tenv=tests\tvalue=foo=bar; baz=qux'
        ]);
    });

    it('should handle error booster formatter "assignToAdditional" option', () => {
        const {logs, transport} = createErrorBoosterArrayTransport({
            onInvalidProperty: {
                drop: {hostname: true, pid: true},
                assignToAdditional: true
            }
        });
        const logger = new Logger({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.info({foo: 'bar', baz: 'qux'});

        expect(logs).toEqual([
            '{"level":"info","version":"0.0.0","env":"tests","additional":{"foo":"bar","baz":"qux"},"timestamp":1650361979824,"project":"test","message":""}'
        ]);
    });

    it('should handle error booster formatter "beforeFormat" option', () => {
        const {logs, transport} = createErrorBoosterArrayTransport({
            onInvalidProperty: {drop: true},
            beforeFormat: (report) => {
                report.project = 'foo';
                delete report.env;
            }
        });
        const logger = new Logger<ErrorBoosterMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'testing'},
            stream: createStream({level: 'info', transport})
        });

        logger.info({message: 'test'});

        expect(logs).toEqual([
            '{"level":"info","version":"0.0.0","message":"test","project":"foo","timestamp":1650361979824}'
        ]);
    });

    it('should handle error booster formatter "afterFormat" option', () => {
        const {logs, transport} = createErrorBoosterArrayTransport({
            onInvalidProperty: {drop: true},
            afterFormat: (report) => {
                report.project = 'foo';
                delete report.env;
            }
        });
        const logger = new Logger<ErrorBoosterMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'testing'},
            stream: createStream({level: 'info', transport})
        });

        logger.info({message: 'test'});

        expect(logs).toEqual([
            '{"level":"info","version":"0.0.0","message":"test","timestamp":1650361979824,"project":"foo"}'
        ]);
    });

    it('should handle taxi formatter "beforeFormat" option', () => {
        const {transport, logs} = createTaxiArrayTransport({
            beforeFormat: (report) => {
                report.name = 'foo';
                delete report.env;
            }
        });
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.info('test');

        tskvEqual(logs, ['tskv\ttimestamp=2021-07-30T11:07:16+03:00\tlevel=INFO\tmsg=test\tname=foo\tversion=0.0.0']);
    });

    it('should handle taxi formatter "afterFormat" option', () => {
        const {transport, logs} = createTaxiArrayTransport({
            afterFormat: (report) => {
                report.name = 'foo';
                delete report.env;
            }
        });
        const logger = new Logger<TaxiKibanaMeta>({
            name: 'test',
            commonMeta: {version: '0.0.0', env: 'tests'},
            stream: createStream({level: 'info', transport})
        });

        logger.info('test');

        tskvEqual(logs, ['tskv\ttimestamp=2021-07-30T11:07:16+03:00\tlevel=INFO\tmsg=test\tname=foo\tversion=0.0.0']);
    });

    it('should check call signature required types', () => {
        const {transport} = createTaxiArrayTransport();
        const logger = new Logger<{foo: string}>({
            name: 'test',
            stream: createStream({level: 'info', transport})
        });

        logger.trace('test', {foo: 'bar'});
        logger.debug('test', {foo: 'bar'});
        logger.info('test', {foo: 'bar'});
        logger.warn('test', {foo: 'bar'});
        logger.error('test', {foo: 'bar'});
        logger.fatal('test', {foo: 'bar'});

        // @ts-expect-error disallowed meta property
        logger.trace('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.debug('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.info('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.warn('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.error('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.fatal('test', {bar: 'baz'});

        // @ts-expect-error missed required meta
        logger.trace('test');
        // @ts-expect-error missed required meta
        logger.debug('test');
        // @ts-expect-error missed required meta
        logger.info('test');
        // @ts-expect-error missed required meta
        logger.warn('test');
        // @ts-expect-error missed required meta
        logger.error('test');
        // @ts-expect-error missed required meta
        logger.fatal('test');

        logger.trace(new TestError('Test Error!'), {foo: 'bar'});
        logger.debug(new TestError('Test Error!'), {foo: 'bar'});
        logger.info(new TestError('Test Error!'), {foo: 'bar'});
        logger.warn(new TestError('Test Error!'), {foo: 'bar'});
        logger.error(new TestError('Test Error!'), {foo: 'bar'});
        logger.fatal(new TestError('Test Error!'), {foo: 'bar'});

        // @ts-expect-error disallowed meta property
        logger.trace(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.debug(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.info(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.warn(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.error(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.fatal(new TestError('Test Error!'), {bar: 'baz'});

        // @ts-expect-error missed required meta
        logger.trace(new TestError('Test Error!'));
        // @ts-expect-error missed required meta
        logger.debug(new TestError('Test Error!'));
        // @ts-expect-error missed required meta
        logger.info(new TestError('Test Error!'));
        // @ts-expect-error missed required meta
        logger.warn(new TestError('Test Error!'));
        // @ts-expect-error missed required meta
        logger.error(new TestError('Test Error!'));
        // @ts-expect-error missed required meta
        logger.fatal(new TestError('Test Error!'));
    });

    it('should check call signature optional types', () => {
        const {transport} = createTaxiArrayTransport();
        const logger = new Logger<{foo?: string}>({
            name: 'test',
            stream: createStream({level: 'info', transport})
        });

        logger.trace('test', {foo: 'bar'});
        logger.debug('test', {foo: 'bar'});
        logger.info('test', {foo: 'bar'});
        logger.warn('test', {foo: 'bar'});
        logger.error('test', {foo: 'bar'});
        logger.fatal('test', {foo: 'bar'});

        // @ts-expect-error disallowed meta property
        logger.trace('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.debug('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.info('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.warn('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.error('test', {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.fatal('test', {bar: 'baz'});

        logger.trace('test');
        logger.debug('test');
        logger.info('test');
        logger.warn('test');
        logger.error('test');
        logger.fatal('test');

        logger.trace(new TestError('Test Error!'), {foo: 'bar'});
        logger.debug(new TestError('Test Error!'), {foo: 'bar'});
        logger.info(new TestError('Test Error!'), {foo: 'bar'});
        logger.warn(new TestError('Test Error!'), {foo: 'bar'});
        logger.error(new TestError('Test Error!'), {foo: 'bar'});
        logger.fatal(new TestError('Test Error!'), {foo: 'bar'});

        // @ts-expect-error disallowed meta property
        logger.trace(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.debug(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.info(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.warn(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.error(new TestError('Test Error!'), {bar: 'baz'});
        // @ts-expect-error disallowed meta property
        logger.fatal(new TestError('Test Error!'), {bar: 'baz'});

        logger.trace(new TestError('Test Error!'));
        logger.debug(new TestError('Test Error!'));
        logger.info(new TestError('Test Error!'));
        logger.warn(new TestError('Test Error!'));
        logger.error(new TestError('Test Error!'));
        logger.fatal(new TestError('Test Error!'));
    });

    describe('parseYaTaxiUserHeader', () => {
        it('should work with empty value', () => {
            const result = parseYaTaxiUserHeader();

            expect(Object.keys(result)).toHaveLength(0);
        });
        it('should work', () => {
            const result = parseYaTaxiUserHeader('personal_phone_id=12345');

            expect(result.personal_phone_id).toBe('12345');
        });
        it('should skip unknown fields', () => {
            const result = parseYaTaxiUserHeader('a=b,personal_phone_id=12345,c=d');

            expect(Object.keys(result)).toHaveLength(1);
            expect(result.personal_phone_id).toBe('12345');
        });
        it('should skip invalid fields', () => {
            const result = parseYaTaxiUserHeader('personal_email_id=12345,personal_phone_id');

            expect(Object.keys(result)).toHaveLength(1);
            expect(result.personal_email_id).toBe('12345');
        });
    });
});

function createArrayWriter(logs: string[] = []) {
    return (message: string) => logs.push(message);
}

function createTaxiArrayTransport({logs = [], ...options}: {logs?: string[]} & TaxiFormatterOptions = {}) {
    options.stringifyDate ??= () => '2021-07-30T11:07:16+03:00';

    const writer = createArrayWriter(logs);
    const formatter = taxiFormatter(options);
    const transport: Transport = (report) => writer(stringifyTskv(formatter(report)));

    return {logs, transport, writer};
}

function createErrorBoosterArrayTransport({
    logs = [],
    ...options
}: {logs?: string[]} & ErrorBoosterFormatterOptions = {}) {
    options.getTimestamp ??= () => 1650361979824;

    const writer = createArrayWriter(logs);
    const formatter = errorBoosterFormatter(options);
    const transport: Transport = (report) => writer(stringifyJson(formatter(report)));

    return {logs, transport, writer};
}

function tskvEqual(actual: string | string[], expected: string | string[]) {
    const sort = (tskv: string) => {
        const out = tskv.split('\t');
        out.sort();
        return out;
    };

    expect(castArray(actual).map(sort)).toEqual(castArray(expected).map(sort));
}
