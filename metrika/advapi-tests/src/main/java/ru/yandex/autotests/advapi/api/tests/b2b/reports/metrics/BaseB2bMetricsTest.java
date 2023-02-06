package ru.yandex.autotests.advapi.api.tests.b2b.reports.metrics;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.api.tests.b2b.reports.BaseB2bTest;
import ru.yandex.autotests.advapi.data.metadata.ParametrizationTypeEnum;
import ru.yandex.autotests.advapi.data.metadata.TableEnum;
import ru.yandex.autotests.advapi.parameters.CommonReportParameters;
import ru.yandex.autotests.advapi.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;

import java.util.Collection;

import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.advapi.data.common.Campaign.YNDX_MARKET_W;
import static ru.yandex.autotests.advapi.data.common.Campaign.YNDX_TAXI;
import static ru.yandex.autotests.advapi.parameters.GoalIdParameters.goalId;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;

/**
 * Created by omaz on 05.12.2014.
 */
public abstract class BaseB2bMetricsTest extends BaseB2bTest {

    @Parameterized.Parameter()
    public String metricName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String DIMENSION = "am:e:creative";

    @Parameterized.Parameters(name = "Метрика {0}")
    public static Collection createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getMetrics(table(TableEnum.EVENTS)),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(YNDX_MARKET_W.date1)
                                .withDate2(YNDX_MARKET_W.date2)
                                .withId(YNDX_MARKET_W.id)
                                .withLimit(10))))
                .apply(table(TableEnum.EVENTS), setParameters(new CommonReportParameters().withDimension(DIMENSION)))
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(YNDX_MARKET_W.goalId)))
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .apply(
                        matches(anyOf(
                                equalTo("am:e:cpmu"),
                                equalTo("am:e:cpm"))),
                        setParameters(new CommonReportParameters().withSort(DIMENSION)))
                .apply(
                        matches(anyOf(
                                equalTo("am:e:clicks"),
                                equalTo("am:e:allClicks"),
                                equalTo("am:e:fraudClicks"),
                                equalTo("am:e:goal<goal_id>ReachesPostClick"))),
                        setParameters(new TableReportParameters()
                                .withDate1(YNDX_TAXI.date1)
                                .withDate2(YNDX_TAXI.date2)
                                .withGoalId(YNDX_TAXI.goalId)
                                .withId(YNDX_TAXI.id)
                                .withIncludeUndefined(true)
                                .withLimit(10)))
                .build(identity());
    }
}
