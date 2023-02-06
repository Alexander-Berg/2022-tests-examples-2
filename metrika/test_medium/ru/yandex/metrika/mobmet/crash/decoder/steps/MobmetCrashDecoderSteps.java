package ru.yandex.metrika.mobmet.crash.decoder.steps;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.common.test.medium.CalcCloudSteps;
import ru.yandex.metrika.common.test.medium.FixedString;
import ru.yandex.metrika.dbclients.zookeeper.ZooClient;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static java.util.stream.Collectors.toList;
import static org.awaitility.Awaitility.await;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ANR;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ERROR;

@Component
public class MobmetCrashDecoderSteps {

    private static final Logger log = LoggerFactory.getLogger(MobmetCrashDecoderSteps.class);

    private static final String CLICKHOUSE_CRASH_DECODER_INPUT_TABLE_PREFIX = "CrashChunk_";

    private static final String CLICKHOUSE_CRASH_DECODER_OUTPUT_TABLE_PREFIX = "Decoded_";

    private static final String ZK_DECODED_CHUNK_ID_SUFFIX = "_decoded";

    @Autowired
    private MobmetCrashDecoderSettings settings;

    @Autowired
    private ZooClient zooClient;

    @Autowired
    private CalcCloudSteps calcCloud;

    @Autowired
    private YdbSteps ydb;

    @Step("Подготовка")
    public void prepare() {
        log.debug("Подготовка");
        createZooKeeperPaths();
        createYdbTables();
    }

    @Step("Создание путей в ZooKeeper")
    public void createZooKeeperPaths() {
        createZooKeeperPath(settings.getInputQueuesRoot());
    }

    private void createZooKeeperPath(String path) {
        try {
            zooClient.rmr(path);
        } catch (IllegalStateException exception) {
            log.debug(format("Node %s does not exist.", path));
        }
        zooClient.create(path, "");
    }

    @Step("Создание таблиц в YDB")
    public void createYdbTables() {
        ydb.createCrashGroupsManagement();
        ydb.createCrashGroupsAppVersions();
        ydb.createOpenCrashGroupEvents();
    }

    @Step("Записываем входной чанк")
    public String writeInputChunk(List<MobileEvent> mobileEvents) {
        return calcCloud.writeInputChunk(
                settings.getInputDataBase(), CLICKHOUSE_CRASH_DECODER_INPUT_TABLE_PREFIX,
                MobileEvent.getCreateTableTemplate(), settings.getInputQueuesPath(), mobileEvents);
    }

    @Step("Ожидаем обработки входных данных")
    public void waitForEmptyQueue() {
        await(Thread.currentThread().getName())
                .atMost(60, TimeUnit.SECONDS)
                .pollInterval(1, TimeUnit.SECONDS)
                .until(this::queueIsEmpty);
    }

    @Step("Читаем выходной чанк")
    public List<MobileEvent> readOutputChunk(String chunkId) {
        List<MobileEvent> chunk = calcCloud.readOutputChunk(
                settings.getOutputDataBase(), getOutputChunkTableName(chunkId), MobileEvent.getRowMapper());
        return sortChunk(chunk);
    }

    public static List<MobileEvent> sortChunk(List<MobileEvent> chunk) {
        return chunk.stream()
                .sorted(Comparator.<MobileEvent, Long>comparing(event -> Long.valueOf(event.getProfileID()))
                        .thenComparing(MobileEvent::getAPIKey)
                        .thenComparing(MobileEvent::getSign)
                        .thenComparing(MobileEvent::getVersion)
                        .thenComparing(MobileEvent::getEventNumber))
                .collect(toList());
    }

    private boolean queueIsEmpty() {
        return zooClient.ls(settings.getInputQueuesPath()).size() == 0;
    }

    private String getOutputChunkTableName(String chunkId) {
        return CLICKHOUSE_CRASH_DECODER_OUTPUT_TABLE_PREFIX + chunkId + ZK_DECODED_CHUNK_ID_SUFFIX;
    }

    public List<MobileEvent> getInputIOTestChunk() {
        List<MobileEvent> events = generateMobileEvents(1000);
        for (int i = 0; i < events.size(); i++) {
            events.get(i)
                    .withEventID(BigInteger.valueOf(i))
                    .withProfileID(String.valueOf(i))
                    .withOperatingSystem("windows")
                    .withEventValueCrash("SOME CRASH VALUE")
                    .withEventValue(ByteString.fromString("SOME CRASH VALUE", StandardCharsets.UTF_8))
                    .withScaleFactor(Math.PI)
                    .withSimCardsAreRoaming(new Integer[]{0, 1, 0})
                    .withSimCardsIccIDs(new String[]{"", "", "Value"})
                    .withSimCardsOperatorsNames(new String[]{" Operator simple name ", "Opetator quota", ""})
                    .withSimCardsCountriesCodes(new Long[]{1L, 2L, 3L})
                    .withSimCardsOperatorsIDs(new Long[]{4L, 5L, 6L})
                    .withInvalidationReasons(new String[]{})
                    .withReceiveTimestamp(new BigInteger("10000000000000000000"));
        }
        return events;
    }

    public List<MobileEvent> getInputInvalidatedEventsTestChunk() {
        return getInputIOTestChunk().stream()
                .peek(event -> event
                        .withInvalidationReasons(new String[]{"Validation error 1", "Validation error 2"}))
                .collect(Collectors.toList());
    }

    public List<MobileEvent> getInputVersionsTestChunk() {
        List<MobileEvent> input = generateMobileEvents(2);

        MobileEvent newCrash = input.get(0);
        CrashTestData newCrashData = CrashTestDataReader.readCrashForDecode(0);
        fillCrashFields(newCrash, newCrashData.getInput());
        newCrash.withDecodeStatus("unknown");

        MobileEvent parsedCrash = input.get(1);
        CrashTestData parsedCrashData = CrashTestDataReader.readCrashForDecode(1);
        fillCrashFields(parsedCrash, parsedCrashData.getInput());
        parsedCrash.withDecodeStatus("parse_success");
        parsedCrash.withDecodeRequiredSymbolsId(parsedCrashData.getExpected().get(0).getDecodeRequiredSymbolsId());
        parsedCrash.withOSBuild(parsedCrashData.getExpected().get(0).getOsBuild());

        return input;
    }

    public MobileEvent convertToMobileEvent(CrashTestData crashTestData) {
        MobileEvent event = generateMobileEvent();
        fillCrashFields(event, crashTestData.getInput());
        return event;
    }

    public List<MobileEvent> getRateLimitedChunk() {
        List<MobileEvent> events = generateMobileEvents(1000);
        for (int i = 0; i < events.size(); ++i) {
            MobileEvent event = events.get(i);
            event
                    .withAPIKey(101200L)
                    .withEventType(EVENT_PROTOBUF_ERROR.getNumber())
                    .withEventNumber(BigInteger.valueOf(i))
                    .withProfileID("111")
                    .withDeviceIDHash(BigInteger.ONE)
                    .withSessionID(BigInteger.ONE)
                    .withUUIDHash(BigInteger.ONE)
                    .withSessionType(0);
        }
        return events;
    }

    private static void fillCrashFields(MobileEvent event, CrashInputFields inputFields) {
        event
                .withEventID(BigInteger.valueOf(inputFields.getEventId()))
                .withProfileID(String.valueOf(inputFields.getEventId()))
                .withDeviceIDHash(BigInteger.valueOf(inputFields.getEventId() * 2))
                .withUUIDHash(BigInteger.valueOf(inputFields.getEventId() * 3))
                .withSessionID(BigInteger.valueOf(inputFields.getEventId() * 4))
                .withEventNumber(BigInteger.valueOf(inputFields.getEventId() * 5))
                .withAPIKey(inputFields.getApplicationId())
                .withOperatingSystem(inputFields.getOperatingSystem())
                .withEventType(inputFields.getEventType())
                .withEventName(inputFields.getEventName())
                .withEventValue(ByteString.fromBytes(inputFields.getEventValue()));
    }

    private static List<MobileEvent> generateMobileEvents(int count) {
        return Stream.generate(MobmetCrashDecoderSteps::generateMobileEvent).limit(count).collect(toList());
    }

    private static MobileEvent generateMobileEvent() {
        return new MobileEvent()
                .withAPIKey(28620L)
                .withAPIKey128(FixedString.fromBytes(new byte[]{13, 0, 3, 0, 0, 5, 0, 0, 0}))
                .withClientIP(FixedString.fromBytes(new byte[]{0, 0, 0, 0}))
                .withAppVersionName("1.0.2")
                .withAppBuildNumber(123L)
                .withStartDate(DateTime.parse("2019-05-13"))
                .withEventDate(DateTime.parse("2019-05-13"))
                .withReceiveDate(DateTime.parse("2019-05-13"))
                .withOperatingSystem("ios")
                .withAppDebuggable("undefined")
                .withLimitAdTracking("false")
                .withLocationEnabled("true")
                .withEventType(EVENT_PROTOBUF_ANR.getNumber())
                .withEventSource("import_api")
                .withEventFirstOccurrence("undefined")
                .withCrashEncodeType("unknown")
                .withDecodeStatus("unknown")
                .withEventNumber(BigInteger.ONE)
                .withEventValue(ByteString.fromBytes(new byte[]{}))
                .withVersion(BigInteger.ZERO)
                .withSign(1);
    }

}
