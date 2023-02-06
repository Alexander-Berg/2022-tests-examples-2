package ru.yandex.autotests.metrika.tests.b2b.management.reportorder;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.reportorder.ReportExecutionListParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportExecutionList;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.b2b.management.reportorder.B2bReportOrderManagementTestData.REPORT_ORDER_WITH_DATA_COUNTER;
import static ru.yandex.autotests.metrika.tests.b2b.management.reportorder.B2bReportOrderManagementTestData.REPORT_ORDER_WITH_DATA_ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features({Requirements.Feature.MANAGEMENT, Requirements.Feature.DATA})
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("B2B - Заказанные отчеты: получение списка выполнений заказанного отчета")
@RunWith(Parameterized.class)
public class B2bGetReportOrderExecutionsTest {

    private static final UserSteps userOnTest = new UserSteps();
    private static final UserSteps userOnRef = new UserSteps().useReference();

    @Parameterized.Parameters(name = "Параметры: {0}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray(new ReportExecutionListParameters()),
                toArray(new ReportExecutionListParameters().withLimit(5)),
                toArray(new ReportExecutionListParameters().withOffset(10).withLimit(5))
        );
    }

    @Parameterized.Parameter
    public ReportExecutionListParameters parameters;

    @Test
    public void test() {
        ReportExecutionList testingReportExecutionList = getReportExecutions(userOnTest);
        ReportExecutionList referenceReportExecutionList = getReportExecutions(userOnRef);

        assertThat("ответы совпадают", testingReportExecutionList, beanEquivalent(referenceReportExecutionList));
    }

    private ReportExecutionList getReportExecutions(UserSteps user) {
        return user.onManagementSteps().onReportOrderSteps()
                .findReportOrderExecutions(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_ID, parameters);
    }
}
