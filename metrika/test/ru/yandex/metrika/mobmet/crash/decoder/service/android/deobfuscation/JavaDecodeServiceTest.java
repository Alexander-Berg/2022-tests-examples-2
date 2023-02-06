package ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation;

import java.io.IOException;
import java.util.Map;
import java.util.Set;

import com.google.common.io.Resources;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.postgresql.ds.PGSimpleDataSource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.mobmet.crash.decoder.android.proto.CrashAndroid;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.group.AndroidSystemPackagesDao;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.group.CrashGroupCalculator;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidCrashProtobufWrapper;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidParsedEventValue;
import ru.yandex.metrika.mobmet.crash.decoder.service.library.DummyLibraryService;
import ru.yandex.metrika.mobmet.crash.decoder.service.library.LibraryResultFactory;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.CrashParams;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.ParseResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.DecodeResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.ProcessingResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.processor.AndroidEventValueProcessor;
import ru.yandex.metrika.mobmet.crash.deobfuscation.fork.FrameRemapper;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.CrashMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMap;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMapYDBDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingMeta;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingMetaDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingMetaService;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingService;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMap;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMapYDBDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.MethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodInfoSerializer;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.R8MethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.SlowLoopStartCommandsDao;
import ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashEncodeType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.collections.F;

import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static ru.yandex.metrika.mobmet.crash.SymbolsUploadType.IMPORT_TOKEN;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.APP_ID;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.BUILD_UUID;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.OBFUSCATED_JVM_CRASH;
import static ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.TestData.getExpectedStackTraceAsText;
import static ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingType.PROGUARD;
import static ru.yandex.metrika.segments.apps.misc.crashes.ProcessingStatus.DECODE_SUCCESS;
import static ru.yandex.metrika.util.app.XmlPropertyConfigurer.getTextFromVault;
import static ru.yandex.metrika.util.json.JsonUtils.formatJson;

/**
 * Тест для отладки деобфускации proguard android крешей
 */
@SuppressWarnings("UnstableApiUsage")
@Ignore
public class JavaDecodeServiceTest {

    private static final String DEBUG_BUILD_UUID = "b68aa824-ad3c-401d-933d-4bdd55b59f09";

    private static final boolean IS_DEBUG_REAL_CRASH = false;

    private YdbSessionManager sessionManager;
    private JavaMappingMetaService mappingMetaService;
    private JavaMappingService<ProguardMethodMapping> proguardMappingService;
    private JavaMappingService<R8MethodMapping> r8MappingService;
    private JavaDecodeService javaDecodeService;

    private JavaMappingMeta mappingMeta;

    @Before
    public void setUp() throws IOException {
        sessionManager = getYdbSessionManager();
        YdbTemplate ydbClient = new YdbTemplate(sessionManager);

        PGSimpleDataSource pgDataSource = getJdbcTemplate();
        JdbcTemplate jdbcTemplate = new JdbcTemplate(pgDataSource);
        JavaMappingMetaDao mappingMetaDao = new JavaMappingMetaDao(jdbcTemplate);
        mappingMetaService = new JavaMappingMetaService(mappingMetaDao);
        mappingMetaService.initCache();
        AndroidSystemPackagesDao androidSystemPackagesDao = new AndroidSystemPackagesDao(jdbcTemplate);
        SlowLoopStartCommandsDao slowLoopStartCommandsDao = new SlowLoopStartCommandsDao(jdbcTemplate);

        JavaClassMapYDBDao classMapYDBDao = new JavaClassMapYDBDao(ydbClient);
        JavaClassMap classMap = new JavaClassMap(classMapYDBDao);
        classMap.initCache();

        JavaMethodMapYDBDao<ProguardMethodMapping> classMethodMapYDBDao = new JavaMethodMapYDBDao(
                ydbClient, new ProguardMethodInfoSerializer());
        JavaMethodMap<ProguardMethodMapping> classMethodMap = new JavaMethodMap<>(classMethodMapYDBDao);
        classMethodMap.initCache();

        proguardMappingService = new JavaMappingService<>(classMap, classMethodMap, mappingMetaService,
                slowLoopStartCommandsDao, new TransactionTemplate(new DataSourceTransactionManager(pgDataSource)));

        LibraryResultFactory libraryResultFactory = new LibraryResultFactory();

        javaDecodeService = new JavaDecodeService(
                mappingMetaService,
                proguardMappingService,
                r8MappingService,
                new CrashGroupCalculator(androidSystemPackagesDao, new DummyLibraryService()),
                libraryResultFactory);

        if (IS_DEBUG_REAL_CRASH) {
// Если меппинга DEBUG_BUILD_UUID ещё нет в тестинге, то его надо залить
//            FrameRemapper frameRemapper = ProguardMappingService.readFrameRemapper(
//                    getClass().getResourceAsStream("mapping_debug.txt"));
//            proguardMappingService.saveMappings(
//                    JavaMappingMeta.create(APP_ID, DEBUG_BUILD_UUID, "First Version", 1, PROGUARD, IMPORT_TOKEN),
//                    frameRemapper.getClassMap(),
//                    frameRemapper.getClassMethodMap()
//            );
        } else {
            FrameRemapper frameRemapper = JavaMappingService.readFrameRemapper(
                    getClass().getResourceAsStream("mapping.txt"));
            mappingMeta = JavaMappingMeta.create(APP_ID, BUILD_UUID, "First Version", 1, PROGUARD,
                    IMPORT_TOKEN, SymbolsYdbTableType.COMPRESSED);
            Map<String, Map<String, Set<ProguardMethodMapping>>> mappings =
                    MethodMapping.convertMappings(frameRemapper.getClassMethodMap(), ProguardMethodMapping::new);
            proguardMappingService.saveMappings(
                    mappingMeta,
                    new CrashMapping<>(frameRemapper.getClassMap(), mappings)
            );
        }
    }

    @Test
    public void test() throws Exception {

        CrashParams crashParams = new CrashParams(APP_ID, 10, 10,
                OperatingSystem.IOS,
                "1.1", 123,
                AppEventType.EVENT_PROTOBUF_CRASH,
                "Случилось что-то плохое.",
                0L, 0L, 0L, (byte) 0);

        AndroidCrashProtobufWrapper crash = getObfuscatedJvmCrash();
        ParseResult<AndroidParsedEventValue> parseResult = AndroidEventValueProcessor.parseSuccess(crash);

        ProcessingResult actual =
                javaDecodeService.decode(crashParams, parseResult.getParseSuccess(), crash, false, false).get(0);

        if (IS_DEBUG_REAL_CRASH) {
            System.out.println(formatJson(actual.getDecodeResult().getEventValueDecoded()));
        } else {
            assertEquals(DECODE_SUCCESS, actual.getStatus());

            // check ParseResult
            assertNotNull(actual.getParseResult());
            assertNull(actual.getParseResult().getOsBuild());
            assertEquals(BUILD_UUID, actual.getParseResult().getRequiredSymbolsId());

            // check DecodeResult
            DecodeResult actualDecodeResult = actual.getDecodeResult();
            assertNotNull(actualDecodeResult);
            assertEquals(EXPECTED_DECODE_RESULT.getGroupId(), actualDecodeResult.getGroupId());
            assertEquals(EXPECTED_DECODE_RESULT.getUsedSymbolsIds(), actualDecodeResult.getUsedSymbolsIds());
            assertEquals(EXPECTED_DECODE_RESULT.getMissedSymbolsIds(), actualDecodeResult.getMissedSymbolsIds());
            assertEquals(EXPECTED_DECODE_RESULT.getEventValueDecoded(),
                    formatJson(actualDecodeResult.getEventValueDecoded()));
            assertEquals(EXPECTED_DECODE_RESULT.getReasonType(), actualDecodeResult.getReasonType());
            assertEquals(EXPECTED_DECODE_RESULT.getReason(), actualDecodeResult.getReason());
            assertEquals(EXPECTED_DECODE_RESULT.getReasonMessage(), actualDecodeResult.getReasonMessage());
            assertEquals(EXPECTED_DECODE_RESULT.getBinaryName(), actualDecodeResult.getBinaryName());
            assertEquals(EXPECTED_DECODE_RESULT.getFileName(), actualDecodeResult.getFileName());
            assertEquals(EXPECTED_DECODE_RESULT.getMethodName(), actualDecodeResult.getMethodName());
            assertEquals(EXPECTED_DECODE_RESULT.getLine(), actualDecodeResult.getLine());
            assertEquals(EXPECTED_DECODE_RESULT.getThreadContent(), actualDecodeResult.getThreadContent());

            assertNull(actual.getErrorDetails());
        }
    }

    @After
    public void tearDown() {
        proguardMappingService.removeAll(singletonList(mappingMeta));
        sessionManager.close();
    }

//// Test Data /////////////////////////////////////////////////////////////////////////////////////////////////////////

    private static YdbSessionManager getYdbSessionManager() {
        return new YdbSessionManager(new YdbClientProperties()
                .setEndpoint("ydb-ru-prestable.yandex.net:2135")
                .setDatabase("/ru-prestable/metricmob/test/crashes")
                .setYdbToken(getTextFromVault("sec-01cw6tk4ymzvcdavxyd6wxv0z9/robot-metrika-test-ydb-token")));

    }

    private static PGSimpleDataSource getJdbcTemplate() {
        PGSimpleDataSource dataSource = new PGSimpleDataSource();
        dataSource.setUrl("jdbc:postgresql://sas-pl30ycbwt2p9r5v0.db.yandex.net:6432/mobile");
        dataSource.setUser("metrika");
        dataSource.setPassword(
                XmlPropertyConfigurer.getTextFromVault("sec-01cw6tk4ymzvcdavxyd6wxv0z9/mobile_crashes_postgresql"));
        dataSource.setSsl(true);
        dataSource.setSslfactory("org.postgresql.ssl.NonValidatingFactory");

        return dataSource;
    }

    @SuppressWarnings("Duplicates")
    private static MySqlJdbcTemplate getMySqlJdbcTemplate() {
        TransactionalMetrikaDataSource dataSource = new DataSourceFactory().getDataSource();
        dataSource.setHost("127.0.0.1");
        dataSource.setPort(7071);
        dataSource.setUser("metrika");
        dataSource.setDb("mobile");
        dataSource.setPassword(XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"));
        try {
            dataSource.afterPropertiesSet();
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
        return new MySqlJdbcTemplate(dataSource);
    }

    private static final String EXPECTED_DECODED_CRASH_JSON;
    private static final String EXPECTED_AFFECTED_THREAD_CONTENT_TXT;

    static {
        try {
            EXPECTED_DECODED_CRASH_JSON = formatJson(Resources.toString(
                    JavaDecodeServiceTest.class.getResource("expected_decoded_crash.json"), UTF_8));
            EXPECTED_AFFECTED_THREAD_CONTENT_TXT = getExpectedStackTraceAsText();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private static final DecodeResult EXPECTED_DECODE_RESULT = new DecodeResult(
            -3461212471523564161L,
            singletonList(BUILD_UUID),
            emptyList(),
            emptyList(),
            emptyList(),
            EXPECTED_DECODED_CRASH_JSON,
            CrashEncodeType.PROGUARD,
            null,
            "com.bumptech.glide.Registry$MissingComponentException",
            "Couldn't find component",
            null,
            "OrderTitleFormatter_MembersInjector.java",
            "ru.yandex.taxi.controller.OrderTitleFormatter_MembersInjector.injectMembers",
            27L,
            EXPECTED_AFFECTED_THREAD_CONTENT_TXT
    );

    private static AndroidCrashProtobufWrapper getObfuscatedJvmCrash() {
        if (IS_DEBUG_REAL_CRASH) {
            CrashAndroid.Crash protoCrash = getTemplate().queryForObject("" +
                    "SELECT EventValue\n" +
                    "FROM mobile.crash_events_all\n" +
                    "WHERE (APIKey = 7633)" +
                    " AND (EventType = 26)" +
                    " AND (EventDate = toDate('2019-10-08'))" +
                    " AND (DecodeRequiredSymbolsId = 'b68aa824-ad3c-401d-933d-4bdd55b59f09')" +
                    " AND (EventID = 18107322682111457503)" +
                    " AND (DecodeStatus = 'decode_success')" +
                    " AND (Sign = 1)" +
                    " AND (DeviceIDHash = 4225286787684034672)\n" +
                    "LIMIT 1", (rs, rowNum) -> {
                try {
                    byte[] bytes = rs.getBytes("EventValue");
                    return CrashAndroid.Crash.parseFrom(bytes);
                } catch (Exception ex) {
                    throw new RuntimeException(ex);
                }
            });

            return new AndroidCrashProtobufWrapper(
                    DEBUG_BUILD_UUID,
                    protoCrash.getThrowable(),
                    protoCrash.getThreads(),
                    protoCrash.getVirtualMachine().toStringUtf8(),
                    protoCrash.hasVirtualMachineVersion() ? protoCrash.getVirtualMachineVersion().toStringUtf8() : null,
                    F.map(protoCrash.getPluginEnvironmentList(), e -> Pair.of(e.getKey().toStringUtf8(), e.getValue().toStringUtf8())));
        } else {
            return OBFUSCATED_JVM_CRASH;
        }
    }

    private static HttpTemplate getTemplate() {
        ClickHouseProperties properties = new ClickHouseProperties();
        properties.setMaxThreads(1);
        properties.setSessionTimeout(500000000L);
        properties.setSocketTimeout(500000000);

        return new HttpTemplateImpl(
                new ClickHouseSource(
                        "localhost",
                        6061,
                        "mobile"
                ),
                properties
        );
    }

}
