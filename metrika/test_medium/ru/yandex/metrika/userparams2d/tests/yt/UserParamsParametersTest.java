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
public class UserParamsParametersTest extends AbstractUserParamsTest {

    @Test
    @Title("Строковый параметр")
    public void userParamsStringParameterTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateStringParameter());

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveParamUpdatesAndCheckParams(updates);
    }

    @Test
    @Title("Числовой параметр")
    public void userParamsDoubleParameterTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateDoubleParameter());

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveParamUpdatesAndCheckParams(updates);
    }

    @Test
    @Title("Максимальный строковый параметр")
    public void userParamsFullStringParameterTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullStringParameter());

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveParamUpdatesAndCheckParams(updates);
    }

    @Test
    @Title("Максимальный числовой параметр")
    public void userParamsFullDoubleParameterTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullDoubleParameter());

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveParamUpdatesAndCheckParams(updates);
    }

    @Test
    @Title("Строковый и числовой параметры")
    public void userParamsStringAndDoubleParameterTest() throws InterruptedException {
        List<Param> params = List.of(generationSteps.generateStringParameter(), generationSteps.generateDoubleParameter());

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveParamUpdatesAndCheckParams(updates);
    }
}
