package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos on 13.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка возможности получения информации о метки пользователями: владелец, менеджер, саппорт, представитель")
@RunWith(Parameterized.class)
public class LabelInfoPositiveTest {
    private static final User OWNER_ACCOUNT = USER_DELEGATOR;
    private static final User DELEGATE_ACCOUNT = USER_DELEGATE_PERMANENT;

    private static UserSteps userOwner = new UserSteps().withUser(OWNER_ACCOUNT);

    private UserSteps userWithPermission;
    private Label label;
    private long labelId;

    @Parameter(0)
    public String userRole;

    @Parameter(1)
    public User userAccount;

    @Parameters(name = "Роль: {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray("Владелец", OWNER_ACCOUNT),
                toArray("Менеджер", MANAGER),
                toArray("Саппорт", SUPPORT),
                toArray("Представитель", DELEGATE_ACCOUNT));
    }

    @Before
    public void setup() {
        userWithPermission = new UserSteps().withUser(userAccount);
        label = getDefaultLabel();
        labelId = userOwner.onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label).getId();
    }

    @Test
    public void shouldGetLabelInfo() {
        Label info = userWithPermission.onManagementSteps().onLabelsSteps().getLabelInfo(labelId);
        assertThat("информация метки должна быть такой же, что и при создании", label.getName(), equalTo(info.getName()));
    }

    @After
    public void teardDown() {
        userOwner.onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }
}
