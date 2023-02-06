package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.permission;

import org.junit.*;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.chartannotaion.ChartAnnotationTestData.*;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.CHART_ANNOTATIONS)
@Title("Примечания на графиках: разрешения на чтение (негативные)")
public class ChartAnnotationReadPermissionNegativeTest {

    private static final UserSteps ownerUser = new UserSteps().withUser(OWNER);

    private static Long counterId;

    private UserSteps user = new UserSteps().withUser(FOREIGN_USER);
    private Long annotationId;

    @BeforeClass
    public static void initClass() {
        counterId = ownerUser.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Before
    public void init() {
        annotationId = ownerUser.onManagementSteps().onChartAnnotationSteps()
                .createAnnotation(counterId, getDefaultAnnotation())
                .getId();
    }

    @Test
    public void testGet() {
        user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotationAndExpectError(ACCESS_DENIED, counterId, annotationId);
    }

    @Test
    public void testGetList() {
        user.onManagementSteps().onChartAnnotationSteps()
                .getAnnotationsAndExpectError(ACCESS_DENIED, counterId);
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
