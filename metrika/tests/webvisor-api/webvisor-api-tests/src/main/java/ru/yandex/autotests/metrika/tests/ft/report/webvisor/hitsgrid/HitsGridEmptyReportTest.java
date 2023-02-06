package ru.yandex.autotests.metrika.tests.ft.report.webvisor.hitsgrid;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataHitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.HitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 17.06.2015.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица просмотров, пустые отчеты")
public class HitsGridEmptyReportTest {

    private static UserSteps user = new UserSteps();

    private static final Counter COUNTER = TEST_CONDITIONS_LIMIT;
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    @Test
    public void hitsGridEmptyReportTest() {
        WebvisorV2DataHitsGETSchema result = user.onWebVisorSteps()
                .getHitsGridAndExpectSuccess(new HitsGridParameters()
                        .withId(COUNTER.get(ID))
                        .withVisitId("1")
                        .withDimensions(user.onWebVisorMetadataSteps()
                                .getWebVisorDefaultHitDimensions().getRequired())
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));

        assertThat("отчет не содержит данных", result.getData(), empty());
    }
}
