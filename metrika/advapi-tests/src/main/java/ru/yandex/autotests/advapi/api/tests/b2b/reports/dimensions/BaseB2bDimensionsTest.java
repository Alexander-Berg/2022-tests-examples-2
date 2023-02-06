package ru.yandex.autotests.advapi.api.tests.b2b.reports.dimensions;

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
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.advapi.data.common.Campaign.YNDX_MARKET_W;
import static ru.yandex.autotests.advapi.parameters.GoalIdParameters.goalId;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;

/**
 * Created by omaz on 05.12.2014.
 */
public abstract class BaseB2bDimensionsTest extends BaseB2bTest {

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public FreeFormParameters tail;

    public static final String METRIC = "am:e:renders";

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getDimensions(table(TableEnum.EVENTS)),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withDate1(YNDX_MARKET_W.date1)
                                .withDate2(YNDX_MARKET_W.date2)
                                .withId(YNDX_MARKET_W.id))))
                .apply(table(TableEnum.EVENTS), setParameters(new CommonReportParameters().withMetric(METRIC)))
                .apply(parameterized(ParametrizationTypeEnum.GOAL_ID), setParameters(goalId(YNDX_MARKET_W.goalId)))
                .apply(parameterized(ParametrizationTypeEnum.GROUP), addGroups())
                .apply(matches(equalTo("am:e:browser")), setParameters(new CommonReportParameters().withIncludeUndefined(true)))
                .build(identity());
    }
}
