package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import java.util.Collection;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.matchers.OrderMatcher.isDescendingOrdered;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by okunev on 22.12.2014.
 */
@Features(Requirements.Feature.INPAGE)
@Stories({Requirements.Story.Inpage.FORM})
@Title("In-page аналитика: проверка аналитики форм")
@RunWith(Parameterized.class)
public class InpageFormTest extends InpageBaseTest {

    private MapsV1DataFormGETPOSTSchema result;

    private static final String DIMENSION = "ym:pv:URLHash";

    private List<List<Long>> funnels;
    private List<String> inputNames;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> data() {
        StatV1DataGETSchema result = user.onReportFacedSteps()
                .getTableReportAndExpectSuccess(getUrlsParameters());

        return getUrls(user.onResultSteps().getDimensionNameOnly(DIMENSION, result));
    }

    @Override
    protected void additionalBefore() {
        result = user.onInpageSteps().getInpageFormDataAndExpectSuccess(inpageDataParameters);
        funnels = user.onResultSteps().getInpageFormFunnels(result);
        inputNames = user.onResultSteps().getInpageFormInputNames(result);
    }

    @Test
    public void inpageFormFunnelsTest() {
        assertThat("\"Воронки\" содержат непротиворечивые данные", funnels, everyItem(both(iterableWithSize(3))
                        .and(isDescendingOrdered())));
    }

    @Test
    public void inpageFormInputNamesTest() {
        assertThat("Имена полей ввода заданы", inputNames, everyItem(notNullValue(String.class)));
    }

}
