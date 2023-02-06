/* eslint-disable max-len */
import {
    createStream,
    Formatter,
    Logger,
    stringifyTskv,
    SyslogWriterLevel,
    tariffEditorCommonResolver,
    tariffEditorTypeResolver,
    taxiFormatter,
    TaxiKibanaMeta
} from '../..';
import {Resolver, TaxiTariffEditorFields} from '../../types';

describe('tariff-editor', () => {
    describe('tariffEditorTypeResolver', () => {
        it(`generates "${TaxiTariffEditorFields.META_TYPE}" from req.path`, () => {
            const {logger, logs} = createLogger({
                resolver: [tariffEditorTypeResolver()]
            });
            logger.info('OOGA', {
                req: {path: '/path'}
            });
            const log = logs[0];

            expect(log).toContain(`${TaxiTariffEditorFields.META_TYPE}=/path`);
        });
        it('uses "generateMetaType" property', () => {
            const {logger, logs} = createLogger({
                resolver: [
                    tariffEditorTypeResolver({
                        generateMetaType() {
                            return 'generatedMetaType';
                        }
                    })
                ]
            });
            logger.info('OOGA', {
                req: {}
            });
            const log = logs[0];

            expect(log).toContain(`${TaxiTariffEditorFields.META_TYPE}=generatedMetaType`);
        });
    });

    describe('tariffEditorCommonResolver', () => {
        const reqCommon = {
            method: 'PUT'
        };

        it("must override properties of 'commonMeta' and 'req' named N if meta-property with name N was provided", () => {
            const {logger, logs} = createLogger({defaultMetaType: 'foo'});
            logger.info('OOGA', {
                req: {link: 'bar'},
                meta_type: 'baz',
                link: 'qux'
            });
            const log = logs[0];

            expect(log).toEqual(expect.stringContaining('meta_type=baz'));
            expect(log).toEqual(expect.stringContaining('link=qux'));
        });

        it("must have 'metaType' fallback to a default if one was provided in 'commonMeta'", () => {
            const {logger, logs} = createLogger({
                defaultMetaType: 'common_meta_type'
            });
            logger.info('OOGA', {});
            const log = logs[0];

            expect(log).toEqual(expect.stringContaining('\tmeta_type=common_meta_type'));
        });

        it("'metaType' property provided in 'req' will not override one in 'commonMeta'", () => {
            const {logger, logs} = createLogger({defaultMetaType: 'common_meta_type'});
            logger.info('BOOGA', {req: {...reqCommon, metaType: 'req_meta_type'}});
            const log = logs[0];

            expect(log).toEqual(expect.stringContaining('\tmeta_type=common_meta_type'));
        });

        it("'metaType' property provided in logger props will override one in 'commonMeta'", () => {
            const {logger, logs} = createLogger({defaultMetaType: 'common_meta_type'});
            logger.info('BOOGA', {req: {...reqCommon}, meta_type: 'OVERRIDEN'});
            const log = logs[0];

            expect(log).toEqual(expect.stringContaining('\tmeta_type=OVERRIDEN'));
        });

        describe('certain tariff-editor properties may be remapped and accessed via provided resolution paths', () => {
            const {logger, logs} = createLogger({
                resolver: tariffEditorCommonResolver({
                    [TaxiTariffEditorFields.META_TYPE]: ['my', 'custom', 'nested', 'statusCode', 'field'],
                    [TaxiTariffEditorFields.STATUS_CODE]: ['my', 'anotherStatusCode'],
                    [TaxiTariffEditorFields.USER_AGENT]: ['not', 'existing', 'path']
                })
            });

            logger.info('AAGAA', {
                req: {
                    my: {
                        anotherStatusCode: 403,
                        custom: {
                            nested: {
                                statusCode: {
                                    field: 'world'
                                }
                            }
                        }
                    }
                }
            });
            const log1 = logs[0];

            it("must remap properties existing in 'req' on provided paths", () => {
                expect(log1).toEqual(expect.stringContaining('\tmeta_type=world'));
                expect(log1).toEqual(expect.not.stringContaining('\tuseragent'));
            });
        });
    });
});

type Logs = string[];

function formatter(report: Parameters<Formatter>[0]): ReturnType<Formatter> {
    return taxiFormatter({
        stringifyDate: () => '2022-04-28T15:34:33+03:00'
    })(report);
}

function createLogger(options?: {defaultMetaType?: string; resolver?: Resolver | [Resolver, ...Resolver[]]}): {
    logger: Logger;
    logs: Logs;
} {
    const logs: Logs = [];
    const logger = new Logger<TaxiKibanaMeta>({
        name: 'cookies',
        commonMeta: {
            version: '0.7.11',
            env: 'production',
            ...(options?.defaultMetaType ? {meta_type: options.defaultMetaType} : {})
        },
        stream: createStream({
            level: SyslogWriterLevel.INFO,
            transport: (report) => logs.push(stringifyTskv(formatter(report))),
            resolver: options?.resolver || [tariffEditorCommonResolver()]
        })
    });

    return {logger, logs};
}
