package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import java.util.Collection;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 22.12.2014.
 */
@Features(Requirements.Feature.INPAGE)
@Stories({Requirements.Story.Inpage.CLICK})
@Title("In-page аналитика: проверка карты кликов")
@RunWith(Parameterized.class)
public class InpageClickTest extends InpageBaseTest {

    private MapsV1DataClickGETSchema result;

    private List<List<Integer>> data;

    private static final String DIMENSION = "ym:pv:URLHash";

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> data() {
        StatV1DataGETSchema result = user.onReportFacedSteps()
                .getTableReportAndExpectSuccess(getUrlsParameters());

        return getUrls(user.onResultSteps().getDimensionNameOnly(DIMENSION, result));
    }

    @Override
    protected void additionalBefore() {
        result = user.onInpageSteps().getInpageClickDataAndExpectSuccess(inpageDataParameters);
        data = user.onResultSteps().getInpageClickData(result);
    }

    @Test
    public void inpageClickDataTest() {
        assertThat("Данные содержат числовые неотрицательные значения", data,
                everyItem(everyItem(greaterThanOrEqualTo(0))));
    }

}
