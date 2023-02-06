package ru.yandex.metrika.mobile.push.api.tests;

import java.util.List;

import io.qameta.allure.Story;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.api.model.PushGroupAdapter;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultApplication;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultPushGroup;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.defaultUserId;
import static ru.yandex.metrika.mobile.push.api.steps.TestData.updatedPushGroup;
import static ru.yandex.metrika.mobile.push.api.tests.Matchers.matchGroup;

@Story("Groups")
public class PushApiGroupsTest extends PushApiBaseTest {

    private Application application;

    private PushGroupAdapter expectedGroup;

    @Before
    public void before() throws Exception {
        application = steps.onApplications().add(defaultUserId(), defaultApplication());

        expectedGroup = defaultPushGroup(application.getId());

        group = steps.onGroups().add(mockMvc, expectedGroup);
    }

    @Test
    @Title("Добавление группы")
    public void pushApiAddGroupTest() {
        assertThat("добавленная группа эквивалентна ожидаемой", group, matchGroup(expectedGroup));
    }

    @Test
    @Title("Получение группы")
    public void pushApiGetGroupTest() throws Exception {
        PushGroupAdapter actualGroup = steps.onGroups().recieve(mockMvc, group.getId());

        assertThat("полученная группа эквивалентна ожидаемой", actualGroup, matchGroup(expectedGroup));
    }

    @Test
    @Title("Получение списка групп")
    public void pushApiListGroupsTest() throws Exception {
        List<PushGroupAdapter> actualGroups = steps.onGroups().list(mockMvc, application.getId());

        assertThat("список групп содержит группу, эквивалентную ожидаемой",
                actualGroups, hasItem(matchGroup(expectedGroup)));
    }

    @Test
    @Title("Обновление группы")
    public void pushApiUpdateGroupTest() throws Exception {
        expectedGroup = updatedPushGroup(group.getId(), expectedGroup);

        PushGroupAdapter actualGroup = steps.onGroups().update(mockMvc, expectedGroup);

        assertThat("обновленная группа эквивалентна ожидаемой", actualGroup, matchGroup(expectedGroup));
    }

}
