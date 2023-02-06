package ru.yandex.metrika.mobmet.crash.decoder.test.ydb;

import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.YdbTestUtils;

public class YdbPingTest {

    @BeforeClass
    public static void init() {
        MediumTestsLogSetup.setup();
    }

    @Test
    public void test() {
        try (YdbSessionManager sessionManager = new YdbSessionManager(YdbTestUtils.getTestProperties())) {
            YdbTemplate template = new YdbTemplate(sessionManager);
            template.ping();
        }
    }
}
