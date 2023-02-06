package ru.yandex.metrika.api.management.tests.medium.client;

import java.time.Instant;
import java.util.Date;
import java.util.List;
import java.util.stream.Stream;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.counter.CountersService;
import ru.yandex.metrika.api.management.client.counter.stat.CounterStatDaoYDB;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.metrika.api.management.config.CountersServiceConfig;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.rbac.Rbac;
import ru.yandex.metrika.rbac.metrika.CountersRbac;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class GuestsCountersServiceTest {

    @Autowired
    private CountersService countersService;

    @Autowired
    private Rbac rbac;

    @Autowired
    private CountersRbac countersRbac;

    @Autowired
    private CounterStatDaoYDB counterStatDaoYDB;

    @Autowired
    private AuthUtils authUtils;

    private static long id = 1L;


    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void createTable() {
        String table = counterStatDaoYDB.createNewTable();
        counterStatDaoYDB.updateCurrentTable(table);
    }

    @Test
    public void containsCountersOwner() {
        long owner = id++;
        var counter = createSomeCounter(owner);
        var guests = countersService.getAllCounterGuests(counter.getId());
        assertEquals(1, guests.size());
        assertEquals(authUtils.getLoginByUid(owner), guests.get(0).login());
    }

    @Test
    public void containsDelegateWriteUser() {
        long owner = id++;
        long delegate = id++;
        var counter = createSomeCounter(owner);
        giveDelegateWriteGrantsToUser(owner, delegate);
        var guests = countersService.getAllCounterGuests(counter.getId());
        assertEquals(
                Stream.of(owner, delegate).map(authUtils::getLoginByUid).toList(),
                guests.stream().map(CountersRbac.CounterGrantInfo::login).toList()
        );
    }

    @Test
    public void containsDelegateReadUser() {
        long owner = id++;
        long delegate = id++;
        var counter = createSomeCounter(owner);
        giveDelegateReadGrantsToUser(owner, delegate);
        var guests = countersService.getAllCounterGuests(counter.getId());
        assertEquals(
                Stream.of(owner, delegate).map(authUtils::getLoginByUid).toList(),
                guests.stream().map(CountersRbac.CounterGrantInfo::login).toList()
        );
    }

    @Test
    public void containsReadGuests() {
        long owner = id++;
        long delegate = id++;
        var counter = createSomeCounter(owner);
        giveUserReadGuestGrants(owner, counter.getId(), delegate);
        var guests = countersService.getAllCounterGuests(counter.getId());
        assertEquals(
                guests.stream().map(CountersRbac.CounterGrantInfo::login).toList(),
                Stream.of(owner, delegate).map(authUtils::getLoginByUid).toList()
        );
    }

    @Test
    public void containsWriteGuests() {
        long owner = id++;
        long delegate = id++;
        var counter = createSomeCounter(owner);
        giveUserWriteGuestGrants(owner, counter.getId(), delegate);
        var guests = countersService.getAllCounterGuests(counter.getId());
        assertEquals(
                guests.stream().map(CountersRbac.CounterGrantInfo::login).toList(),
                Stream.of(owner, delegate).map(authUtils::getLoginByUid).toList()
        );
    }

    @Test
    public void containsGuestsDelegate() {
        long owner = id++;
        long guest = id++;
        long delegate = id++;
        var counter = createSomeCounter(owner);
        giveUserWriteGuestGrants(owner, counter.getId(), guest);
        giveDelegateWriteGrantsToUser(guest, delegate);
        var guests = countersService.getAllCounterGuests(counter.getId());
        assertEquals(
                Stream.of(owner, guest, delegate).map(authUtils::getLoginByUid).toList(),
                guests.stream().map(CountersRbac.CounterGrantInfo::login).toList()
                );
    }

    @Test
    public void containsOwnCounter() {
        long owner = id++;
        var counter = createSomeCounter(owner);
        var guestCounters = countersService.getAllUserGuestCounters(owner);
        System.out.println(guestCounters);
        assertTrue(guestCounters.stream().anyMatch(it -> it.counterId() == counter.getId()));
    }

    @Test
    public void containsGuestCounter() {
        long owner = id++;
        long guest = id++;
        var counter = createSomeCounter(owner);
        giveUserReadGuestGrants(owner, counter.getId(), guest);
        var guestCounters = countersService.getAllUserGuestCounters(guest);
        assertTrue(guestCounters.stream().anyMatch(it -> it.counterId() == counter.getId()));
    }

    @Test
    public void containsDelegateCounter() {
        long owner = id++;
        long delegate = id++;
        var counter = createSomeCounter(owner);
        giveDelegateWriteGrantsToUser(owner, delegate);
        var guestCounters = countersService.getAllUserGuestCounters(delegate);
        assertTrue(guestCounters.stream().anyMatch(it -> it.counterId() == counter.getId()));
    }

    @Test
    public void containsDelegatesGuestCounter() {
        long owner = id++;
        long delegate = id++;
        long guest = id++;
        var counter = createSomeCounter(owner);
        giveUserReadGuestGrants(owner, counter.getId(), guest);
        giveDelegateReadGrantsToUser(guest, delegate);
        var guestCounters = countersService.getAllUserGuestCounters(delegate);
        assertTrue(guestCounters.stream().anyMatch(it -> it.counterId() == counter.getId()));
    }

    private CounterFull createSomeCounter(long ownerUid) {
        var counter = new CounterFull();
        counter.setSite2(new CounterMirrorE("example.com"));
        var owner = AuthUtils.buildSimpleUserDetails(ownerUid, "localhost");
        return countersService.save(owner, owner, counter, List.of(), false);
    }

    private void giveDelegateWriteGrantsToUser(long ownerUid, long delegateUid) {
        rbac.userDelegateUserForWrite(ownerUid, ownerUid, delegateUid, 0, Date.from(Instant.now()), "");
    }

    private void giveDelegateReadGrantsToUser(long ownerUid, long delegateUid) {
        rbac.userDelegateUserForRead(ownerUid, ownerUid, delegateUid, 0, Date.from(Instant.now()), "");
    }

    private void giveUserReadGuestGrants(long ownerUid, int counterId, long targetUid) {
        countersRbac.allowUserViewObject(ownerUid, counterId, targetUid, 0, Date.from(Instant.now()), "");
    }

    private void giveUserWriteGuestGrants(long ownerUid, int counterId, long targetUid) {
        countersRbac.allowUserEditObject(ownerUid, counterId, targetUid, 0, Date.from(Instant.now()), "");
    }

    @Configuration
    @Import({CountersServiceConfig.class})
    public static class Config {}
}

