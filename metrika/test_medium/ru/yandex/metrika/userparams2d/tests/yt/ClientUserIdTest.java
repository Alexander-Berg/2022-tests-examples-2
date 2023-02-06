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

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("ClientUserIds")
public class ClientUserIdTest extends AbstractUserParamsTest {

    private static final String CLIENT_USER_ID = "{{undefined:)}}";

    @Test
    @Title("Обновление через поле clientUserId с пустым параметром")
    public void updateViaFieldWithEmptyParamTest() throws InterruptedException {
        var param = generationSteps.generateStringParameter();
        var update = generationSteps.generateUpdateWithClientUserId(List.of(),
                param.getKey().getOwnerKey().getCounterId(),
                param.getKey().getOwnerKey().getUserId(),
                CLIENT_USER_ID);

        testsSteps.saveClientUserIdsAndCheckMatchingTables(List.of(update));
    }

    @Test
    @Title("Обновление через поле clientUserId с непустым параметром")
    public void updateViaFieldWithNonEmptyParamTest() throws InterruptedException {
        var param = generationSteps.generateStringParameter();
        var update = generationSteps.generateUpdateWithClientUserId(List.of(param),
                param.getKey().getOwnerKey().getCounterId(),
                param.getKey().getOwnerKey().getUserId(),
                CLIENT_USER_ID);

        testsSteps.saveClientUserIdsAndCheckMatchingTables(List.of(update));
    }

}
