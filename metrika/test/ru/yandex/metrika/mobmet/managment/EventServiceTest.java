package ru.yandex.metrika.mobmet.managment;

import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.dao.events.EventNamesDao;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationPermission;
import ru.yandex.metrika.mobmet.management.ApplicationsLoadService;
import ru.yandex.metrika.mobmet.management.events.EventService;
import ru.yandex.metrika.mobmet.management.events.EventsRestriction;
import ru.yandex.metrika.mobmet.model.events.EventsRequest;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.mockito.Matchers.anyInt;
import static org.mockito.Matchers.anyObject;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.auth.AuthenticationType.fake;
import static ru.yandex.metrika.auth.MetrikaUserDetails.createExceptionTrigger;
import static ru.yandex.metrika.mobmet.management.events.EventsRestriction.anyAllowed;
import static ru.yandex.metrika.mobmet.management.events.EventsRestriction.restrictedTo;

/**
 * Created by graev on 12/04/2017.
 */
@RunWith(Parameterized.class)
public class EventServiceTest {

    private static final MetrikaUserDetails targetUser = createExceptionTrigger(fake);
    private static final MetrikaUserDetails currentUser = createExceptionTrigger(fake);

    @Parameterized.Parameter
    public String testDescription;

    @Parameterized.Parameter(1)
    public List<String> allEvents;

    @Parameterized.Parameter(2)
    public EventsRequest request;

    @Parameterized.Parameter(3)
    public EventsRestriction agencyRestriction;

    @Parameterized.Parameter(4)
    public List<String> expected;

    public EventService service;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                param("Check agency restriction",
                        of("foo", "bar", "baz"), request(), restrictedTo("foo", "meow"), of("foo")),
                param("Check substring",
                        of("foo", "bar", "baz"), request("Ba"), anyAllowed(), of("bar", "baz")),
                param("Check limit/offset",
                        of("foo", "bar", "baz"), request(2, 1), anyAllowed(), of("bar")),
                param("Check all at once",
                        of("foo", "bar", "bazaar", "mara"), request("aR", 2, 100), restrictedTo("MARA", "bar", "bazaar"), of("bazaar"))
        );
    }

    @Before
    public void setup() {
        EventNamesDao dao = mock(EventNamesDao.class);
        when(dao.events(anyInt())).thenReturn(allEvents);

        ApplicationsLoadService applicationsLoadService = mock(ApplicationsLoadService.class);
        Application app = new Application();
        if (!agencyRestriction.allowAll) {
            app.setPermission(ApplicationPermission.agency_view);
            app.setAllowedEventLabels(agencyRestriction.allowedEvents);
        }
        when(applicationsLoadService.getApplication(anyInt(), anyObject(), anyObject())).thenReturn(app);

        service = new EventService(dao, applicationsLoadService);
    }

    @Test
    public void testEvents() {
        List<String> actual = service.events(request, targetUser, currentUser).getEvents();
        assertThat(actual, equalTo(expected));
    }

    // region helpers

    private static EventsRequest request() {
        return new EventsRequest()
                .withAppId(42);
    }

    private static EventsRequest request(String mask) {
        return request()
                .withMask(mask);
    }

    private static EventsRequest request(int offset, int limit) {
        return request()
                .withOffsetLimit(offset, limit);
    }

    private static EventsRequest request(String mask, int offset, int limit) {
        return request(offset, limit)
                .withMask(mask);
    }

    private static Object[] param(String description, List<String> allEvents, EventsRequest request,
                                  EventsRestriction restriction, List<String> expected) {
        return new Object[]{description, allEvents, request, restriction, expected};
    }

    // endregion

}
