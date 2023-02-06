package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderList;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithPermissions;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getDefaultReportOrder;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.permission.ReportOrderPermissionTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: проверка поля writeAccess")
@RunWith(Parameterized.class)
public class ReportOrderWriteAccessTest {

    private static final UserSteps counterOwnerUser = new UserSteps().withUser(COUNTER_OWNER);
    private static final UserSteps reportOrderOwnerUser = new UserSteps().withUser(REPORT_ORDER_OWNER);

    private static Long counterId;

    private UserSteps user;
    private Long reportOrderId;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("владелец счетчика", COUNTER_OWNER, true),
                toArray("представитель владельца счетчика", COUNTER_OWNER_DELEGATE, true),
                toArray("владелец заказанного отчета", REPORT_ORDER_OWNER, true),
                toArray("представитель владельца заказанного отчета", REPORT_ORDER_OWNER_DELEGATE, true),
                toArray("с доступом на редактирование", GRANTEE_WRITE_ACCESS, true),
                toArray("суперпользователь", SUPER_USER, true),
                toArray("саппорт", SUPPORT, true),
                toArray("с доступом на чтение", GRANTEE_READ_ACCESS, false),
                toArray("менеджер", MANAGER, false),
                toArray("менеджер Директа", MANAGER_DIRECT, false)
        );
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public User userParam;

    @Parameterized.Parameter(2)
    public boolean expectedWriteAccess;

    @BeforeClass
    public static void initClass() {
        counterId = counterOwnerUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithPermissions(
                        of(REPORT_ORDER_OWNER, GRANTEE_READ_ACCESS),
                        of(GRANTEE_WRITE_ACCESS)
                ))
                .getId();
    }

    @Before
    public void init() {
        user = new UserSteps().withUser(userParam);

        reportOrderId = reportOrderOwnerUser.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getDefaultReportOrder())
                .getId();
    }

    @Test
    public void testGetReportOrder() {
        ReportOrder reportOrder = user.onManagementSteps().onReportOrderSteps()
                .getReportOrder(counterId, reportOrderId);

        assertThat("поле writeAccess у полученного заказанного отчета соответствует ожиданию",
                reportOrder.getWriteAccess(), equalTo(expectedWriteAccess)
        );
    }

    @Test
    public void testGetReportOrders() {
        ReportOrderList reportOrderList = user.onManagementSteps().onReportOrderSteps()
                .findReportOrders(counterId);

        assertThat("поле writeAccess полученных заказанных отчетов соответствует ожиданию",
                reportOrderList.getData().get(0).getWriteAccess(), equalTo(expectedWriteAccess)
        );
    }

    @After
    public void cleanup() {
        reportOrderOwnerUser.onManagementSteps().onReportOrderSteps()
                .deleteReportOrder(counterId, reportOrderId);
    }

    @AfterClass
    public static void cleanupClass() {
        counterOwnerUser.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
