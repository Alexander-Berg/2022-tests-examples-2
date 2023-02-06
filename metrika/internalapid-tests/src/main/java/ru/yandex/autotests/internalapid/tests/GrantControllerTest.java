package ru.yandex.autotests.internalapid.tests;

import org.junit.Test;

import ru.yandex.autotests.internalapid.beans.schemes.GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;

@Title("Тесты контроллера для запроса доступов")
public class GrantControllerTest extends InternalApidTest{

    @Test
    @Title("Проверка поведения, если JSON содержит только неверные поля")
    public void getGrantAccessRequestStatusWithoutCountersList() {
        GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema result =
                userSteps.onGrantsSteps().tryGetGrantAccessRequestStatusWithoutCountersList(60893964L);

        assertThat("Не возвращает информации о доступах", result.getGrantRequestStatusList(), empty());
        assertThat("Код ответа 400", result.getCode(), is(400L));
        assertThat("Возвращает ошибку", result.getErrors(), hasSize(1));
    }
}
