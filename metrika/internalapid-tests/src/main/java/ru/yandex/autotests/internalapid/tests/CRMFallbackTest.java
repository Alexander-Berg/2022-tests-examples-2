package ru.yandex.autotests.internalapid.tests;

import java.util.List;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.steps.UserSteps;
import ru.yandex.metrika.api.management.client.counter.CounterIdEnhanced;
import ru.yandex.metrika.internalapid.idm.crm.Reason;
import ru.yandex.qatools.allure.annotations.Title;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static ru.yandex.autotests.internalapid.beans.data.Users.PINCODE_DELEGATE_USER;
import static ru.yandex.autotests.internalapid.beans.data.Users.PINCODE_DELEGATE_USER2;

@Title("Тесты ручек для fallback-режима при отказе IDM")
public class CRMFallbackTest {

    private final String LOGIN = "robot-metrika-test";
    private final UserSteps userSteps = new UserSteps();
    private final int counterId = 24226447;

    @Test
    @Title("Тест ручки /crm/fallback/enable")
    public void testEnable() {
        userSteps.onIdmSteps().addRole(LOGIN, "crm_support_base", PINCODE_DELEGATE_USER.get(User.LOGIN));
        userSteps.onCRMFallbackSteps().enableFallback(LOGIN, Reason.MANUAL, "er ee", null);
        assertTrue("Fallback-режим включен", userSteps.onCRMFallbackSteps().getStatus().getEnabled());
    }


    @Test
    @Title("Тест ручки /crm/fallback/disable")
    public void testDisable() {
        userSteps.onIdmSteps().addRole(LOGIN, "crm_support_base", PINCODE_DELEGATE_USER.get(User.LOGIN));
        userSteps.onCRMFallbackSteps().enableFallback(LOGIN, Reason.MANUAL, "ук уу", null);
        userSteps.onCRMFallbackSteps().disableFallback(LOGIN, Reason.MANUAL, "ук уу", null);
        assertFalse("Fallback-режим выключен", userSteps.onCRMFallbackSteps().getStatus().getEnabled());
    }

    @Test
    @Title("Тест выдачи базовой пинкодной роли во время режима fallback")
    public void testRoleAdding() {
        userSteps.onCRMFallbackSteps().enableFallback(LOGIN, Reason.MANUAL, "some reason", null);

        Assert.assertFalse("Проверяем что отсутствует доступ до счетчика", containsCounterWithId(
                userSteps.onCountersSteps().getCounterDescription(counterId, PINCODE_DELEGATE_USER2.get(User.UID)),
                counterId
        ));

        userSteps.onIdmSteps().addRole(LOGIN, "crm_support_base", PINCODE_DELEGATE_USER2.get(User.LOGIN));

        Assert.assertTrue("Проверяем что доступ до счетчика появился", containsCounterWithId(
                userSteps.onCountersSteps().getCounterDescription(counterId, PINCODE_DELEGATE_USER2.get(User.UID)),
                counterId
        ));

        userSteps.onIdmSteps().removeRole(LOGIN, "crm_support_base", PINCODE_DELEGATE_USER2.get(User.LOGIN));
        userSteps.onCRMFallbackSteps().disableFallback(LOGIN, Reason.MANUAL, "another reason", null);
    }

    @Before
    @After
    public void init() {
        userSteps.onCRMFallbackSteps().disableFallback(LOGIN, Reason.AUTO, "init", null);
        userSteps.onIdmSteps().removeRole(LOGIN, "crm_support_base", PINCODE_DELEGATE_USER.get(User.LOGIN));
    }

    private boolean containsCounterWithId(List<CounterIdEnhanced> counters, int counterId) {
        return counters.stream().map(CounterIdEnhanced::getCounterId).anyMatch(id -> id == counterId);
    }
}
