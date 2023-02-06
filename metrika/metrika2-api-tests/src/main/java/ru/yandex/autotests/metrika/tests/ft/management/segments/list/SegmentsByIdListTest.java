package ru.yandex.autotests.metrika.tests.ft.management.segments.list;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithEditPermission;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultSegment;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 20.11.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Получение списков сегментов по списку идентификаторов")
public class SegmentsByIdListTest {
    private static UserSteps user;
    private static UserSteps userWithPermission;
    private static UserSteps userWithoutPermission;

    private static User restrictedUserWithPermission = SIMPLE_USER;
    private static User restrictedUserWithoutPermission = Users.SIMPLE_USER2;

    private static Segment segment;
    private static Long counterId;
    private static Long segmentId;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        userWithPermission = new UserSteps().withUser(restrictedUserWithPermission);
        userWithoutPermission = new UserSteps().withUser(restrictedUserWithoutPermission);

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounterWithEditPermission(restrictedUserWithPermission)).getId();

        segment = getDefaultSegment();

        segmentId = user.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, segment).getSegmentId();
    }

    @Test
    public void segmentsListGetCounterListByIdTest() {
        List<Segment> segments = user.onManagementSteps().onSegmentsSteps()
                .getSegmentsAndExpectSuccess(counterId, asList(segmentId));

        assertThat("сегмент присутствует в списке сегментов", segments, hasItem(beanEquivalent(segment)));
    }

    @Test
    public void segmentsListGetCounterListByIdWithPermissionTest() {
        List<Segment> segments =
                userWithPermission.onManagementSteps().onSegmentsSteps()
                        .getSegmentsAndExpectSuccess(counterId, asList(segmentId));

        assertThat("сегмент присутствует в списке сегментов", segments, hasItem(beanEquivalent(segment)));
    }

    @Test
    public void segmentsListGetCounterListByIdWithoutPermissionTest() {
        userWithoutPermission.onManagementSteps().onSegmentsSteps()
                .getSegmentsAndExpectError(
                        ACCESS_DENIED,
                        counterId,
                        asList(segmentId));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
