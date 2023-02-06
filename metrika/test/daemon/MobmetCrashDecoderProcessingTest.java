package ru.yandex.metrika.mobmet.crash.decoder.test.daemon;

import java.util.List;

import io.qameta.allure.Description;
import io.qameta.allure.Story;
import io.qameta.allure.junit4.DisplayName;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestName;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.mobmet.crash.decoder.steps.MobileEvent;
import ru.yandex.metrika.mobmet.crash.decoder.steps.MobmetCrashDecoderSteps;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.SandboxDataUnpacker;
import ru.yandex.metrika.mobmet.crash.decoder.test.common.YdbCrashSymbolsLoader;
import ru.yandex.metrika.mobmet.crash.decoder.test.daemon.spring.ConfigHelper;
import ru.yandex.metrika.mobmet.crash.decoder.test.daemon.spring.MobmetCrashDecoderTestConfig;
import ru.yandex.qatools.allure.annotations.Features;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.mobmet.crash.decoder.test.daemon.Matchers.equalToMobileEvents;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = MobmetCrashDecoderTestConfig.class)
@Features("MobmetCrashDecoder")
@Story("Processing")
public class MobmetCrashDecoderProcessingTest {

    private static final Logger log = LoggerFactory.getLogger(MobmetCrashDecoderProcessingTest.class);

    @Rule
    public TestName testName = new TestName();

    @Autowired
    private MobmetCrashDecoderSteps steps;

    @BeforeClass
    public static void init() {
        MediumTestsLogSetup.setup();
        SandboxDataUnpacker.unpack();
        ConfigHelper.configure();

        // Нужно для mobmetCrashDecoderProcessingVersionsTest
        YdbCrashSymbolsLoader.restoreIosFunctions();
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

    @Test
    @Story("Processing")
    @DisplayName("Проверка IO")
    @Description("Сценарий проверки обработки чанка IO")
    public void mobmetCrashDecoderProcessingIOTest() {
        List<MobileEvent> inputChunk = steps.getInputIOTestChunk();

        String chunkId = steps.writeInputChunk(inputChunk);

        steps.waitForEmptyQueue();

        List<MobileEvent> outputChunk = steps.readOutputChunk(chunkId);

        assertThat("события эквивалентны ожидаемым", outputChunk, equalToMobileEvents(inputChunk, Matchers::withIODecodeParams));
    }

    @Test
    @Story("Processing")
    @DisplayName("Проверка инвалидированных событий")
    @Description("Сценарий проверки обработки чанка инвалидированных событий")
    public void mobmetCrashDecoderProcessingInvalidatedEventsTest() {
        List<MobileEvent> inputChunk = steps.getInputInvalidatedEventsTestChunk();

        String chunkId = steps.writeInputChunk(inputChunk);

        steps.waitForEmptyQueue();

        List<MobileEvent> outputChunk = steps.readOutputChunk(chunkId);

        assertThat("события эквивалентны ожидаемым", outputChunk, equalToMobileEvents(inputChunk, Matchers::withInvalidatedEventsDecodeParams));
    }

    @Test
    @Story("Processing")
    @DisplayName("Проверка инвалидированных событий")
    @Description("Сценарий проверки обработки чанка с лимитированными ошибками")
    public void mobmetRateLimitedTest() {
        List<MobileEvent> inputChunk = steps.getRateLimitedChunk();

        String chunkId = steps.writeInputChunk(inputChunk);

        steps.waitForEmptyQueue();

        List<MobileEvent> outputChunk = steps.readOutputChunk(chunkId);

        assertThat("события эквивалентны ожидаемым", outputChunk, equalToMobileEvents(inputChunk, Matchers::withRateLimitedEventsParams));
    }

    @Test
    @Story("Processing")
    @DisplayName("Проверка версий и знаков")
    @Description("Сценарий проверки обработки чанка с версиями и знаками")
    public void mobmetCrashDecoderProcessingVersionsTest() {
        List<MobileEvent> inputChunk = steps.getInputVersionsTestChunk();

        String chunkId = steps.writeInputChunk(inputChunk);

        steps.waitForEmptyQueue();

        List<MobileEvent> outputChunk = steps.readOutputChunk(chunkId);

        assertThat("события эквивалентны ожидаемым", outputChunk, equalToMobileEvents(inputChunk, Matchers::withVersionsDecodeParams));
    }

}
