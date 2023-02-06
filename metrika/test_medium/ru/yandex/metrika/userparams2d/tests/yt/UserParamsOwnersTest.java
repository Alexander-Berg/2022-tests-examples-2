package ru.yandex.metrika.userparams2d.tests.yt;

import java.util.List;

import io.qameta.allure.Story;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams2d.config.UserParams2dTestConfig;
import ru.yandex.metrika.userparams2d.tests.AbstractUserParamsTest;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("Owners")
public class UserParamsOwnersTest extends AbstractUserParamsTest {

    private Param firstParam;
    private Param secondParam;

    @Before
    public void before() {
        firstParam = generationSteps.generateStringParameter();
        secondParam = generationSteps.generateParamWithSameOwner(firstParam);
    }

    @Test
    @Title("Один владелец")
    public void userParamsOneOwnerTest() throws InterruptedException {
        List<UserParamUpdate> updates = singletonList(generationSteps.generateUpdateWithParams(List.of(firstParam)));

        testsSteps.saveParamUpdatesAndCheckOwners(updates);
    }

    @Test
    @Title("Количество параметров у владельца")
    public void userParamsParamQuantityTest() throws InterruptedException {
        var updates = singletonList(generationSteps.generateUpdateWithParams(List.of(firstParam, secondParam)));

        testsSteps.saveParamUpdatesAndCheckOwners(updates);
    }

    @Test
    @Title("Обновление количества параметров и ClientID владельца")
    public void userParamsOwnerUpdateTest() throws InterruptedException {
        var initState = singletonList(generationSteps.generateUpdateWithParams(List.of(firstParam)));
        var updates = singletonList(generationSteps.generateUpdateWithParams(List.of(secondParam)));

        testsSteps.saveInitStateUpdateItAndCheckUpdatedOwners(initState, updates);
    }
}
