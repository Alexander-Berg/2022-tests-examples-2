package ru.yandex.autotests.metrika.tests.b2b.management.reportorder;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportExecution;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.b2b.management.reportorder.B2bReportOrderManagementTestData.REPORT_ORDER_WITH_DATA_COUNTER;
import static ru.yandex.autotests.metrika.tests.b2b.management.reportorder.B2bReportOrderManagementTestData.REPORT_ORDER_WITH_DATA_EXECUTION_ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features({Requirements.Feature.MANAGEMENT, Requirements.Feature.DATA})
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("B2B - Заказанные отчеты: получение информации о выполнении заказанного отчета")
public class B2bGetReportExecutionTest {

    private static final UserSteps userOnTest = new UserSteps();
    private static final UserSteps userOnRef = new UserSteps().useReference();

    @Test
    public void test() {
        ReportExecution testingReportExecution = getReportExecution(userOnTest);
        ReportExecution referenceReportExecution = getReportExecution(userOnRef);

        assertThat("ответы совпадают", testingReportExecution, beanEquivalent(referenceReportExecution));
    }

    private ReportExecution getReportExecution(UserSteps user) {
        return user.onManagementSteps().onReportOrderSteps()
                .getReportExecution(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID);
    }
}
