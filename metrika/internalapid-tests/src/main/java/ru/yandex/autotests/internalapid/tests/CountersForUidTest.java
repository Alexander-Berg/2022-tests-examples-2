package ru.yandex.autotests.internalapid.tests;


import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.hamcrest.MatcherAssert;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.management.client.counter.CounterIdEnhanced;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.qatools.allure.annotations.Title;


@Title("Тест ручки /counters_for_uid")
public class CountersForUidTest extends InternalApidTest {

    private static final String SITE = "counters.for.uid.test.ru";
    private static final String userDelegateLogin = Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN);
    private static final Long DELEGATE_UID = Users.METRIKA_INTAPI_DELEGATE.get(User.UID);
    private static final Long USER_UID = Users.METRIKA_INTAPI_AUTO.get(User.UID);

    private static CounterFull viewCounter;
    private static CounterFull editCounter;
    private static CounterFull ownCounter;

    private static Map<Long, CounterIdEnhanced> countersMap;
    private static Map<Long, CounterIdEnhanced> countersOwnMap;

    @BeforeClass
    public static void init() {
        viewCounter = userSteps.onInternalApidSteps().createCounter(new CounterFull()
                .withName(DataUtil.getRandomCounterName())
                .withSite(SITE));

        editCounter = userSteps.onInternalApidSteps().createCounter(new CounterFull()
                .withName(DataUtil.getRandomCounterName())
                .withSite(SITE));

        ownCounter = userSteps.onInternalApidSteps().createCounter(new CounterFull()
                .withName(DataUtil.getRandomCounterName())
                .withSite(SITE));


        userSteps.onInternalApidSteps().addGrant(viewCounter.getId(),
                new GrantE().withUserLogin(userDelegateLogin).withPerm(GrantType.VIEW));

        userSteps.onInternalApidSteps().addGrant(editCounter.getId(),
                new GrantE().withUserLogin(userDelegateLogin).withPerm(GrantType.EDIT));

    }

    @Before
    public void getCounters() {
        List<CounterIdEnhanced> countersList = userSteps.onCountersSteps().getCountersForUid(DELEGATE_UID);
        List<CounterIdEnhanced> countersOwnList = userSteps.onCountersSteps().getCountersForUid(USER_UID);

        countersMap = countersList.stream()
                .collect(Collectors.toMap(CounterIdEnhanced::getCounterId, counter -> counter));

        countersOwnMap = countersOwnList.stream()
                .collect(Collectors.toMap(CounterIdEnhanced::getCounterId, counter -> counter));
    }


    @Test
    public void testCounterEditPermission() {
        MatcherAssert.assertThat("Есть счетчик с доступом на редактирование", existsWithPermission(countersMap,
                editCounter.getId(), Permission.EDIT));
    }

    @Test
    public void testCounterViewPermission() {
        MatcherAssert.assertThat("Есть счетчик с доступом на просмотр", existsWithPermission(countersMap,
                viewCounter.getId(), Permission.VIEW));
    }

    @Test
    public void testCounterOwnPermission() {
        MatcherAssert.assertThat("Есть счетчик с доступом на владение", existsWithPermission(countersOwnMap,
                ownCounter.getId(), Permission.EDIT));
    }

    private boolean existsWithPermission(Map<Long, CounterIdEnhanced> counters, Long counterId,
                                         Permission permission) {
        if (!counters.containsKey(counterId)) {
            return false;
        }
        return counters.get(counterId).getPermission().equals(permission) && !counters.get(counterId).getFavorite();
    }

    @AfterClass
    public static void cleanup() {
        userSteps.onInternalApidSteps().deleteCounter(editCounter.getId());
        userSteps.onInternalApidSteps().deleteCounter(viewCounter.getId());
        userSteps.onInternalApidSteps().deleteCounter(ownCounter.getId());
    }
}
