package ru.yandex.metrika.userparams2d.tests;

import java.io.IOException;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.rules.TestName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.common.test.medium.YtClient;
import ru.yandex.metrika.dbclients.ytrpc.YtReplicatedTableReadClient;
import ru.yandex.metrika.userparams2d.cache.CacheContainer;
import ru.yandex.metrika.userparams2d.config.UserParamsSettings;
import ru.yandex.metrika.userparams2d.steps.DataSteps;
import ru.yandex.metrika.userparams2d.steps.GenerationSteps;
import ru.yandex.metrika.userparams2d.steps.TestsSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static java.lang.String.format;

@Features("UserParams")
public abstract class AbstractUserParamsTest {

    protected static final Logger log = LoggerFactory.getLogger(AbstractUserParamsTest.class);

    @Autowired
    protected YtClient ytClient;

    @Autowired
    protected YtReplicatedTableReadClient ytReadClient;

    @Autowired
    protected UserParamsSettings settings;

    @Autowired
    protected DataSteps dataSteps;

    @Autowired
    protected TestsSteps testsSteps;

    @Autowired
    protected GenerationSteps generationSteps;

    @Autowired
    protected CacheContainer cacheContainer;

    @Rule
    public TestName testName = new TestName();

    @BeforeClass
    public static void beforeClass() throws IOException {
        UserParamsTestSetup.setup();
    }

    @Before
    public void setup() {
        log.info(format("Test %s start", testName.getMethodName()));
        createYtTables();
        cacheContainer.invalidateAll();
    }

    @After
    public void after() {
        log.info(format("Test %s end", testName.getMethodName()));
    }

    protected void createYtTables() {
        ytClient.clearMapNode(settings.getYtPathPrefix());
        ytClient.createDynamicTable(settings.getParamOwnersYtTable(), settings.getParamOwnersTableSchema());
        ytClient.createDynamicTable(settings.getParamsYtTable(), settings.getParamsTableSchema());
        ytClient.createDynamicTable(settings.getClientUserIdMatchingYtTable(), settings.getParamOwnersWithClientUseIdTableSchema());
    }

}
