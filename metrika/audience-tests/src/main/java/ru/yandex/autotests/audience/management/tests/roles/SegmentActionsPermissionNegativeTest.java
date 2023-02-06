package ru.yandex.autotests.audience.management.tests.roles;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.MetrikaSegmentType;
import ru.yandex.audience.SegmentContentType;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;

/**
 * Created by ava1on on 23.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: действия над сегментами разными ролями (негативные тесты)")
@RunWith(Parameterized.class)
public class SegmentActionsPermissionNegativeTest {
    private final User owner = USER_DELEGATOR;
    private final UserSteps userOwner = UserSteps.withUser(owner);

    @Parameter
    public String descripion;

    @Parameter(1)
    public User userParam;

    private UserSteps user;
    private Long segmentId;

    @Parameterized.Parameters(name = "пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("с правом на просмотр", USER_WITH_PERM_VIEW),
                toArray("с ролью менеджер", MANAGER),
                toArray("без прав", SIMPLE_USER)
        );
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
    }

    @Test
    public void checkTryUploadFile() {
        user.onSegmentsSteps().uploadFileAndExpectError(ACCESS_DENIED, getContent(SegmentContentType.EMAIL, false, "\t"),
                ulogin(owner));
    }

    @Test
    public void checkTryConfrimUploading() {
        segmentId = userOwner.onSegmentsSteps()
                .uploadFile(getContent(SegmentContentType.EMAIL, false, "\t")).getId();

        user.onSegmentsSteps().confirmSegmentAndExpectError(ACCESS_DENIED, segmentId,
                getUploadingSegment(SegmentContentType.EMAIL, false), ulogin(owner));
    }

    @Test
    public void checkTryDeleteSegment() {
        segmentId = userOwner.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.REGULAR)).getId();

        user.onSegmentsSteps().deleteSegmentAndExpectError(ACCESS_DENIED, segmentId, ulogin(owner));
    }

    @Test
    public void checkTryEditSegment() {
        BaseSegment segment = userOwner.onSegmentsSteps()
                .createMetrika(getMetrikaSegment(MetrikaSegmentType.COUNTER_ID, owner));
        segmentId = segment.getId();

        user.onSegmentsSteps().editSegmentAndExpectError(ACCESS_DENIED, segmentId,
                getSegmentToChange(segment, getName(METRIKA_SEGMENT_NAME_PREFIX)), ulogin(owner));
    }

    @Test
    public void checkTryAddGrantForSegment() {
        segmentId = userOwner.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST)).getId();

        user.onGrantsSteps().createGrantAndExpectError(ACCESS_DENIED, segmentId, getGrant(SIMPLE_USER.toString()),
                ulogin(owner));
    }

    @After
    public void tearDown() {
        userOwner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
