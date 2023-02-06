package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_FOR_LABELS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabels;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sourx on 25.12.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка изменения порядка групп счетчиков")
public class SetLabelsOrderTest {

    private UserSteps user;
    private List<Long> labelIds;

    @Before
    public void setup() {
        user = new UserSteps().withUser(USER_FOR_LABELS);
        labelIds = user.onManagementSteps().onLabelsSteps().addLabels(getDefaultLabels(5));
        assumeThat("cодержатся только добавленные метки", user.onManagementSteps().onLabelsSteps().getLabels(),
                equalTo(labelIds));
    }

    @Test
    @Title("Порядок групп счетчиков изменяется верно")
    public void withChangeInOrder() {
        List<Long> newOrder = labelIds.stream().filter(id -> id % 2 == 0).collect(toList());
        List<Long> notOrdered = labelIds.stream().filter(id -> id % 2 != 0).collect(toList());

        user.onManagementSteps().onLabelsSteps().changeLabelsOrder(newOrder);
        newOrder.addAll(notOrdered);
        List<Long> actualOrder = user.onManagementSteps().onLabelsSteps().getLabels();
        assertThat("порядок групп счетчиков изменен верно", actualOrder, equalTo(newOrder));
    }

    @Test
    @Title("Порядок групп счетчиков не должен измениться")
    public void withoutChangeInOrder() {
        user.onManagementSteps().onLabelsSteps().changeLabelsOrder(labelIds);
        List<Long> actualOrder = user.onManagementSteps().onLabelsSteps().getLabels();
        assertThat("порядок групп счетчиков не изменился", actualOrder, equalTo(labelIds));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onLabelsSteps().deleteLabels(labelIds);
    }
}
