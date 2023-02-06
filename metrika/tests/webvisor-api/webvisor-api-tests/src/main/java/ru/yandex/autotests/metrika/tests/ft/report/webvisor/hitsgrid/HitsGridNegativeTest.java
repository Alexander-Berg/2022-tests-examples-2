package ru.yandex.autotests.metrika.tests.ft.report.webvisor.hitsgrid;

import org.junit.Test;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.HitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_COUNTER;
import static ru.yandex.autotests.metrika.errors.ReportError.INCORRECT_VISIT_RU;

public class HitsGridNegativeTest {

    private static UserSteps user = new UserSteps();

    private static final Counter COUNTER = TEST_COUNTER;
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    @Test
    public void testInvalidVisitId() {
        user.onWebVisorSteps()
                .getHitsGridAndExpectError(INCORRECT_VISIT_RU, new HitsGridParameters()
                        .withId(COUNTER.get(ID))
                        .withVisitId("1 435432543")
                        .withDimensions(user.onWebVisorMetadataSteps()
                                .getWebVisorDefaultHitDimensions().getRequired())
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));
    }
}
