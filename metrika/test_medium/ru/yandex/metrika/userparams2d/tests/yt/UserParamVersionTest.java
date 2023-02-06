package ru.yandex.metrika.userparams2d.tests.yt;

import java.util.List;

import io.qameta.allure.Story;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams2d.config.UserParams2dTestConfig;
import ru.yandex.metrika.userparams2d.tests.AbstractUserParamsTest;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("Parameters")
public class UserParamVersionTest extends AbstractUserParamsTest {

    @Test
    @Title("Обновление версии параметра")
    public void correctlyUpdatesParamVersionInYT() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullStringParameter());

        var updatedParams = generationSteps.updateParamsStringValues(params);

        var init = singletonList(generationSteps.generateUpdateWithParams(params));
        var update = singletonList(generationSteps.generateUpdateWithParams(updatedParams));

        testsSteps.saveInitStateUpdateItAndCheckParamVersion(init, update);
    }
}
