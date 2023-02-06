package ru.yandex.metrika.clickhouse.b2b;

import io.qameta.allure.Allure;
import io.qameta.allure.model.StepResult;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.Test;
import ru.yandex.metrika.clickhouse.properties.ClickhouseStatBoxB2BTestsProperties;
import ru.yandex.metrika.clickhouse.steps.Init;
import ru.yandex.metrika.clickhouse.steps.TestCase;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

public class ClickhouseStatboxB2B00PreparationTest {

    private static final Logger LOG = LogManager.getLogger(ClickhouseStatboxB2B00PreparationTest.class);

    @Test
    public void init() throws Throwable {
        Path rootDir = ClickhouseStatBoxB2BTestsProperties.getInstance().getQueriesBaseDir().resolve("setup");
        LOG.info(String.format("Setup queries dir: %s", rootDir));
        processDDLQuery("create_db");
        processDDLQuery("drop");
        processDDLQuery("counters");
        check("check");
    }

    private void check(String name) throws Throwable {
        Allure.getLifecycle().startStep(UUID.randomUUID().toString(), new StepResult().setName(name));

        Path queryPath = ClickhouseStatBoxB2BTestsProperties.getInstance().getQueriesBaseDir().resolve("test").resolve(name);

        new TestCase(ClickhouseStatBoxB2BTestsProperties.getInstance().getUriTest(),
                ClickhouseStatBoxB2BTestsProperties.getInstance().getUriRef(),
                new String(Files.readAllBytes(queryPath), StandardCharsets.UTF_8)).execute();

        Allure.getLifecycle().stopStep();
    }

    private void processDDLQuery(String name) throws Throwable {
        Allure.getLifecycle().startStep(UUID.randomUUID().toString(), new StepResult().setName(name));

        Path queryPath = ClickhouseStatBoxB2BTestsProperties.getInstance().getQueriesBaseDir().resolve("setup").resolve(name);

        new Init(ClickhouseStatBoxB2BTestsProperties.getInstance().getUriTest(),
                ClickhouseStatBoxB2BTestsProperties.getInstance().getUriRef(),
                new String(Files.readAllBytes(queryPath), StandardCharsets.UTF_8)).execute();

        Allure.getLifecycle().stopStep();
    }
}
