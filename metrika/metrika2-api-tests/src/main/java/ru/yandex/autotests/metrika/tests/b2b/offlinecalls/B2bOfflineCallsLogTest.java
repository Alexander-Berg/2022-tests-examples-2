package ru.yandex.autotests.metrika.tests.b2b.offlinecalls;

import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_COUNTER;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_UPLOADINGS;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.OFFLINE_CALLS;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.EMPTY;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Report.Type.OFFLINE_CALLS_LOG)
@Title("B2B - Лог звонков")
public class B2bOfflineCallsLogTest extends BaseB2bTest {

    private static final String START_DATE = DateConstants.OfflineCalls.START_DATE;
    private static final String END_DATE = DateConstants.OfflineCalls.END_DATE;
    private static final String ACCURACY = "1";
    private static final Counter COUNTER_WITH_NO_CALLS = TEST_COUNTER;

    @Parameterized.Parameter
    public IFormParameters additionalParameters;

    @Parameterized.Parameters(name = "параметры: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][] {
                { EMPTY },
                { new TableReportParameters()
                        .withFilters(dimension("ym:oc:offlineCallMissed").equalTo("yes").build())
                },
                { new TableReportParameters()
                        .withFilters(dimension("ym:oc:offlineCallFirstTimeCaller").equalTo("yes").build())
                },
                { new TableReportParameters()
                        .withFilters(dimension("ym:oc:offlineCallStatic").equalTo("yes").build())
                },
                { new TableReportParameters()
                        .withFilters(dimension("ym:s:trafficSource").equalTo("direct").build())
                },
                { new TableReportParameters()
                        .withFilters(dimension("ym:s:browser").in("3", "70").build()) // Firefox или Яндекс.Браузер
                },
                { new TableReportParameters()
                        .withFilters(exists("ym:u:userID", dimension("ym:u:gender").equalTo("male")).build())
                },
                { new TableReportParameters()
                        .withId(COUNTER_WITH_NO_CALLS)
                        .withFilters(exists("ym:u:userID", dimension("ym:u:pageViews").equalTo(3))
                                .and(dimension("ym:s:regionCountry").notIn(167))
                                .and(dimension("ym:oc:offlineCallGoalID").defined())
                                .build()
                        )
                },
                { new TableReportParameters()
                        .withFilters(dimension("ym:oc:offlineCallStatic").equalTo("no")
                                .and(dimension("ym:oc:offlineCallTalkDuration").greaterThanOrEqualTo(60))
                                .and(dimension("ym:oc:offlineCallTalkDuration").lessThanOrEqualTo(300))
                                .and(dimension("ym:oc:offlineCallMissed").equalTo("no"))
                                .and(dimension("ym:oc:offlineCallFirstTimeCaller").equalTo("yes"))
                                .and(dimension("ym:oc:offlineCallHoldDuration").greaterThan(300))
                                .build()
                        )
                },
                { new TableReportParameters()
                        .withId(3792295L)
                        .withDate1("2017-12-01")
                        .withDate2("2017-12-31")
                        .withFilters(dimension("ym:oc:offlineCallFirstTimeCaller").equalTo("yes")
                                .and(dimension("ym:s:lastSignDirectClickOrder").equalTo("17857438"))
                                .build()
                        )
                },
                { new TableReportParameters()
                        .withId(20781052L)
                        .withDate1("2018-01-01")
                        .withDate2("2018-01-31")
                }
        });
    }

    @Before
    public void setup() {
        requestType = OFFLINE_CALLS;

        reportParameters = makeParameters()
                .append(new TableReportParameters()
                        .withId(TEST_UPLOADINGS)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withAccuracy(ACCURACY)
                )
                .append(additionalParameters);
    }
}
