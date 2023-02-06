package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash.crashgroup;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.ReportGroupPlural;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashGroup;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashGroupStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.PUSH_SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.parameters.crash.ReportGroupPlural.*;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.CrashGroup.COMMENT,
        Requirements.Story.Crash.CrashGroup.STATUS
})
@Title("Управление группой крэшей")
@RunWith(Parameterized.class)
public class CrashGroupManagementTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SUPER_LIMITED);

    private final long appId = PUSH_SAMPLE.get(ID);

    @Parameterized.Parameter
    public ReportGroupPlural report;

    @Parameterized.Parameter(1)
    public String crashGroupId;

    @Parameterized.Parameters(name = "Report: {0}")
    public static Collection<Object[]> createParameters() {
        // Тесты проверяют изменение крэш-группы на тестинге YDB, поэтому работаем с Push Sample
        return ImmutableList.of(
                params(crashes, "16614724676811231540")
                /*,
                TODO пока что ждём группы ошибок и ANR в Push Sample
                params(errors),
                params(anrs)
                 */
        );
    }

    @Test
    public void checkAddComment() {
        String comment = TestData.getTestCrashComment();
        userSteps.onCrashGroupManagementSteps().setCrashGroupComment(report, appId, crashGroupId, comment);

        CrashGroup crashGroup = userSteps.onCrashGroupManagementSteps().getCrashGroup(report, appId, crashGroupId);
        assertThat("Комментарий группы крэшей соответствует ожидаемому", crashGroup.getComment(), equalTo(comment));
    }

    @Test
    public void checkDeleteComment() {
        String comment = TestData.getTestCrashComment();
        userSteps.onCrashGroupManagementSteps().setCrashGroupComment(report, appId, crashGroupId, comment);
        userSteps.onCrashGroupManagementSteps().deleteCrashGroupComment(report, appId, crashGroupId);

        CrashGroup crashGroup = userSteps.onCrashGroupManagementSteps().getCrashGroup(report, appId, crashGroupId);
        assertThat("Комментарий группы крэшей удалён", crashGroup.getComment(), nullValue());
    }

    @Test
    public void checkSetStatus() {
        CrashGroupStatus status = CrashGroupStatus.CLOSED;
        userSteps.onCrashGroupManagementSteps().setCrashGroupStatus(report, appId, crashGroupId, status);

        CrashGroup crashGroup = userSteps.onCrashGroupManagementSteps().getCrashGroup(report, appId, crashGroupId);
        assertThat("Статус группы крэшей соответствует ожидаемому", crashGroup.getStatus(), equalTo(status));
    }

    private static Object[] params(Object... params) {
        return params;
    }

}
