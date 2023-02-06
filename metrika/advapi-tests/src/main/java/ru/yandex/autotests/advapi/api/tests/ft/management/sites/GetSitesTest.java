package ru.yandex.autotests.advapi.api.tests.ft.management.sites;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.parameters.SitesManagementParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(MANAGEMENT)
@Title("Получение площадок")
@RunWith(Parameterized.class)
public class GetSitesTest {

    @Parameterized.Parameter()
    public SitesManagementParameters parameters;

    @Parameterized.Parameter(1)
    public Matcher matcher;

    @Parameterized.Parameter(2)
    public String message;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        new SitesManagementParameters().withLimit(2),
                        iterableWithSize(2),
                        "лимит в 2 площадок"
                },
                {
                        new SitesManagementParameters().withOffset(1).withLimit(1),
                        contains(hasProperty("url", equalTo("display.yandex.ru"))),
                        "сдвиг на 1, лимит 1 (возвращается display.yandex.ru)"
                },
                {
                        new SitesManagementParameters().withFilter("Другое"),
                        allOf(iterableWithSize(1), contains(hasProperty("name", equalTo("Другое")))),
                        "фильтруем по 'Другое' (возвращается 1 площадка)"
                },
                {
                        new SitesManagementParameters(),
                        allOf(iterableWithSize(3), hasItem(hasProperty("name", equalTo("Другое")))),
                        "по умолчанию возвращаем 3 площадки и среди них присутствует опция 'Другое'"
                }
        });
    }

    @Test
    public void getPlacements() {
        assertThat(message, UserSteps.withUser(SUPER_USER).onSitesSteps().getSitesAndExpectSuccess(parameters).getSites(), matcher);
    }
}
