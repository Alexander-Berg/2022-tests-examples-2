package ru.yandex.autotests.metrika.tests.ft.management.reportorder.negative;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getDefaultReportOrder;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getEditReportOrderNegativeParams;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: изменение заказанного отчета (негативные)")
@RunWith(Parameterized.class)
public class EditReportOrderNegativeTest {

    private static final UserSteps user = new UserSteps();

    private static Long counterId;

    private Long reportOrderId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return getEditReportOrderNegativeParams();
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public ReportOrder reportOrder;

    @Parameterized.Parameter(2)
    public IExpectedError error;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Before
    public void init() {
        reportOrderId = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getDefaultReportOrder())
                .getId();
    }

    @Test
    public void test() {
        user.onManagementSteps().onReportOrderSteps()
                .editReportOrderAndExpectError(error, counterId, reportOrderId, reportOrder);
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
