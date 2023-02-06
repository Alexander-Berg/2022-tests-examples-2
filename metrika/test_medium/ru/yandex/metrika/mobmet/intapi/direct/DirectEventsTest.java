package ru.yandex.metrika.mobmet.intapi.direct;

import java.time.LocalDateTime;
import java.util.List;

import org.assertj.core.api.Assertions;
import org.junit.Before;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.intapi.common.AbstractMobmetIntapiTest;
import ru.yandex.metrika.mobmet.intapi.common.TestData;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectAppIdRequest;
import ru.yandex.metrika.mobmet.intapi.direct.model.DirectClientEventsRequest;
import ru.yandex.metrika.mobmet.intapi.direct.model.TypedEvent;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationsManageService;
import ru.yandex.metrika.mobmet.model.events.EventsResponse;
import ru.yandex.metrika.mobmet.scheduler.tasks.clientevents.ClientEvent;
import ru.yandex.metrika.mobmet.scheduler.tasks.clientevents.EventNamesCacheDao;

public class DirectEventsTest extends AbstractMobmetIntapiTest {

    @Autowired
    private ApplicationsManageService applicationsManageService;
    @Autowired
    private AuthUtils authUtils;
    @Autowired
    private DirectService directService;
    @Autowired
    private EventNamesCacheDao eventNamesCacheDao;

    private MetrikaUserDetails user;
    private Application addedApp;

    @Before
    public void before() {
        user = authUtils.getUserByUid(TestData.randomUid());
        addedApp = applicationsManageService.createApplication(TestData.defaultApp(), user, user);
    }

    @Test
    public void empty() {
        DirectClientEventsRequest request = new DirectClientEventsRequest();
        request.setAppId(addedApp.getId());
        request.setUid(user.getUid());
        EventsResponse actual = directService.getClientEvents(request);

        Assertions.assertThat(actual).isEqualTo(new EventsResponse(List.of(), 0L));
    }

    @Test
    public void withMysqlCache() {
        LocalDateTime now = LocalDateTime.now();
        List<ClientEvent> cachedEvents = List.of(new ClientEvent(addedApp.getId(), "test", now));
        eventNamesCacheDao.storeCache(cachedEvents);
        eventNamesCacheDao.updateLastCachedDate(now.toLocalDate());

        DirectClientEventsRequest request = new DirectClientEventsRequest();
        request.setAppId(addedApp.getId());
        request.setUid(user.getUid());

        EventsResponse actual = directService.getClientEvents(request);

        Assertions.assertThat(actual).isEqualTo(new EventsResponse(List.of("test"), 1L));
    }

    @Test
    public void typedEvents() {
        DirectAppIdRequest request = new DirectAppIdRequest();
        request.setAppId(addedApp.getId());
        request.setUid(user.getUid());
        List<TypedEvent> actual = directService.getTypedEvents(request);

        Assertions.assertThat(actual)
                .hasSize(6)
                .contains(new TypedEvent("EVENT_ECOMMERCE", "REMOVE_FROM_CART"));
    }
}
