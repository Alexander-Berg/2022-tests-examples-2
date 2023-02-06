package ru.yandex.metrika.visor3d.tests;

import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.rules.TestName;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.visor3d.steps.Visor3dSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static java.lang.String.format;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = {
        "/ru/yandex/metrika/util/common-jmx-support.xml",
        "/ru/yandex/metrika/util/common-monitoring-support.xml",
        "/ru/yandex/metrika/util/common-metrics-support.xml",
        "/ru/yandex/metrika/util/common-jdbc.xml",
        "/ru/yandex/metrika/util/common-console.xml",
        "/ru/yandex/metrika/util/juggler-reporter.xml",
        "/ru/yandex/metrika/visord/visor3d-cloud.xml",
        "/ru/yandex/metrika/visord/visor3d-logbroker-source.xml",
        "/ru/yandex/metrika/visord/visor3d-logbroker.xml",
        "/ru/yandex/metrika/visord/visor3d-copier-logbroker-source.xml",
        "/ru/yandex/metrika/visord/visor3d-copier-logbroker.xml",
        "/ru/yandex/metrika/visord/visor3d-jdbc.xml",
        "/ru/yandex/metrika/visord/visor3d.xml",
        "/ru/yandex/metrika/visord/visor3d-copier.xml",
        "/ru/yandex/metrika/dbclients/clickhouse/clickhouse-log.xml",
        "/ru/yandex/metrika/webvisor-yt-connection.xml",
        "/ru/yandex/metrika/webvisor-yt.xml",
        "/ru/yandex/metrika/webvisor-yt-rpc.xml",
        "/ru/yandex/metrika/webvisor-serialization.xml",
        "/ru/yandex/metrika/webvisor-serialization-writer.xml",
        "/ru/yandex/metrika/webvisor-eventstat.xml",
        //Степы тестов
        "/ru/yandex/metrika/visor3d/steps/visor3d-steps.xml"
})
@Features("Visor3d")
public abstract class Visor3dBaseTest {

    private static final Logger log = LoggerFactory.getLogger(Visor3dBaseTest.class);

    @Rule
    public TestName testName = new TestName();

    @Autowired
    protected Visor3dSteps steps;

    @BeforeClass
    public static void init() {
        Log4jSetup.basicArcadiaSetup(Level.ALL);
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.yt.ytclient.bus");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.ApiServiceClient");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.PeriodicDiscovery");
        Log4jSetup.mute("ru.yandex.yt.ytclient.rpc");

        ConfigHelper.configure();
    }

    @Before
    public void setup() {
        log.info(format("Test %s start", testName.getMethodName()));
        steps.prepare();
    }

    @After
    public void after() {
        log.info(format("Test %s end", testName.getMethodName()));
    }
}
