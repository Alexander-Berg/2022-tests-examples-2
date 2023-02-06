package ru.yandex.autotests.audience.management.tests.roles;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.*;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.audience.uploading.UploadingSegment;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.metrika.audience.pubapi.SegmentRequestUploading;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.User.GEO_SEGMENT_ID;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 23.06.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Роли: действия над сегментами разными ролями")
@RunWith(Parameterized.class)
public class SegmentActionsPermissionTest {
    private final User owner = USER_DELEGATOR;
    private final UserSteps userOwner = UserSteps.withUser(owner);

    private UserSteps user;
    private Long segmentId;

    @Parameter
    public String descripion;

    @Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "пользователь {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray("с правом на редактирование", USER_WITH_PERM_EDIT),
                toArray("с ролью суперпользователь", SUPER_USER)
        );
    }

    @Before
    public void setup() {
        user = UserSteps.withUser(userParam);
    }

    @Test
    public void checkCreateSegment() {
        UploadingSegment segment = user.onSegmentsSteps().uploadFile(getContent(SegmentContentType.CRM, false, "\t"),
                ulogin(owner));
        SegmentRequestUploading segmentRequest = getUploadingSegment(SegmentContentType.CRM, false);
        segmentId = segment.getId();
        user.onSegmentsSteps().confirmSegment(segmentId, segmentRequest, ulogin(owner));

        List<BaseSegment> segments = userOwner.onSegmentsSteps().getSegments();

        assertThat("сегмент присутствует в списке", segments,
                hasBeanEquivalent(UploadingSegment.class, getExpectedSegment(segmentRequest)));
    }

    @Test
    public void checkDeleteSegment() {
        segmentId = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.REGULAR), ulogin(owner)).getId();

        user.onSegmentsSteps().deleteSegment(segmentId, ulogin(owner));

        List<BaseSegment> segments = userOwner.onSegmentsSteps().getSegments();

        assertThat("сегмент остуствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }

    @Test
    public void checkEditSegment() {
        MetrikaSegment segment = userOwner.onSegmentsSteps().createMetrika(getMetrikaSegment(MetrikaSegmentType.COUNTER_ID, owner));
        segmentId = segment.getId();

        MetrikaSegment editedSegment = user.onSegmentsSteps().editSegment(segmentId,
                getSegmentToChange(segment, getName(METRIKA_SEGMENT_NAME_PREFIX)), ulogin(owner));

        List<BaseSegment> segments = userOwner.onSegmentsSteps().getSegments();

        assertThat("измененный сегмент присутствует в списке", segments,
                hasBeanEquivalent(MetrikaSegment.class, editedSegment));
    }

    @Test
    public void checkAddGrantForSegment() {
        segmentId = userOwner.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST),ulogin(owner)).getId();

        Grant grant = user.onGrantsSteps().createGrant(segmentId, getGrant(SIMPLE_USER), ulogin(owner));

        List<Grant> grants = user.onGrantsSteps().getGrants(segmentId, ulogin(owner));

        assertThat("аккаунт присутствует в списке прав", grants, hasBeanEquivalent(Grant.class, grant));
    }

    @After
    public void tearDown() {
        userOwner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
