package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.CLICK, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Карта кликов. Маски url (regex)")
public class InpageClicksMaskRegexTest {

    private static UserSteps user = new UserSteps();

    private MapsV1DataClickGETSchema resultRegex;

    @Before
    public void setup() {
        resultRegex = getResultForUrl(InpageTestData.getRegexUrl());
    }

    @Test
    public void testDataNotEmpty() {
        assertThat("Результат не пустой", resultRegex.getData().getTotal(), greaterThan(0L));
    }

    private MapsV1DataClickGETSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageClickDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
