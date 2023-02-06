package ru.yandex.autotests.audience.management.tests.grants;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.audience.BaseSegment;
import ru.yandex.audience.geo.GeoSegment;
import ru.yandex.audience.geo.GeoSegmentType;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

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
@Title("Доступ: выдача доступа на сегмент")
public class AddGrantTest {
    private static final UserSteps user = UserSteps.withUser(SIMPLE_USER);
    private static final User GRANTEE = USER_GRANTEE;

    private final UserSteps userGrantee = UserSteps.withUser(GRANTEE);

    private static GeoSegment segment;
    private static Long segmentId;
    private static Grant grant;

    @BeforeClass
    public static void setup() {
        segment = user.onSegmentsSteps().createGeo(getGeoCircleSegment(GeoSegmentType.REGULAR));
        segmentId = segment.getId();
        grant = getGrant(GRANTEE);

        user.onGrantsSteps().createGrant(segmentId, grant);
    }

    @Test
    public void checkAddGrant() {
        List<Grant> grants = user.onGrantsSteps().getGrants(segmentId);

        assertThat("доступ присутствует в списке", grants,
                hasBeanEquivalent(Grant.class, grant));
    }

    @Test
    public void checkGranteeSegmentList() {
        List<BaseSegment> granteeSegments = userGrantee.onSegmentsSteps().getSegments();

        assertThat("сегмент присутствует в списке у пользователя, которому выдали права", granteeSegments,
                hasBeanEquivalent(GeoSegment.class, segment.withGuestQuantity(1L).withHasGuests(Boolean.TRUE),
                        BeanFieldPath.newPath("guest")));
    }

    @AfterClass
    public static void tearDown() {
        user.onSegmentsSteps().deleteSegmentAndIgnoreStatus(segmentId);
    }
}
