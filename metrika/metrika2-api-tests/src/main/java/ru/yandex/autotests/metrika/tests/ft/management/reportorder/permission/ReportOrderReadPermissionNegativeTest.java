package ru.yandex.autotests.metrika.tests.ft.management.reportorder.permission;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithPermissions;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getDefaultReportOrder;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.permission.ReportOrderPermissionTestData.*;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: разрешения на чтение (негативные)")
@RunWith(Parameterized.class)
public class ReportOrderReadPermissionNegativeTest {

    private static final UserSteps counterOwnerUser = new UserSteps().withUser(COUNTER_OWNER);
    private static final UserSteps reportOrderOwnerUser = new UserSteps().withUser(REPORT_ORDER_OWNER);

    private static Long counterId;

    private UserSteps user;
    private Long reportOrderId;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("чужой", FOREIGN_USER),
                toArray("неавторизованный", UNAUTHORIZED_USER)
        );
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public User userParam;

    @BeforeClass
    public static void initClass() {
        counterId = counterOwnerUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithPermissions(
                        of(REPORT_ORDER_OWNER, GRANTEE_READ_ACCESS),
                        of(GRANTEE_WRITE_ACCESS)),
                        ignoreQuota(true))
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
        user.onManagementSteps().onReportOrderSteps()
                .getReportOrderAndExpectError(ACCESS_DENIED, counterId, reportOrderId);
    }

    @Test
    public void testGetReportOrderExecutions() {
        user.onManagementSteps().onReportOrderSteps()
                .findReportOrderExecutionsAndExpectError(ACCESS_DENIED, counterId, reportOrderId);
    }

    @Test
    public void testGetReportOrders() {
        user.onManagementSteps().onReportOrderSteps()
                .findReportOrdersAndExpectError(ACCESS_DENIED, counterId);
    }

    @Test
    public void testGetReportExecutions() {
        user.onManagementSteps().onReportOrderSteps()
                .findReportExecutionsAndExpectError(ACCESS_DENIED, counterId);
    }

    @Test
    public void testGetExecution() {
        user.onManagementSteps().onReportOrderSteps()
                .getReportExecutionAndExpectError(ACCESS_DENIED, counterId, 1L);
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
