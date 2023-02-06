package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import java.util.Collection;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.core.Every.everyItem;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 22.12.2014.
 */
@Features({Requirements.Feature.INPAGE})
@Stories({Requirements.Story.Inpage.SCROLL})
@Title("In-page аналитика: проверка карты скроллинга")
@RunWith(Parameterized.class)
public class InpageScrollTest extends InpageBaseTest {

    private static final int HEIGHT = 100;

    private MapsV1DataScrollGETSchema result;

    private List<Long> data;
    private List<Long> hits;

    private static final String DIMENSION = "ym:pv:URLHash";

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> data() {
        StatV1DataGETSchema result = user.onReportFacedSteps()
                .getTableReportAndExpectSuccess(getUrlsParameters());

        return getUrls(user.onResultSteps().getDimensionNameOnly(DIMENSION, result));
    }

    @Override
    protected void additionalBefore() {
        inpageDataParameters.setHeight(String.valueOf(HEIGHT));

        result = user.onInpageSteps().getInpageScrollDataAndExpectSuccess(inpageDataParameters);

        data = user.onResultSteps().getInpageScrollData(result);
        hits = user.onResultSteps().getInpageScrollHits(result);
    }

    @Test
    public void inpageScrollDataSizeTest() {
        assumeThat("для теста доступен список адресов", result.getData(), is(not(empty())));
        assertThat("Размер данных соответствует указанному", data, iterableWithSize(HEIGHT));
    }

    @Test
    public void inpageScrollDataTest() {
        assertThat("Данные содержат числовые неотрицательные значения", data,
                everyItem(greaterThanOrEqualTo(0L)));
    }

    @Test
    public void inpageScrollHitsSizeTest() {
        assumeThat("для теста доступен список адресов", result.getData(), is(not(empty())));
        assertThat("Размер хитов соответствует указанному", hits, iterableWithSize(HEIGHT));
    }

    @Test
    public void inpageScrollHitsTest() {
        assertThat("Хиты содержат числовые неотрицательные значения", hits,
                everyItem(greaterThanOrEqualTo(0L)));
    }

}
