package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.List;
import java.util.Map;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasValue;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.LINK, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Карта ссылок. Маски url(regex)")
public class InpageLinkMaskRegexTest {
    private static UserSteps user = new UserSteps();

    private MapsV1DataLinkMapGETSchema resultRegex;
    private Map<String, List<Integer>> linkData;

    @Before
    public void setup() {
        resultRegex = getResultForUrl(InpageTestData.getRegexUrl());
        assumeThat("Данные есть", resultRegex.getData(), not(empty()));
        linkData = resultRegex.getData().getL();
    }

    @Test
    public void testDataNotEmpty() {
        assertThat("Результат содержит не нули", linkData, hasValue(hasItem(greaterThan(0))));
    }

    private MapsV1DataLinkMapGETSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageLinkDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
