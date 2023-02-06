package ru.yandex.autotests.audience.management.tests.grants;

import org.junit.*;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.audience.management.tests.TestData.getGeoCircleSegment;
import static ru.yandex.autotests.audience.management.tests.TestData.getGrant;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Доступ: удаление доступа на сегмент")
public class DeleteGrantTest {
    private static final UserSteps userOwner = UserSteps.withUser(SIMPLE_USER);
    private final UserSteps userGrantee = UserSteps.withUser(USER_GRANTEE);

    private Long segmentId;
    private Grant grant;

    @Before
    public void init() {
        segmentId = userOwner.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.LAST)).getId();
        grant = getGrant();
        userOwner.onGrantsSteps().createGrant(segmentId, grant);

    }

    @Test
    public void checkDeleteGrant() {
        userOwner.onGrantsSteps().deleteGrant(segmentId, grant.getUserLogin());
        List<Grant> grants = userOwner.onGrantsSteps().getGrants(segmentId);

        assertThat("доступ отсутствует в списке", grants,
                not(hasBeanEquivalent(Grant.class, grant)));
    }

    @Test
    public void checkDeleteGrantInSegmentList() {
        userOwner.onGrantsSteps().deleteGrant(segmentId, grant.getUserLogin());
        List<BaseSegment> segments = userGrantee.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }

    @Test
    public void checkDeleteGrantSelf() {
        userGrantee.onGrantsSteps().deleteGrant(segmentId, "");
        List<BaseSegment> segments = userGrantee.onSegmentsSteps().getSegments();

        assertThat("сегмент отсутствует в списке", segments,
                not(hasItem(having(on(BaseSegment.class).getId(), equalTo(segmentId)))));
    }

    @After
    public void cleanUp() {
        userOwner.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
