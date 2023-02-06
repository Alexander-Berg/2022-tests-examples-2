package ru.yandex.autotests.metrika.tests.b2b.inpage;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.lang.String.valueOf;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Inpage.SCROLL})
@Title("B2B - In-page аналитика: длинная карта скроллинга")
public class B2bInpageScrollHugeHeightTest extends B2bInpageScrollTest {

    @Override
    protected InpageDataParameters getReportParameters() {
        return new InpageDataParameters()
                .withId(COUNTER.get(ID))
                .withUrl(url)
                .withAccuracy("full")
                .withHeight(valueOf(100001))
                .withDate1("14daysAgo")
                .withDate2("3daysAgo");
    }

}
