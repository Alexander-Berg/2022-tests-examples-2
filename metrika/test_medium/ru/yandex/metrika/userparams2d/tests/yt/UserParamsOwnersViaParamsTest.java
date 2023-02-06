package ru.yandex.metrika.userparams2d.tests.yt;

import java.util.List;

import io.qameta.allure.Story;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.userparams2d.config.UserParams2dTestConfig;
import ru.yandex.metrika.userparams2d.tests.AbstractUserParamsTest;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.userparams2d.tests.Matchers.haveClientUserIdFromParams;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("Owners")
public class UserParamsOwnersViaParamsTest extends AbstractUserParamsTest {

    @Test
    @Title("Заполнение владельца через параметр")
    public void userParamsOwnersViaParamsTest() throws InterruptedException {
        var param = generationSteps.generateUserIdParameter();

        var updates = singletonList(generationSteps.generateUpdateWithParams(List.of(param)));

        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(updates);

        var owners = dataSteps.readParamOwnersFromYt();

        assertThat("ClientUserID владельца соответствует данным в параметрах", owners, haveClientUserIdFromParams(param));
    }
}
