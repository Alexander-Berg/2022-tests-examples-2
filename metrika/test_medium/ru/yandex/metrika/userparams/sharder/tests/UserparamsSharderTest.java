package ru.yandex.metrika.userparams.sharder.tests;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.userparams.sharder.config.UserParamsSharderTestConfig;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParamsSharderTestConfig.class)
public class UserparamsSharderTest extends AbstractUserparamsSharderTest {

    @Before
    public void cleanUp() {
        dataSteps.resetWaitingLogbrokerWriter();
    }

    @Test
    public void correctlyWritesSingleParamTest() throws InterruptedException {
        testSteps.writeParamsAndCheckOutput(List.of(SINGLE_PARAM_WRAPPER));
    }

    @Test
    public void correctlyWritesWrappedBatchTest() throws InterruptedException {
        testSteps.writeParamsAndCheckOutput(List.of(BATCH_PARAM_WRAPPER));
    }

    @Test
    public void correctlyWritesCoupleOfBatchesTest() throws InterruptedException {
        testSteps.writeParamsAndCheckOutput(List.of(BATCH_PARAM_WRAPPER, ANOTHER_SINGLE_PARAM_WRAPPER));
    }
}
