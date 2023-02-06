package ru.yandex.metrika.lambda.test;

import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import io.qameta.allure.junit4.DisplayName;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.lambda.steps.LambdaSteps;
import ru.yandex.metrika.util.log.Log4jSetup;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = {
        "/ru/yandex/metrika/util/common-jmx-support.xml",
        "/ru/yandex/metrika/util/common-metrics-support.xml",
        "/ru/yandex/metrika/util/common-jdbc.xml",
        "/ru/yandex/metrika/util/common-console.xml",
        "/ru/yandex/metrika/util/common-yt.xml",
        "/ru/yandex/metrika/util/common-tx.xml",
        "/ru/yandex/metrika/dbclients/clickhouse/clickhouse-log.xml",
        // test stub used "/ru/yandex/metrika/util/juggler-reporter.xml",
        // test stub used "/ru/yandex/metrika/bazinga/worker/worker-context.xml",
        "/ru/yandex/metrika/lambda/lambda-visits.xml",
        "/ru/yandex/metrika/lambda/lambda-visits-v1.xml",
        "/ru/yandex/metrika/lambda/lambda-visits-jdbc.xml",
        "/ru/yandex/metrika/lambda/lambda-dsp.xml",
        "/ru/yandex/metrika/lambda/lambda-recommendation-widget.xml",
        "/ru/yandex/metrika/lambda/lambda-adfox.xml",
        "/ru/yandex/metrika/lambda/lambda-offline-conversion.xml",
        "/ru/yandex/metrika/lambda/lambda-telephony.xml",
        "/ru/yandex/metrika/lambda/lambda-cdp-order.xml",
        //Степы тестов
        "/ru/yandex/metrika/lambda/steps/lambda-test-steps.xml"
})
@Epic("Лямбда")
@Feature("Lambda-Visits")
@Story("End-to-End")
public class LambdaTest {

    private static final Logger log = LoggerFactory.getLogger(LambdaTest.class);

    @Autowired
    private LambdaSteps steps;

    @BeforeClass
    public static void init() {

        Log4jSetup.basicArcadiaSetup(Level.ALL);
        Log4jSetup.mute("ru.yandex.yt.ytclient.rpc");
        Log4jSetup.mute("ru.yandex.yt.ytclient.bus");
        Log4jSetup.mute("ru.yandex.misc.io.http.apache.v4.ApacheHttpClient4Utils");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.ApiServiceClient");
        Log4jSetup.mute("ru.yandex.yt.ytclient.proxy.PeriodicDiscovery");
        Log4jSetup.mute("com.codahale.metrics.graphite.GraphiteReporter");

        ConfigHelper.configure();
    }

    @Before
    public void setup() {
        steps.configureYt();
        steps.configureMysql();

        steps.performScenario();

        steps.canonizeOutput();
    }

    @Test
    @Story("Инварианты")
    @DisplayName("Проверка инвариантов")
    @Description("Сценарий проверки всех тасок лямбды, инвариантов и канонизация")
    public void invariants() {
        steps.checkInvariants();
    }

    @After
    public void diagnostics() {
        steps.dumpCypressState();
    }
}
