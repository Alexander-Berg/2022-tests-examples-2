package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.model.ApplicationCategory;
import ru.yandex.qatools.allure.annotations.*;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;

@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.CATEGORIES
})
@Title("Получение списка категорий приложений")
@Issues({
        @Issue("MOBMET-8412")
})
@RunWith(Parameterized.class)
public class ApplicationCategoriesTest {

    private final UserSteps user = UserSteps.onTesting(Users.SIMPLE_USER);

    @Parameterized.Parameter
    public String lang;

    @Parameters(name = "Lang: {0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(
                new Object[]{"ru"},
                new Object[]{"en"});
    }

    @Test
    public void checkApplicationCategoriesList() {
        List<ApplicationCategory> categories = user.onApplicationSteps().getApplicationCategories(lang);
        assertThat("Список категорий приложений пуст", !categories.isEmpty());
    }
}
