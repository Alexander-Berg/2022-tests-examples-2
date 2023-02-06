package ru.yandex.metrika.schedulerd.tests;

import java.util.List;

import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.rules.TestName;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.schedulerd.helpers.ConfigBuilder;
import ru.yandex.metrika.schedulerd.helpers.ConfigHelper;
import ru.yandex.metrika.schedulerd.helpers.EnvironmentConfigHelper;
import ru.yandex.metrika.schedulerd.helpers.JmxConfigHelper;
import ru.yandex.metrika.schedulerd.steps.SchedulerdSteps;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.spring.CommonMetricsSupportConfig;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = SchedulerdBaseTestConfig.class)
@Import(CommonMetricsSupportConfig.class)
public abstract class SchedulerdBaseTest {
    private static final Logger log = LoggerFactory.getLogger(SchedulerdBaseTest.class);
    private static final List<ConfigHelper> CONFIG_HELPERS = List.of(
            new JmxConfigHelper(SchedulerdBaseTest.class.getName()),
            new EnvironmentConfigHelper()
    );
    private static final ConfigBuilder CONFIG_BUILDER = new ConfigBuilder(
            CONFIG_HELPERS,
            "/ru/yandex/metrika/schedulerd"
    );

    @Rule
    public TestName testName = new TestName();

    @Autowired
    protected SchedulerdSteps steps;

    @BeforeClass
    public static void init() {
        log.info("\n===== INIT ====");
        Log4jSetup.basicArcadiaSetup(Level.ALL);
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.yt.ytclient.bus");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.ApiServiceClient");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.PeriodicDiscovery");
        Log4jSetup.mute("ru.yandex.yt.ytclient.rpc");

        CONFIG_BUILDER.configure();
    }

    @AfterClass
    public static void dicsard() {
        log.info("\n===== DISCARD ====");
    }

    @Before
    public void setup() {
        log.info(String.format("\n=== Test %s start", testName.getMethodName()));
        steps.prepare();
    }

    @After
    public void after() {
        log.info(String.format("\n=== Test %s end", testName.getMethodName()));
    }
}
