package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.permission;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
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
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithPermissions;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.*;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: разрешения на запись (негативные)")
@RunWith(Parameterized.class)
public class ChartAnnotationWritePermissionNegativeTest {

    private static final UserSteps ownerUser = new UserSteps().withUser(OWNER);

    private static Long counterId;

    private UserSteps user;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("с доступом на чтение", GRANTEE_READ_ACCESS),
                toArray("менеджер", MANAGER),
                toArray("менеджер Директа", MANAGER_DIRECT),
                toArray("чужой", FOREIGN_USER)
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
    }

    @Test
    public void testCreate() {
        user.onManagementSteps().onChartAnnotationSteps()
                .createAnnotationAndExpectError(ACCESS_DENIED, counterId, getDefaultAnnotation());
    }

    @Test
    public void testEdit() {
        Long annotationId = ownerUser.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, getDefaultAnnotation())
                .getId();

        user.onManagementSteps().onChartAnnotationSteps()
                .editAnnotationAndExpectError(ACCESS_DENIED, counterId, annotationId, getDefaultAnnotation());
    }

    @Test
    public void testDelete() {
        Long annotationId = ownerUser.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, getDefaultAnnotation())
                .getId();

        user.onManagementSteps().onChartAnnotationSteps()
                .deleteAnnotationAndExpectError(ACCESS_DENIED, counterId, annotationId);
    }

    @AfterClass
    public static void cleanupClass() {
        ownerUser.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
