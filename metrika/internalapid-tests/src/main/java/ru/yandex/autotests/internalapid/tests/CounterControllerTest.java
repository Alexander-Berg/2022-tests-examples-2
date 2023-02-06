package ru.yandex.autotests.internalapid.tests;

import org.junit.Test;
import ru.yandex.qatools.allure.annotations.Title;

@Title("Тест апи для проверки CountersController")
public class CounterControllerTest extends InternalApidTest {
    @Test
    public void testCountersForUnregisteredUidOwner() {
        // 60893964 - имеет доступ для счетчика 49126030 у которого владельца нет в Черном Ящике
        // если что переделать 273197151(at-metrika) имеет доступ к 67657737(аккаунт удален 25.09.2020)
        userSteps.onCountersSteps().getCountersForUidSuccess(60893964);
    }

}
