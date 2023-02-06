package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import org.junit.Test;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageUrlsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.errors.ReportError.WRONG_PARAMETR_URL;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 17.06.2015.
 */
@Features(Requirements.Feature.INPAGE)
@Stories({
        Requirements.Story.Inpage.CLICK,
        Requirements.Story.Inpage.LINK,
        Requirements.Story.Inpage.FORM,
        Requirements.Story.Inpage.SCROLL})
@Title("In-page аналитика: пустые отчеты")
public class InpageEmptyReportTest {

    private static UserSteps user = new UserSteps();

    private static final Counter COUNTER = TEST_CONDITIONS_LIMIT;
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    @Test
    public void emptyFormDataTest() {
        user.onInpageSteps()
                .getInpageFormDataAndExpectError(WRONG_PARAMETR_URL, getInpageDataParameters());
    }

    @Test
    public void emptyScrollDataTest() {
        user.onInpageSteps()
                .getInpageScrollDataAndExpectError(WRONG_PARAMETR_URL, getInpageDataParameters());
    }

    @Test
    public void emptyClickDataTest() {
        user.onInpageSteps()
                .getInpageClickDataAndExpectError(WRONG_PARAMETR_URL, getInpageDataParameters());
    }

    @Test
    public void emptyLinkTest() {
        MapsV1DataLinkGETSchema result = user.onInpageSteps()
                .getInpageLinkUrlsAndExpectSuccess(getInpageUrlsParameters());

        assertThat("отчет не содержит данных", result.getData(), empty());
    }

    @Test
    public void emptyLinkDataTest() {
        user.onInpageSteps()
                .getInpageLinkDataAndExpectError(WRONG_PARAMETR_URL, getInpageDataParameters());
    }

    private static IFormParameters getInpageDataParameters() {
        return new InpageDataParameters()
                .withId(COUNTER.get(ID))
                .withUrl(EMPTY)
                .withHeight("100")
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    private static IFormParameters getInpageUrlsParameters() {
        return new InpageUrlsParameters()
                .withId(COUNTER.get(ID))
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }
}
