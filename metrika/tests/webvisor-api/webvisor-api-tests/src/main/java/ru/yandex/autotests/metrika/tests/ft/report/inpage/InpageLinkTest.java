package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import java.util.Collection;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 22.12.2014.
 */
@Features(Requirements.Feature.INPAGE)
@Stories({Requirements.Story.Inpage.LINK})
@Title("In-page аналитика: проверка карты ссылок")
@RunWith(Parameterized.class)
public class InpageLinkTest extends InpageBaseTest {

    private MapsV1DataLinkMapGETSchema result;

    private List<List<Double>> data;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> data() {
        MapsV1DataLinkGETSchema result = user.onInpageSteps()
                .getInpageLinkUrlsAndExpectSuccess(getInpageUrlsParameters());

        return getUrls(user.onResultSteps().getInpageUrls(result));
    }

    @Override
    protected void additionalBefore() {
        result = user.onInpageSteps().getInpageLinkDataAndExpectSuccess(inpageDataParameters);
        data = user.onResultSteps().getInpageLinkData(result);
    }

    @Test
    public void inpageLinkDataSizeTest() {
        assertThat("Все строки данных содержат одинаковое количество элементов, равное интервалу дат", data,
                everyItem(iterableWithSize(DATES_DIFF)));
    }

    @Test
    public void inpageLinkDataTest() {
        assertThat("Данные содержат числовые неотрицательные значения", data,
                everyItem(everyItem(greaterThanOrEqualTo(0d))));
    }

}
