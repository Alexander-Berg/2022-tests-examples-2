package ru.yandex.autotests.metrika.tests.ft.report.inpage;

import java.util.List;

import org.junit.Before;

import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageUrlsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.apache.commons.lang3.StringEscapeUtils.escapeJava;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by okunev on 22.12.2014.
 */
public abstract class InpageBaseTest {

    protected static final String DATE1 = "14daysAgo";
    protected static final String DATE2 = "7daysAgo";
    protected static final int DATES_DIFF = 8;

    /**
     * user инициализируется статически, т.к. он используется на этапе
     * формирования перечня параметров теста
     */
    protected static final UserSteps user = new UserSteps();

    protected static final Counter counter = SENDFLOWERS_RU;

    protected InpageDataParameters inpageDataParameters;

    private static final String METRIC = "ym:pv:pageviews";
    private static final String DIMENSION = "ym:pv:URLHash";

    @Parameter(0)
    public String url;

    @Parameter(1)
    public String title;

    protected static InpageUrlsParameters getInpageUrlsParameters() {
        InpageUrlsParameters inpageUrlsParameters = new InpageUrlsParameters();
        inpageUrlsParameters.setId(counter.get(ID));
        inpageUrlsParameters.setDate1(DATE1);
        inpageUrlsParameters.setDate2(DATE2);

        return inpageUrlsParameters;
    }

    protected static InpageUrlsParameters getUrlsParameters() {
        InpageUrlsParameters inpageUrlsParameters = new InpageUrlsParameters();
        inpageUrlsParameters.setId(counter.get(ID));
        inpageUrlsParameters.setDate1(DATE1);
        inpageUrlsParameters.setDate2(DATE2);
        inpageUrlsParameters.setDimension(DIMENSION);
        inpageUrlsParameters.setMetric(METRIC);

        return inpageUrlsParameters;
    }

    protected static List<Object[]> getUrls(List<String> urls) {
        assumeThat("для теста доступен список адресов", urls, is(not(empty())));

        return urls.stream()
                .map(u -> toArray(u, escapeJava(u)))
                .collect(toList());
    }

    @Before
    public void before() {
        inpageDataParameters = new InpageDataParameters();
        inpageDataParameters.setId(counter.get(ID));
        inpageDataParameters.setUrl(url);
        inpageDataParameters.setDate1(DATE1);
        inpageDataParameters.setDate2(DATE2);

        additionalBefore();
    }

    protected abstract void additionalBefore();

}
