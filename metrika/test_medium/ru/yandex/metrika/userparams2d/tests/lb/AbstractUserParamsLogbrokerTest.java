package ru.yandex.metrika.userparams2d.tests.lb;

import org.junit.Before;

import ru.yandex.metrika.userparams2d.tests.AbstractUserParamsTest;

public abstract class AbstractUserParamsLogbrokerTest extends AbstractUserParamsTest {

    @Before
    public void cleanUpLogbroker() {
        dataSteps.clearOutputGigaTopic();
        dataSteps.clearOutputNanoTopic();
    }
}
