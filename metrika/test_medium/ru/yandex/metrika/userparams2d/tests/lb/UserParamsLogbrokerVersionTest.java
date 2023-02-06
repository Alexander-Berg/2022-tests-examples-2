package ru.yandex.metrika.userparams2d.tests.lb;

import java.util.List;

import io.qameta.allure.Story;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams2d.config.UserParams2dTestConfig;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("Logbroker")
public class UserParamsLogbrokerVersionTest extends AbstractUserParamsLogbrokerTest {

    @Test
    @Title("Обновление версии параметра")
    public void correctlyUpdatesParamVersionInLB() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullStringParameter());

        var updatedParams = generationSteps.updateParamsStringValues(params);

        var init = singletonList(generationSteps.generateUpdateWithParams(params));
        var update = singletonList(generationSteps.generateUpdateWithParams(updatedParams));


        testsSteps.saveInitStateUpdateItAndCheckLBParamVersion(init, update);
    }
}
