package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.permission;

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
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithPermissions;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.*;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: разрешения на чтение")
@RunWith(Parameterized.class)
public class ChartAnnotationReadPermissionTest {

    private static final UserSteps ownerUser = new UserSteps().withUser(OWNER);

    private static Long counterId;

    private UserSteps user;
    private Long annotationId;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("владелец", OWNER),
                toArray("представитель владельца", DELEGATE),
                toArray("с доступом на редактирование", GRANTEE_WRITE_ACCESS),
                toArray("суперпользователь", SUPER_USER),
                toArray("саппорт", SUPPORT),
                toArray("с доступом на чтение", GRANTEE_READ_ACCESS),
                toArray("менеджер", MANAGER),
                toArray("менеджер Директа", MANAGER_DIRECT)
        );
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public User userParam;

    @BeforeClass
    public static void initClass() {
        counterId = ownerUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithPermissions(GRANTEE_READ_ACCESS, GRANTEE_WRITE_ACCESS),
                        ignoreQuota(true))
                .getId();
    }

    @Before
    public void init() {
        user = new UserSteps().withUser(userParam);

        annotationId = ownerUser.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, getDefaultAnnotation())
                .getId();
    }

    @Test
    public void testGet() {
        user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotation(counterId, annotationId);
    }

    @Test
    public void testGetList() {
        user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotations(counterId);
    }

    @After
    public void cleanup() {
        ownerUser.onManagementSteps().onChartAnnotationSteps()
                .deleteAnnotation(counterId, annotationId);
    }

    @AfterClass
    public static void cleanupClass() {
        ownerUser.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
