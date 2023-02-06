package ru.yandex.autotests.metrika.tests.ft.management.subscriptions;

import java.util.List;

import org.hamcrest.Matchers;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка получения списка почтовых адресов")
public class GetEmailsTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);

    @Test
    public void checkEmailsSubscription() {
        List<String> emails = USER.onManagementSteps().onSubscriptionsSteps().getEmails();
        assertThat("Список почт получен", emails, Matchers.notNullValue());
    }

}
