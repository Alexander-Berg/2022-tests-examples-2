package ru.yandex.autotests.metrika.tests.ft.management.direct;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.CLIENT_IDS;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;

/**
 * Created by vananos on 15.08.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка получения списка ID клиентов директа")
@RunWith(Parameterized.class)
public class DirectClientsTest {

    private UserSteps user = new UserSteps();

    @Parameterized.Parameter
    public Counter counter;

    @Parameterized.Parameter(1)
    public User directUser;

    @Parameterized.Parameters(name = "Счетчик: {0} пользователь:{1}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray(YANDEX_MARKET, DIRECT_COMPANY_OWNER),
                toArray(YANDEX_MARKET, DIRECT_CLIENT_DELEGATEE),
                toArray(HOLODILNIKRU, DIRECT_CLIENT_MANAGER),
                toArray(ALI_EXPRESS, DIRECT_AGENCY_DELEGATEE),
                toArray(SHATURA_COM, DIRECT_CLIENT_AGENCY),
                toArray(GENVIC_RU, DIRECT_AGENCY_MANAGER)
        );
    }

    @Test
    public void directClientsShouldBeInList() {
        List<Long> clientsIds = user.onManagementSteps().onClientSteps()
                .getClientIds(new ClientsParameters().withCounters(counter.get(ID)), ulogin(directUser.get(LOGIN)));

        assertThat("список должен содержать ожидаемые id клиентов", clientsIds,
                hasItems(isIn(counter.get(CLIENT_IDS))));
    }
}
