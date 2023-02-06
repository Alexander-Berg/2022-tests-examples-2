package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.reportorder.ReportOrderListParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.reportorder.ReportOrderListSortType;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderList;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderStatus;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: получение списка заказанных отчетов")
@RunWith(Parameterized.class)
public class GetReportOrdersTest {

    private static final ReportOrder SINGLE_REPORT_ORDER = getSingleReportOrder().withName("Одноразовый отчет");
    private static final ReportOrder REGULAR_REPORT_ORDER = getRegularReportOrder().withName("Регулярный отчет");
    private static final ReportOrder INACTIVE_SINGLE_REPORT_ORDER = getSingleReportOrder().withName("Неактивный одноразовый отчет");

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private static Long counterId;

    @Parameterized.Parameters(name = "Параметры: {0}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray(new ReportOrderListParameters(),
                        new ReportOrderList()
                                .withData(of(INACTIVE_SINGLE_REPORT_ORDER, REGULAR_REPORT_ORDER, SINGLE_REPORT_ORDER))
                                .withTotal(3L)
                ),
                toArray(new ReportOrderListParameters().withType(ReportOrderType.SINGLE),
                        new ReportOrderList()
                                .withData(of(INACTIVE_SINGLE_REPORT_ORDER, SINGLE_REPORT_ORDER))
                                .withTotal(2L)
                ),
                toArray(new ReportOrderListParameters().withType(ReportOrderType.REGULAR),
                        new ReportOrderList()
                                .withData(of(REGULAR_REPORT_ORDER))
                                .withTotal(1L)
                ),
                toArray(new ReportOrderListParameters().withStatus(ReportOrderStatus.ACTIVE),
                        new ReportOrderList()
                                .withData(of(REGULAR_REPORT_ORDER, SINGLE_REPORT_ORDER))
                                .withTotal(2L)
                ),
                toArray(new ReportOrderListParameters().withStatus(ReportOrderStatus.INACTIVE),
                        new ReportOrderList()
                                .withData(of(INACTIVE_SINGLE_REPORT_ORDER))
                                .withTotal(1L)
                ),
                toArray(new ReportOrderListParameters().withLimit(1),
                        new ReportOrderList()
                                .withData(of(INACTIVE_SINGLE_REPORT_ORDER))
                                .withTotal(3L)
                ),
                toArray(new ReportOrderListParameters().withOffset(1).withLimit(1),
                        new ReportOrderList()
                                .withData(of(REGULAR_REPORT_ORDER))
                                .withTotal(3L)
                ),
                toArray(new ReportOrderListParameters().withSortType(ReportOrderListSortType.CREATE_TIME),
                        new ReportOrderList()
                                .withData(of(INACTIVE_SINGLE_REPORT_ORDER, REGULAR_REPORT_ORDER, SINGLE_REPORT_ORDER))
                                .withTotal(3L)
                ),
                toArray(new ReportOrderListParameters().withSortType(ReportOrderListSortType.END_DATE),
                        new ReportOrderList()
                                .withData(of(REGULAR_REPORT_ORDER, INACTIVE_SINGLE_REPORT_ORDER, SINGLE_REPORT_ORDER))
                                .withTotal(3L)
                )
        );
    }

    @Parameterized.Parameter
    public ReportOrderListParameters parameters;

    @Parameterized.Parameter(1)
    public ReportOrderList expectedReportOrderList;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, SINGLE_REPORT_ORDER);

        user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, REGULAR_REPORT_ORDER);

        user.onManagementSteps().onReportOrderSteps()
                .inactivateReportOrder(counterId, user.onManagementSteps().onReportOrderSteps()
                        .createReportOrder(counterId, INACTIVE_SINGLE_REPORT_ORDER)
                        .getId()
                );
    }

    @Test
    public void test() {
        ReportOrderList reportOrderList = user.onManagementSteps().onReportOrderSteps()
                .findReportOrders(counterId, parameters);

        assertThat("полученный список заказанных отчетов соответствует ожиданию",
                reportOrderList, beanEquivalent(expectedReportOrderList)
        );
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
