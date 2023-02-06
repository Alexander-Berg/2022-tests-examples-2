package ru.yandex.metrika.mobmet.crash.decoder.test.daemon;

import java.util.Collection;
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
import org.junit.runners.Parameterized;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.TestContextManager;

import ru.yandex.metrika.common.test.medium.MediumTestsLogSetup;
import ru.yandex.metrika.mobmet.crash.decoder.steps.CrashDataParams;
import ru.yandex.metrika.mobmet.crash.decoder.steps.CrashTestData;
import ru.yandex.metrika.mobmet.crash.decoder.steps.CrashTestDataReader;
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

@ContextConfiguration(classes = MobmetCrashDecoderTestConfig.class)
@Features("MobmetCrashDecoder")
@Story("Decoding")
@RunWith(Parameterized.class)
public class MobmetCrashDecoderDecodingTest {

    private static final Logger log = LoggerFactory.getLogger(MobmetCrashDecoderDecodingTest.class);

    @Rule
    public TestName testName = new TestName();

    @Autowired
    private MobmetCrashDecoderSteps steps;

    @Parameterized.Parameter()
    public String dataPath;

    @Parameterized.Parameter(1)
    public CrashDataParams crashDataParams;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> params() {
        return CrashTestDataReader.CRASH_DATA_PARAMS.stream()
                .map(crashDataParams -> new Object[]{crashDataParams.crashFieldsPath(), crashDataParams})
                .toList();
    }

    @BeforeClass
    public static void init() {
        MediumTestsLogSetup.setup();
        SandboxDataUnpacker.unpack();
        ConfigHelper.configure();

        YdbCrashSymbolsLoader.restoreIosFunctions();
        YdbCrashSymbolsLoader.restoreAndroidFunctions();
    }

    @Before
    public void setup() throws Exception {
        log.info(format("Test %s start", testName.getMethodName()));

        // Вручную поднимаем Spring
        TestContextManager testContextManager = new TestContextManager(getClass());
        testContextManager.prepareTestInstance(this);
        log.debug("Spring application context initialized");

        steps.prepare();
    }

    @After
    public void after() {
        log.info(format("Test %s end", testName.getMethodName()));
    }

    @Test
    @Story("Decoding")
    @DisplayName("Проверка декодирования крешей")
    @Description("Сценарий проверки обработки чанка с крешами")
    public void mobmetCrashDecoderProcessingDecodeTest() {
        CrashTestData crashTestData = CrashTestDataReader.readCrash(crashDataParams);

        MobileEvent inputEvent = steps.convertToMobileEvent(crashTestData);

        String chunkId = steps.writeInputChunk(List.of(inputEvent));

        steps.waitForEmptyQueue();

        List<MobileEvent> outputChunk = steps.readOutputChunk(chunkId);
        List<MobileEvent> expectedChunk = Matchers.withDecodeParams(inputEvent, crashTestData);

        assertThat("события эквивалентны ожидаемым", outputChunk, equalToMobileEvents(expectedChunk));
    }
}
