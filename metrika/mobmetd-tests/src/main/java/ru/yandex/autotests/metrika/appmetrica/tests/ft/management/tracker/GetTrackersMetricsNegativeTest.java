package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.ACCESS_TO_TRACKER_DENIED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.INVALID_PARAMETER;

/**
 * @author dancingelf
 */
@Features(Requirements.Feature.Management.TRACKER)
@Stories(Requirements.Story.Tracker.INFO)
@Title("Получение статистики по трекерам (негативный)")
@RunWith(Parameterized.class)
public class GetTrackersMetricsNegativeTest {

    private static final User PRIVILEGED_USER = SUPER_LIMITED;

    private static final UserSteps privilegedUser = UserSteps.onTesting(PRIVILEGED_USER);
    private static final UserSteps restrictedUser = UserSteps.onTesting(SIMPLE_USER);

    @Parameterized.Parameter
    public Long appId;
    @Parameterized.Parameter(value = 1)
    public String invalidTrackerId;

    @Parameterized.Parameters(name = "Приложение {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(Applications.KINOPOISK, "123ab"))
                .build();
    }

    private List<String> requestedTrackingIds;

    @Before
    public void setup() {
        // Запрашиваем список трекеров для указанного target uid-а, потому что SUPER_LIMITED так может.
        // Иначе нужно было бы выдать грант на приложение, а для приложений yastorepublisher это делается только через IDM.
        long appOwnerUid = privilegedUser.onApplicationSteps().getApplication(appId).getUid();
        requestedTrackingIds = privilegedUser.onTrackerSteps().getTrackerList(appId, appOwnerUid).stream()
                .map(Campaign::getTrackingId)
                .collect(Collectors.toList());
        assumeThat("получены идентификаторы трекера", requestedTrackingIds, not(empty()));
    }

    @Test
    public void testNoAccessToTracker() {
        restrictedUser.onTrackerSteps().getTrackerMetricsAndExpectError(requestedTrackingIds, ACCESS_TO_TRACKER_DENIED);
    }

    @Test
    public void testInvalidTracker() {
        restrictedUser.onTrackerSteps().getTrackerMetricsAndExpectError(
                Collections.singletonList(invalidTrackerId), INVALID_PARAMETER);
    }

    public static Object[] param(Application application, String invalidTrackerId) {
        return toArray(application.get(ID), invalidTrackerId);
    }
}
