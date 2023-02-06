package ru.yandex.metrika.mobmet.crash.decoder.service.ios;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.Duration;
import java.util.Collection;
import java.util.List;

import com.atomikos.jdbc.nonxa.AtomikosNonXADataSourceBean;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import freemarker.template.utility.StringUtil;
import org.apache.commons.lang3.tuple.Pair;
import org.jetbrains.annotations.Nullable;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.postgresql.ds.PGPoolingDataSource;
import org.postgresql.ds.common.BaseDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;
import ru.yandex.metrika.dbclients.postgres.PgDataSourceFactory;
import ru.yandex.metrika.dbclients.postgres.PgDataSourceProperties;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.mobmet.crash.decoder.android.proto.CrashAndroid;
import ru.yandex.metrika.mobmet.crash.decoder.ios.proto.CrashIos;
import ru.yandex.metrika.mobmet.crash.decoder.ios.protocol.IOSCrashReport;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.JavaDecodeService;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.group.AndroidSystemPackagesDao;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.deobfuscation.group.CrashGroupCalculator;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidCrashProtobufWrapper;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidErrorProtobufWrapper;
import ru.yandex.metrika.mobmet.crash.decoder.service.android.model.AndroidParsedEventValue;
import ru.yandex.metrika.mobmet.crash.decoder.service.flutter.FlutterDecodeService;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.InternalModelDecoder;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.decoder.YDBImageDecoder;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.CrashReasonInfoFactory;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.ErrorMessageTrimWordsDao;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.ErrorMessageTrimmer;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.group.NsExceptionNameTrimmer;
import ru.yandex.metrika.mobmet.crash.decoder.service.ios.proto.AppleSdkProtocolConverter;
import ru.yandex.metrika.mobmet.crash.decoder.service.library.LibraryPredicatesService;
import ru.yandex.metrika.mobmet.crash.decoder.service.library.LibraryResultFactory;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.CrashParams;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.ParseResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.DecodeResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.LibraryResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.ParseSuccess;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.ProcessingResult;
import ru.yandex.metrika.mobmet.crash.decoder.service.processor.AndroidEventValueProcessor;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.FunctionsYDBService;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.FilesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.InlinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.LinesSerializer;
import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.serialization.YDBFunctionSerializer;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMap;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaClassMapYDBDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingMetaDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingMetaService;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMappingService;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMap;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.JavaMethodMapYDBDao;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodInfoSerializer;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.ProguardMethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.R8MethodMapping;
import ru.yandex.metrika.mobmet.crash.deobfuscation.mapping.SlowLoopStartCommandsDao;
import ru.yandex.metrika.mobmet.crash.ios.AppleDSymMetaDao;
import ru.yandex.metrika.mobmet.crash.ios.FunctionsYDBDao;
import ru.yandex.metrika.mobmet.crash.ios.FunctionsYDBDaoImpl;
import ru.yandex.metrika.mobmet.crash.ios.MultitableFunctionsYDBDao;
import ru.yandex.metrika.mobmet.crash.library.LibraryPredicatesDao;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashEncodeType;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashReasonType;
import ru.yandex.metrika.segments.apps.misc.crashes.ProcessingStatus;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.log.Log4jSetup;

import static ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType.COMPRESSED;
import static ru.yandex.metrika.mobmet.crash.symbols.SymbolsYdbTableType.UNCOMPRESSED;
import static ru.yandex.metrika.util.app.XmlPropertyConfigurer.getTextFromVault;

/**
 * Запускалка декодирования как юнит тест.
 * <p>
 * Может быть полезна так как
 * 1) Интерфейс демона с RecountRequest-ами жутко неповоротливый для разработки
 * 2) На момент написания ранера этот интерфейс не был нормально интегрирован
 * <p>
 * То есть в данный момент это такая мини замена интеграционного теста
 */
@Ignore("For manual run only. External resources is used")
@RunWith(Parameterized.class)
public class AppleDecodeRunnerTest {

    private static final Logger log = LoggerFactory.getLogger(AppleDecodeRunnerTest.class);

    private static final ObjectMapper MAPPER = new ObjectMapper();

    //private static final String TEST_PATH = "/home/dancingelf/crashes/";
    private static final String TEST_PATH = "/Users/rodion-m/workspace/tmp/mobmet-15508/crashes/";

    private static AppleParseService appleParseService;
    private static AppleDecodeService appleDecodeService;
    private static JavaDecodeService javaDecodeService;
    private static FlutterDecodeService flutterDecodeService;

    @Parameterized.Parameter
    public long eventId;

    @Parameterized.Parameter(1)
    public int applicationId;

    @Parameterized.Parameter(2)
    public String path;

    @Parameterized.Parameter(3)
    public AppEventType eventType;

    @Parameterized.Parameter(4)
    public @Nullable String errorMessage;

    @Parameterized.Parameter(5)
    public @Nullable String libraryProcessingResultFile;

    @Parameterized.Parameter(6)
    public boolean android;

    @Parameterized.Parameter(7)
    public boolean flutter;

    @Parameterized.Parameters(name = "path: {2}")
    public static Collection<Object[]> init() {
        return ImmutableList.<Object[]>builder()
                // flutter
                .add(crashParams(7633, "flutter/ios_flutter-crash-11923795939279766376"))
                .add(errorParams(7633, "flutter/ios_flutter-error-7024917473067146049", null))
                .add(errorParams(7633, "flutter/ios_flutter-custom_error-16991900502358374989", null))
                .add(crashParams(7633, "flutter/android_flutter-crash-10028777523086836113"))
                .add(errorParams(7633, "flutter/android_flutter-error-9441546643700524976", null))
                .add(errorParams(7633, "flutter/android_flutter-error_current_stack-3595811449176055413", null))

                .add(crashParams(18895, "ios/disk"))
                .add(crashParams(25378, "ios/music"))
                .add(crashParams(2, 25378, "ios/music_sdk_crash", "sdk_processing_fields.json"))
                .add(crashParams(10180, "ios/translate"))
                .add(crashParams(10267, "ios/kinopoisk"))
                .add(crashParams(28620, "ios/crash_2"))
                .add(crashParams(28620, "ios/crash_11"))
                .add(crashParams(28620, "ios/crash_18"))
                .add(crashParams(28620, "ios/crash_19"))
                .add(crashParams(28620, "ios/crash_28"))
                .add(crashParams(28620, "ios/crash_29"))
                .add(crashParams(28620, "ios/crash_without_symbols"))
                .add(errorParams(28620, "ios/error_with_stacktrace", "EXCEPTION 1"))
                .add(errorParams(28620, "ios/error_without_stacktrace",
                        "com.edadeal.favoriteDataSyncService code: 1: Incident Identifier: 50719901-0477-41A6-AD46-B2C2CC2DBB8D"))
                .add(anrParams(28620, "ios/anr"))
                .add(crashParams(18895, "ios/MOBMET-10925"))
                .add(crashParams(38000, "ios/MOBMET-11191"))
                .add(errorParams(28620, "ios/error_nserror", null))
                .add(errorParams(28620, "ios/error_custom", null))
                .add(errorParams(28620, "ios/error_custom_mangled", null))
                .add(errorParams(3049552, "ios/MOBMET-14039", null))

                // android
                .add(crashParams(20, 28620, "proguard/crash_with_lib_frame", "sdk_processing_fields.json"))
                .add(crashParams(28620, "proguard/crash_with_symbols"))
                .add(crashParams(917433, "proguard/crash_with_symbols_compressed"))
                .add(crashParams(28620, "proguard/crash_without_symbols"))
                // не можем проверить в этом тесте
                //.add(crashParams(28620, "proguard/crash_without_throwable"))

                // проверка кеша
//                .add(crashParams(18895, "ios/disk"))
//                .add(crashParams(25378, "ios/music"))
//                .add(crashParams(10180, "ios/translate"))
//                .add(crashParams(10267, "ios/kinopoisk"))
//                .add(crashParams(28620, "ios/crash_2"))
//                .add(crashParams(28620, "ios/crash_11"))
//                .add(crashParams(28620, "ios/crash_18"))
//                .add(crashParams(28620, "ios/crash_19"))
//                .add(crashParams(28620, "ios/crash_28"))
//                .add(crashParams(28620, "ios/crash_29"))
//                .add(crashParams(28620, "ios/crash_without_symbols"))
//                .add(errorParams(28620, "ios/error_with_stacktrace", "EXCEPTION 1"))
//                .add(errorParams(28620, "ios/error_without_stacktrace", "AudioEngine_Start_Error"))
//                .add(anrParams(28620, "ios/anr"))
//                .add(crashParams(18895, "ios/disk"))
//                .add(crashParams(25378, "ios/music"))
//                .add(crashParams(10180, "ios/translate"))
//                .add(crashParams(10267, "ios/kinopoisk"))
//                .add(crashParams(28620, "ios/crash_2"))
//                .add(crashParams(28620, "ios/crash_11"))
//                .add(crashParams(28620, "ios/crash_18"))
//                .add(crashParams(28620, "ios/crash_19"))
//                .add(crashParams(28620, "ios/crash_28"))
//                .add(crashParams(28620, "ios/crash_29"))
//                .add(crashParams(28620, "ios/crash_without_symbols"))
//                .add(errorParams(28620, "ios/error_with_stacktrace", "EXCEPTION 1"))
//                .add(errorParams(28620, "ios/error_without_stacktrace", "AudioEngine_Start_Error"))
//                .add(anrParams(28620, "ios/anr"))

                .build();
    }

    @BeforeClass
    public static void beforeClass() {
        Log4jSetup.basicSetup();

        // источники данных
        YdbSessionManager sessionManager = new YdbSessionManager(new YdbClientProperties()
                .setEndpoint("ydb-ru-prestable.yandex.net:2135")
                .setDatabase("/ru-prestable/metricmob/test/crashes")
                .setYdbToken(getTextFromVault("sec-01cw6tk4ymzvcdavxyd6wxv0z9/robot-metrika-test-ydb-token")));
        YdbTemplate ydbTemplate = new YdbTemplate(sessionManager);

        JdbcTemplate pgTemplate = getPgSqlJdbcTemplate();

        // поднимаем все бины, может можно сделать через спринговые тесты, без этой портянки
        FunctionsYDBDao functionsYDBDao = new MultitableFunctionsYDBDao(List.of(
                new FunctionsYDBDaoImpl(ydbTemplate, UNCOMPRESSED.getIosTable(), UNCOMPRESSED),
                new FunctionsYDBDaoImpl(ydbTemplate, COMPRESSED.getIosTable(), COMPRESSED)));

        YDBFunctionSerializer serializer = new YDBFunctionSerializer(new FilesSerializer(), new InlinesSerializer(), new LinesSerializer());
        FunctionsYDBService functionsService = new FunctionsYDBService(functionsYDBDao, serializer);
        YDBImageDecoder ydbImageDecoder = new YDBImageDecoder(functionsService);
        AppleDSymMetaDao metaDao = new AppleDSymMetaDao(pgTemplate);
        InternalModelDecoder internalModelDecoder = new InternalModelDecoder(ydbImageDecoder, metaDao);
        // 0 чтобы не смотреть на работу кеша инструкций
        internalModelDecoder.setInstructionCacheMaximumSize(0);
        internalModelDecoder.setInstructionCacheExpireAfterAccess(Duration.ZERO);
        internalModelDecoder.setMetaCacheMaximumSize(0);
        internalModelDecoder.setMetaCacheExpireAfterWrite(Duration.ZERO);
        internalModelDecoder.init();
        appleParseService = new AppleParseService(new AppleSdkProtocolConverter());
        LibraryPredicatesService libraryPredicatesService = new LibraryPredicatesService(new LibraryPredicatesDao(pgTemplate));
        libraryPredicatesService.reload();
        ErrorMessageTrimWordsDao errorMessageTrimWordsDao = new ErrorMessageTrimWordsDao(pgTemplate);
        ErrorMessageTrimmer errorMessageTrimmer = new ErrorMessageTrimmer(errorMessageTrimWordsDao);
        errorMessageTrimmer.reload();
        CrashReasonInfoFactory crashReasonInfoFactory = new CrashReasonInfoFactory(
                new NsExceptionNameTrimmer(), errorMessageTrimmer, libraryPredicatesService);

        LibraryResultFactory libraryResultFactory = new LibraryResultFactory();
        appleDecodeService = new AppleDecodeService(
                internalModelDecoder,
                crashReasonInfoFactory,
                libraryResultFactory);

        ProguardMethodInfoSerializer proguardMemberInfoSerializer = new ProguardMethodInfoSerializer();

        JavaClassMapYDBDao javaClassMapDao = new JavaClassMapYDBDao(ydbTemplate);

        JavaClassMap javaClassMap = new JavaClassMap(javaClassMapDao);
        javaClassMap.initCache();

        JavaMethodMapYDBDao<ProguardMethodMapping> javaMethodMapYDBDao =
                new JavaMethodMapYDBDao(ydbTemplate, proguardMemberInfoSerializer);

        JavaMethodMap<ProguardMethodMapping> javaMethodMap = new JavaMethodMap<>(javaMethodMapYDBDao);
        javaMethodMap.initCache();
        JavaMappingMetaService mappingMetaService = new JavaMappingMetaService(new JavaMappingMetaDao(pgTemplate));
        mappingMetaService.initCache();
        JavaMappingService<ProguardMethodMapping> proguardMappingService = new JavaMappingService<>(
                javaClassMap,
                javaMethodMap,
                mappingMetaService,
                new SlowLoopStartCommandsDao(pgTemplate),
                null);
        JavaMappingService<R8MethodMapping> r8MappingService = null;
        CrashGroupCalculator proguardCrashGroupCalculator = new CrashGroupCalculator(
                new AndroidSystemPackagesDao(pgTemplate),
                libraryPredicatesService);
        javaDecodeService = new JavaDecodeService(
                mappingMetaService,
                proguardMappingService,
                r8MappingService,
                proguardCrashGroupCalculator,
                libraryResultFactory);

        flutterDecodeService = new FlutterDecodeService(errorMessageTrimmer);
    }

    @Test
    public void test() throws Exception {

        // получить из clickhouse-client protobuf креша не получилось, использовал
//        getTemplate().query("" +
//                        "SELECT EventValue FROM crash_events_all " +
//                        "WHERE EventID=1033817182897459234 AND EventDate>=today() AND APIKey=3049552 " +
//                        "LIMIT 1",
//                (rs) -> {
//                    try {
//                        byte[] bytes = rs.getBytes("EventValue");
//                        java.nio.file.Files.write(java.nio.file.Paths.get("/home/dancingelf/event_value.bin"),
//                                bytes, java.nio.file.StandardOpenOption.CREATE_NEW);
//                    } catch (Exception ex) {
//                        throw new RuntimeException(ex);
//                    }
//                });
//        var a = true;
//        if (a) {
//            return;
//        }

        byte[] bytes = Files.readAllBytes(Paths.get(path, "event_value.bin"));

        // воспроизводим логику генерации этих полей из тестов
        long deviceId = 2 * eventId;
        long uuidHash = 3 * eventId;
        long eventNumber = 5 * eventId;
        long sessionId = 4 * eventId;
        byte sessionType = (byte) 0;
        CrashParams crashParams = new CrashParams(applicationId, deviceId, eventId,
                android ? OperatingSystem.ANDROID : OperatingSystem.IOS,
                "1.0", 1,
                eventType,
                errorMessage,
                uuidHash, eventNumber, sessionId, sessionType);

        List<ProcessingResult> actualProcessingResultList;
        switch (eventType) {
            case EVENT_PROTOBUF_CRASH:
                if (android) {
                    CrashAndroid.Crash crash = CrashAndroid.Crash.parseFrom(bytes);
                    AndroidCrashProtobufWrapper crashWrapper = new AndroidCrashProtobufWrapper(
                            crash.hasBuildId() ? crash.getBuildId() : null,
                            crash.hasThrowable() ? crash.getThrowable() : null,
                            crash.hasThreads() ? crash.getThreads() : null,
                            crash.hasVirtualMachine() ? crash.getVirtualMachine().toStringUtf8() : null,
                            crash.hasVirtualMachineVersion() ? crash.getVirtualMachineVersion().toStringUtf8() : null,
                            F.map(crash.getPluginEnvironmentList(), e -> Pair.of(e.getKey().toStringUtf8(), e.getValue().toStringUtf8())));
                    ParseResult<AndroidParsedEventValue> parseResult = AndroidEventValueProcessor.parseSuccess(crashWrapper);
                    actualProcessingResultList = flutter ?
                            flutterDecodeService.decodeAndroidFlutterEvent(crashParams, parseResult.getParseSuccess(), crashWrapper) :
                            javaDecodeService.decode(crashParams, parseResult.getParseSuccess(), crashWrapper, false, true);
                } else {
                    CrashIos.IOSCrashReport parsedProto = CrashIos.IOSCrashReport.parseFrom(bytes);
                    ParseResult<IOSCrashReport> parseResult = appleParseService.parse(crashParams.getAppId(), parsedProto);
                    actualProcessingResultList = flutter ?
                            flutterDecodeService.decodeIosFlutterEvent(crashParams, parseResult) :
                            appleDecodeService.decodeCrash(crashParams, parseResult, false, true);
                }
                break;
            case EVENT_PROTOBUF_ANR:
                if (android) {
                    throw new UnsupportedOperationException("not supported");
                } else {
                    CrashIos.IOSCrashReport parsedProto = CrashIos.IOSCrashReport.parseFrom(bytes);
                    ParseResult<IOSCrashReport> parseResult = appleParseService.parse(crashParams.getAppId(), parsedProto);
                    actualProcessingResultList = appleDecodeService.decodeCrash(crashParams, parseResult, false, false);
                }
                break;
            case EVENT_PROTOBUF_ERROR:
                if (android) {
                    CrashAndroid.Error error = CrashAndroid.Error.parseFrom(bytes);
                    String identifier = null;
                    if (error.getType() == CrashAndroid.Error.ErrorType.CUSTOM) {
                        if (!error.hasCustom()) {
                            throw new IllegalArgumentException("'custom' field is required");
                        }
                        identifier = error.getCustom().getIdentifier();
                    }
                    AndroidErrorProtobufWrapper errorWrapper = new AndroidErrorProtobufWrapper(
                            error.hasBuildId() ? error.getBuildId() : null,
                            identifier,
                            error.hasMessage() ? error.getMessage() : StringUtil.emptyToNull(crashParams.getEventName()),
                            error.hasThrowable() ? error.getThrowable() : null,
                            error.getMethodCallStacktraceList(),
                            error.getVirtualMachine().toStringUtf8(),
                            error.hasVirtualMachineVersion() ? error.getVirtualMachineVersion().toStringUtf8() : null,
                            F.map(error.getPluginEnvironmentList(), e -> Pair.of(e.getKey().toStringUtf8(), e.getValue().toStringUtf8())));
                    ParseResult<AndroidParsedEventValue> parseResult = AndroidEventValueProcessor.parseSuccess(errorWrapper);
                    actualProcessingResultList = flutter ?
                            flutterDecodeService.decodeAndroidFlutterEvent(crashParams, parseResult.getParseSuccess(), errorWrapper) :
                            javaDecodeService.decode(crashParams, parseResult.getParseSuccess(), errorWrapper, false, true);
                } else {
                    CrashIos.IOSCrashReport parsedProto = CrashIos.IOSCrashReport.parseFrom(bytes);
                    ParseResult<IOSCrashReport> parseResult = appleParseService.parse(crashParams.getAppId(), parsedProto);
                    actualProcessingResultList = flutter ?
                            flutterDecodeService.decodeIosFlutterEvent(crashParams, parseResult) :
                            appleDecodeService.decodeError(crashParams, parseResult, false, false);
                }
                break;
            default:
                throw new IllegalArgumentException("Unexpected event type: " + eventType);
        }

        assertProcessingResult(actualProcessingResultList.get(0), "processing_fields.json", 1);
        if (libraryProcessingResultFile != null) {
            Assert.assertEquals(2, actualProcessingResultList.size());
            ProcessingResult actualProcessingResult = actualProcessingResultList.get(1);
            ProcessingFields libraryFields = assertProcessingResult(actualProcessingResult, libraryProcessingResultFile, 2);
            LibraryResult libraryResult = actualProcessingResult.getLibResult();
            LibraryResult expectedLibraryResult = new LibraryResult(
                    libraryFields.apiKey, libraryFields.eventID.longValue(),
                    libraryFields.decodeOriginalAPIKey, libraryFields.decodeOriginalEventID);
            Assert.assertEquals(expectedLibraryResult, libraryResult);
        } else {
            Assert.assertEquals(1, actualProcessingResultList.size());
        }
    }

    private void writeActualResult(ProcessingResult processingResult,
                                   DecodeResult decodeResult,
                                   int id) throws IOException {
        String dirPath = path + String.format("-actual-%s/", id);
        log.info("Writing actual data into {}", dirPath);

        //noinspection ResultOfMethodCallIgnored
        Paths.get(dirPath).toFile().mkdirs();

        assert decodeResult.getThreadContent() != null;
        Files.writeString(Path.of(dirPath + "crash_thread_content.txt"),
                decodeResult.getThreadContent(),
                StandardOpenOption.CREATE, StandardOpenOption.WRITE);

        Files.writeString(Path.of(dirPath + "crash_decoded_event_value.json"),
                beautify(decodeResult.getEventValueDecoded()),
                StandardOpenOption.CREATE, StandardOpenOption.WRITE);

        ProcessingFields processingFields = new ProcessingFields(processingResult, decodeResult);
        String processingFieldsJson = writeBeautifulJson(processingFields);
        Files.writeString(Path.of(dirPath + "processing_fields.json"),
                processingFieldsJson,
                StandardOpenOption.CREATE, StandardOpenOption.WRITE);
    }

    private ProcessingFields assertProcessingResult(ProcessingResult actualProcessingResult, String expectedFieldsFile,
                                                    int outputEventIndex)
            throws IOException {
        DecodeResult actualDecodeResult = actualProcessingResult.getDecodeResult();
        DecodeResult actualDecodeResultWithoutNulls = new DecodeResult(
                actualDecodeResult.getGroupId(),
                actualDecodeResult.getUsedSymbolsIds(),
                actualDecodeResult.getMissedSymbolsIds(),
                actualDecodeResult.getUsedSystemSymbolsIds(),
                actualDecodeResult.getMissedSystemSymbolsIds(),
                actualDecodeResult.getEventValueDecoded(),
                actualDecodeResult.getCrashEncodeType(),
                actualDecodeResult.getReasonType(),
                replaceNull(actualDecodeResult.getReason()),
                replaceNull(actualDecodeResult.getReasonMessage()),
                replaceNull(actualDecodeResult.getBinaryName()),
                replaceNull(actualDecodeResult.getFileName()),
                replaceNull(actualDecodeResult.getMethodName()),
                actualDecodeResult.getLine() == null ? 0 : actualDecodeResult.getLine(),
                replaceNull(actualDecodeResult.getThreadContent()));

        writeActualResult(actualProcessingResult, actualDecodeResultWithoutNulls, outputEventIndex);

        String processingFields = readCrashDataAsString(expectedFieldsFile);
        ProcessingFields fields = MAPPER.readValue(processingFields, ProcessingFields.class);
        ParseSuccess expectedParseResult = new ParseSuccess(
                fields.osBuild,
                fields.decodeRequiredSymbolsId
        );
        String crashThreadContent = readCrashDataAsString("crash_thread_content.txt");
        String crashDecodedEventValueBeautified = readCrashDataAsString("crash_decoded_event_value.json");
        String crashDecodedEventValue = MAPPER.writeValueAsString(MAPPER.readTree(crashDecodedEventValueBeautified));
        DecodeResult expectedDecodeResult = new DecodeResult(
                fields.decodeGroupId.longValue(),
                fields.decodeUsedSymbolsIds,
                fields.decodeMissedSymbolsIds,
                fields.decodeUsedSystemSymbolsIds,
                fields.decodeMissedSystemSymbolsIds,
                crashDecodedEventValue,
                CrashEncodeType.fromChValue(fields.crashEncodeType),
                CrashReasonType.fromChValue(fields.crashReasonType),
                fields.crashReason,
                fields.crashReasonMessage,
                fields.crashBinaryName,
                fields.crashFileName,
                fields.crashMethodName,
                fields.crashSourceLine,
                crashThreadContent
        );

        Assert.assertEquals(fields.decodeStatus, actualProcessingResult.getStatus());

        ParseSuccess actualParseResult = actualProcessingResult.getParseResult();
        ParseSuccess actualParseResultWithoutNulls = new ParseSuccess(
                replaceNull(actualParseResult.getOsBuild()),
                replaceNull(actualParseResult.getRequiredSymbolsId()));
        Assert.assertEquals(expectedParseResult, actualParseResultWithoutNulls);
        // две проверки ниже содержатся в третьей проверке, но так мы увидим diff больших строк
        Assert.assertEquals(expectedDecodeResult.getThreadContent(), actualDecodeResultWithoutNulls.getThreadContent());
        Assert.assertEquals(beautify(expectedDecodeResult.getEventValueDecoded()),
                beautify(actualDecodeResultWithoutNulls.getEventValueDecoded()));
        Assert.assertEquals(expectedDecodeResult, actualDecodeResultWithoutNulls);

        return fields;
    }

    private String readCrashDataAsString(String file) throws IOException {
        return Files.readString(Paths.get(path, file)).stripTrailing();
    }

    private static String writeBeautifulJson(Object value) throws IOException {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }

    private static String beautify(String value) throws IOException {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(MAPPER.readTree(value));
    }

    @SuppressWarnings("Duplicates")
    private static JdbcTemplate getPgSqlJdbcTemplate() {
        PgDataSourceProperties properties = new PgDataSourceProperties();
        properties.setHost(List.of("sas-pl30ycbwt2p9r5v0.db.yandex.net"));
        properties.setPort(6432);
        properties.setUser("metrika");
        properties.setPool(true);
        properties.setDb("mobile");
        properties.setPassword(XmlPropertyConfigurer.getTextFromVault("sec-01cw6tk4ymzvcdavxyd6wxv0z9/mobile_crashes_postgresql"));

        BaseDataSource dataSourceProps = new PGPoolingDataSource();
        dataSourceProps.setLoadBalanceHosts(true);
        dataSourceProps.setConnectTimeout(30);
        dataSourceProps.setSocketTimeout(30);
        dataSourceProps.setTargetServerType("master");
        dataSourceProps.setSsl(true);
        dataSourceProps.setSslfactory("org.postgresql.ssl.NonValidatingFactory");
        dataSourceProps.setPrepareThreshold(0);

        PgDataSourceFactory factory = new PgDataSourceFactory();
        factory.setProps(dataSourceProps);
        System.setProperty("ru.yandex.metrika.daemon.name", "test");
        AtomikosNonXADataSourceBean dataSource = factory.getDataSource(properties);
        dataSource.setMaxPoolSize(10);

        return new JdbcTemplate(dataSource);
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

    private HttpTemplate getTemplate() {
        ClickHouseProperties properties = new ClickHouseProperties();
        properties.setMaxThreads(1);
        properties.setSessionTimeout(500000000L);
        properties.setSocketTimeout(500000000);

        return new HttpTemplateImpl(
                new ClickHouseSource(
                        "localhost",
                        45001,
                        "mobile"
                ),
                properties
        );
    }

    private static String replaceNull(String str) {
        return str == null ? "" : str;
    }

    private static Object[] anrParams(int applicationId, String path) {
        return new Object[]{1L, applicationId, TEST_PATH + path, AppEventType.EVENT_PROTOBUF_ANR, null, null, isAndroidPath(path), isFlutterPath(path)};
    }

    private static Object[] crashParams(int applicationId, String path) {
        return new Object[]{1L, applicationId, TEST_PATH + path, AppEventType.EVENT_PROTOBUF_CRASH, null, null, isAndroidPath(path), isFlutterPath(path)};
    }

    private static Object[] crashParams(long eventId, int applicationId, String path, String libraryProcessingResultFile) {
        return new Object[]{eventId, applicationId, TEST_PATH + path, AppEventType.EVENT_PROTOBUF_CRASH, null, libraryProcessingResultFile, isAndroidPath(path), isFlutterPath(path)};
    }

    private static Object[] errorParams(int applicationId, String path, String errorMessage) {
        return new Object[]{1L, applicationId, TEST_PATH + path, AppEventType.EVENT_PROTOBUF_ERROR, errorMessage, null, isAndroidPath(path), isFlutterPath(path)};
    }

    private static boolean isAndroidPath(String path) {
        return path.contains("proguard") || path.contains("android");
    }

    private static boolean isFlutterPath(String path) {
        return path.contains("flutter");
    }

    private static class ProcessingFields {
        public ProcessingStatus decodeStatus;
        public String crashEncodeType;
        public BigInteger decodeGroupId;
        public String osBuild;
        public String decodeRequiredSymbolsId;
        public List<String> decodeUsedSymbolsIds;
        public List<String> decodeMissedSymbolsIds;
        public List<String> decodeUsedSystemSymbolsIds;
        public List<String> decodeMissedSystemSymbolsIds;
        public String crashReasonType;
        public String crashReason;
        public String crashReasonMessage;
        public String crashBinaryName;
        public String crashFileName;
        public String crashMethodName;
        public Long crashSourceLine;
        public Integer apiKey;
        public BigInteger eventID;
        public Integer decodeOriginalAPIKey;
        public Long decodeOriginalEventID;

        public ProcessingFields() {
            // Пустой конструктор нужен джексону
        }

        public ProcessingFields(ProcessingResult processingResult,
                                DecodeResult decodeResult) {
            ParseSuccess parseSuccess = processingResult.getParseResult();
            this.decodeStatus = processingResult.getStatus();
            this.crashEncodeType = decodeResult.getCrashEncodeType().getChValue();
            this.decodeGroupId = BigInteger.valueOf(decodeResult.getGroupId());
            this.osBuild = replaceNull(parseSuccess.getOsBuild());
            this.decodeRequiredSymbolsId = replaceNull(parseSuccess.getRequiredSymbolsId());
            this.decodeUsedSymbolsIds = decodeResult.getUsedSymbolsIds();
            this.decodeMissedSymbolsIds = decodeResult.getMissedSymbolsIds();
            this.decodeUsedSystemSymbolsIds = decodeResult.getUsedSystemSymbolsIds();
            this.decodeMissedSystemSymbolsIds = decodeResult.getMissedSystemSymbolsIds();
            this.crashReasonType = decodeResult.getReasonType().getChValue();
            this.crashReason = decodeResult.getReason();
            this.crashReasonMessage = decodeResult.getReasonMessage();
            this.crashBinaryName = decodeResult.getBinaryName();
            this.crashFileName = decodeResult.getFileName();
            this.crashMethodName = decodeResult.getMethodName();
            this.crashSourceLine = decodeResult.getLine();
            // Для тестов библиотек надо тут ещё доделать, а пока что заглушка:
            this.apiKey = null;
            this.eventID = null;
            this.decodeOriginalAPIKey = null;
            this.decodeOriginalEventID = null;
        }
    }
}
