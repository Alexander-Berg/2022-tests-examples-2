package ru.yandex.autotests.metrika.tests.ft.report.inpage.mask;

import java.util.List;
import java.util.stream.Collectors;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.report.inpage.InpageTestData;
import ru.yandex.metrika.ui.maps.external.ActivityPageReportExternalInnerForm;
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
@Stories({Requirements.Story.Inpage.FORM, Requirements.Story.Inpage.MASKS})
@Title("In-page аналитика: Аналитика форм. Маски url (regex)")
public class InpageFormMaskRegexTest {
    private static UserSteps user = new UserSteps();

    private MapsV1DataFormGETPOSTSchema resultRegex;
    private List<List<Long>> formsFunnels;

    @Before
    public void setup() {
        resultRegex = getResultForUrl(InpageTestData.getRegexUrl());
        assumeThat("Данные есть", resultRegex.getForms(), not(empty()));
        formsFunnels = resultRegex.getForms().stream().map(ActivityPageReportExternalInnerForm::getFunnels).collect(Collectors.toList());
    }

    @Test
    public void testDataNotEmpty() {
        assertThat("Результат содержит не нули", formsFunnels, hasItem(hasItem(greaterThan(0L))));
    }

    private MapsV1DataFormGETPOSTSchema getResultForUrl(String url) {
        return user.onInpageSteps().getInpageFormDataAndExpectSuccess(InpageTestData.getReportParameters(url));
    }
}
