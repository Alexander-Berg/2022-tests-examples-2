package ru.yandex.metrika.mobmet.crash.decoder.cloud.chunk;

import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.crash.decoder.cloud.chunk.dao.CrashRateLimitsSettingsDao;
import ru.yandex.metrika.mobmet.crash.decoder.service.model.CrashParams;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.type.OperatingSystem;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_CRASH;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ERROR;

public class CrashRateLimiterTest {

    private final int BATCH_SIZE = 100;

    private final int LIMITED_APP_LIMIT = 20;
    private final int DEFAULT_LIMIT = 50;

    private static final int LIMITED_APP = 1;
    private static final int UNLIMITED_APP = 2;

    private CrashRateLimiter crashRateLimiter;

    @Before
    public void before() {
        CrashRateLimitsSettingsDao dao = mock(CrashRateLimitsSettingsDao.class);
        when(dao.getLimitedApps()).thenReturn(Map.of(LIMITED_APP, (long) LIMITED_APP_LIMIT));
        crashRateLimiter = new CrashRateLimiter(dao);
        crashRateLimiter.setDefaultLimit(DEFAULT_LIMIT);
        crashRateLimiter.refresh();
    }

    @Test
    public void crashesIsNotLimited() {
        var params = Collections.nCopies(BATCH_SIZE, params(LIMITED_APP, 1, 1, LIMITED_APP_LIMIT + 1, EVENT_PROTOBUF_CRASH));
        assertThat(params).allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
    }

    @Test
    public void unlimitedAppsIsNotLimited() {
        var params = Collections.nCopies(BATCH_SIZE, params(UNLIMITED_APP, 1, 1, DEFAULT_LIMIT + 1, EVENT_PROTOBUF_ERROR));
        assertThat(params).allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
    }

    @Test
    public void smallEventNumberIsNotLimited() {
        var params = Collections.nCopies(BATCH_SIZE, params(LIMITED_APP, 1, 1, LIMITED_APP_LIMIT - 1, EVENT_PROTOBUF_ERROR));
        assertThat(params).allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
    }

    @Test
    public void distinctSessionsIsNotLimited() {
        var params = IntStream.range(0, BATCH_SIZE)
                .mapToObj(n -> params(LIMITED_APP, 1, n, LIMITED_APP_LIMIT - 1, EVENT_PROTOBUF_ERROR))
                .collect(Collectors.toList());
        assertThat(params).allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
    }

    @Test
    public void distinctDevicesIsNotLimited() {
        var params = IntStream.range(0, BATCH_SIZE)
                .mapToObj(n -> params(LIMITED_APP, n, 1, LIMITED_APP_LIMIT + 1, EVENT_PROTOBUF_ERROR))
                .collect(Collectors.toList());
        assertThat(params).allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
    }

    @Test
    public void limitedAppIsLimited() {
        var params = Collections.nCopies(BATCH_SIZE, params(LIMITED_APP, 1, 1, LIMITED_APP_LIMIT + 1, EVENT_PROTOBUF_ERROR));
        assertThat(params.subList(0, LIMITED_APP_LIMIT))
                .allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
        assertThat(params.subList(LIMITED_APP_LIMIT, params.size()))
                .allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isTrue());
    }

    @Test
    public void limitedForUnlimitedIfSettingEnabled() {
        crashRateLimiter.setEnabledForAnyAppByDefault(true);

        var params = Collections.nCopies(BATCH_SIZE, params(UNLIMITED_APP, 1, 1, DEFAULT_LIMIT + 1, EVENT_PROTOBUF_ERROR));
        assertThat(params.subList(0, DEFAULT_LIMIT))
                .allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isFalse());
        assertThat(params.subList(DEFAULT_LIMIT, params.size()))
                .allSatisfy(p -> assertThat(crashRateLimiter.isRateLimited(p)).isTrue());
    }

    public CrashParams params(int appId,
                              long deviceIDHash,
                              long sessionID,
                              long eventNumber,
                              AppEventType eventType) {
        return new CrashParams(appId,
                deviceIDHash,
                ThreadLocalRandom.current().nextLong(),
                OperatingSystem.IOS,
                UUID.randomUUID().toString(),
                ThreadLocalRandom.current().nextLong(),
                eventType,
                "",
                0,
                eventNumber,
                sessionID,
                (byte) 0);
    }
}
