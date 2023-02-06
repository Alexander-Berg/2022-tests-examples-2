package ru.yandex.metrika.mobmet.crash.decoder.service.library;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.crash.decoder.service.model.CrashParams;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.result.LibraryResult;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;

// Проверка того, что мы генерим EventID также как и ядро
//
//SELECT
//    EventID,
//    APIKey,
//    DeviceIDHash,
//    SessionType,
//    SessionID,
//    EventNumber,
//    UUIDHash
//    FROM crash_events_all
//    WHERE StartDate = today()
//    LIMIT 10
//    FORMAT Vertical
//
//Row 8:
//EventID:      1036866870321430389
//APIKey:       2
//DeviceIDHash: 13835162914495314185
//SessionType:  0
//SessionID:    10000000778
//EventNumber:  22
//UUIDHash:     9820111336803100101
//Row 9:
//EventID:      17127825871615022870
//APIKey:       2
//DeviceIDHash: 9149257893041123294
//SessionType:  1
//SessionID:    10000001637
//EventNumber:  4
//UUIDHash:     5040778948031975021
//Row 10:
//EventID:      11800432097548043914
//APIKey:       10321
//DeviceIDHash: 6277350458094497208
//SessionType:  1
//SessionID:    10000001937
//EventNumber:  19
//UUIDHash:     7612606627916644684
@RunWith(Parameterized.class)
public class LibraryResultTest {

    private static final int LIB_LAYER_ID = 10;

    private LibraryResultFactory factory;

    @Parameterized.Parameter
    public long eventId;
    @Parameterized.Parameter(1)
    public int apiKey;
    @Parameterized.Parameter(2)
    public long deviceId;
    @Parameterized.Parameter(3)
    public byte sessionType;
    @Parameterized.Parameter(4)
    public long sessionId;
    @Parameterized.Parameter(5)
    public long eventNumber;
    @Parameterized.Parameter(6)
    public long uuidHash;

    @Parameterized.Parameters
    public static Collection<Object[]> initParams() {
        return ImmutableList.<Object[]>builder()
                // примеры из КХ
                .add(params("11800432097548043914", "10321", "6277350458094497208", "1", "10000001937", "19", "7612606627916644684"))
                .add(params("1036866870321430389", "2", "13835162914495314185", "0", "10000000778", "22", "9820111336803100101"))
                .add(params("17127825871615022870", "2", "9149257893041123294", "1", "10000001637", "4", "5040778948031975021"))
                // примеры из тестов запускаемых в sandbox (см. также AppleDecodeRunnerTest)
                .add(params(Long.toUnsignedString(1850438952488994759L), "13", "4", "0", "8", "10", "6"))
                .add(params(Long.toUnsignedString(-6939828822573851698L), "13", "40", "0", "80", "100", "60"))
                .build();
    }

    @Before
    public void before() {
        factory = new LibraryResultFactory();
    }

    @Test
    public void test() {
        final int originalAppId = 25;
        final int originalEventId = 1025;
        CrashParams params = new CrashParams(originalAppId, deviceId, originalEventId, OperatingSystem.IOS,
                "versionName", 0, AppEventType.EVENT_PROTOBUF_CRASH, null,
                uuidHash, eventNumber, sessionId, sessionType);
        LibraryResult actual = factory.create(apiKey, params);

        LibraryResult expected = new LibraryResult(apiKey, eventId, originalAppId, originalEventId);

        Assert.assertEquals(expected, actual);
    }

    /**
     * Хорошо бы парсить аргументы так же как и в {@link ru.yandex.metrika.mobmet.crash.decoder.cloud.chunk.data.CrashChunkRow}
     */
    private static Object[] params(String eventId, String apiKey, String deviceId, String sessionType, String sessionId, String eventNumber, String uuidHash) {
        return new Object[]{
                Long.parseUnsignedLong(eventId),
                Integer.parseUnsignedInt(apiKey),
                Long.parseUnsignedLong(deviceId),
                (byte) Integer.parseUnsignedInt(sessionType),
                Long.parseUnsignedLong(sessionId),
                Long.parseUnsignedLong(eventNumber),
                Long.parseUnsignedLong(uuidHash)};
    }
}
