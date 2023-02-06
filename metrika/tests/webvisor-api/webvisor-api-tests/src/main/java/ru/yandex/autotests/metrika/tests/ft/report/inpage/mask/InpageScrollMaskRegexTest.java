package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.SCROLL, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Карта скроллов. Маски url(regex)")
public class InpageScrollMaskRegexTest {
    private static UserSteps user = new UserSteps();

    private MapsV1DataScrollGETSchema resultRegex;
    private List<Long> data;
    private List<Long> hits;

    @Before
    public void setup() {
        resultRegex = getResultForUrl(InpageTestData.getRegexUrl());
        assumeThat("Данные есть", resultRegex.getData(), not(empty()));
        hits = resultRegex.getHits();
        data = resultRegex.getData();
    }

    @Test
    public void testDataNotEmpty() {
        assertThat("Результат содержит не нули", data, hasItem(greaterThan(0L)));
    }

    @Test
    public void testHitsNotEmpty() {
        assertThat("Результат содержит не нули", hits, hasItem(greaterThan(0L)));
    }

    private MapsV1DataScrollGETSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageScrollDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
