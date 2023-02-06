package ru.yandex.autotests.metrika.tests.ft.management.reportorder.negative;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.CustomError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getRegularReportOrder;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: лимит (негативные)")
public class ReportOrderLimitNegativeTest {

    private static final Long COUNTER_ID = 47357064L; // счетчик с 100 активными заказанными отчетами

    private static final UserSteps user = new UserSteps();

    @Test
    public void test() {
        user.onManagementSteps().onReportOrderSteps()
                .createReportOrderAndExpectError(
                        CustomError.expect(400L, "Превышено максимальное количество активных заказанных отчетов на счётчик"),
                        COUNTER_ID,
                        getRegularReportOrder()
                );
    }
}
