package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.segment;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.mobmet.dao.MobSegment;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultSegment;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.SEGMENT)
@Stories({
        Requirements.Story.Segments.ADD,
        Requirements.Story.Segments.LIST,
})
@Title("Просмотр сегментов")
@RunWith(Parameterized.class)
public class GetSegmentNegativeTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps ownerSteps = UserSteps.onTesting(OWNER);

    @Parameterized.Parameter
    public User segmentCreator;

    @Parameterized.Parameter(1)
    public User segmentViewer;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    private UserSteps segmentViewerSteps;

    private Long appId;

    private Long segmentId;

    @Parameterized.Parameters(name = "Создатель {0}. Пользователь {1}. {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(SIMPLE_USER, SIMPLE_USER_2, forUser(SIMPLE_USER_2).grant(GrantType.VIEW)),
                param(SIMPLE_USER, SIMPLE_USER_2, forUser(SIMPLE_USER_2).agencyEditGrant()),
                param(SIMPLE_USER, SIMPLE_USER_2, forUser(SIMPLE_USER_2).agencyViewGrant())
        );
    }

    @Before
    public void setup() {
        final UserSteps segmentCreatorSteps = UserSteps.onTesting(segmentCreator);
        segmentViewerSteps = UserSteps.onTesting(segmentViewer);

        final MobSegment segmentToAdd = defaultSegment();

        final Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().createGrant(appId, grant);
        }

        segmentId = segmentCreatorSteps.onSegmentSteps().addSegment(appId, segmentToAdd).getSegmentId();
    }

    @Test
    public void getSegment() {
        segmentViewerSteps.onSegmentSteps()
                .getSegmentAndExpectError(appId, segmentId, FORBIDDEN);
    }

    @Test
    public void getSegmentList() {
        final List<MobSegment> segments = segmentViewerSteps.onSegmentSteps().getSegmentsList(appId);
        assertThat("список сегментов пуст", segments, empty());
    }

    @After
    public void teardown() {
        ownerSteps.onSegmentSteps().deleteSegmentAndIgnoreResult(appId, segmentId);
        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().deleteGrant(appId, grant.getGrant().getUserLogin());
        }
        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] param(User segmentCreator, User segmentViewer, MobmetGrantE grant) {
        return new Object[]{segmentCreator, segmentViewer, new GrantWrapper(grant)};
    }
}

