package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 20.03.17.
 */
@RunWith(Parameterized.class)
public class ParticularsBaseTableTest {

    protected static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(value = 1)
    public IFormParameters[] reportParameters;

    protected static Object[] createParams(String title, IFormParameters... params) {
        return toArray(title, params);
    }

    @Before
    public void setup() {
        changeTestCaseTitle(title);
    }

}
