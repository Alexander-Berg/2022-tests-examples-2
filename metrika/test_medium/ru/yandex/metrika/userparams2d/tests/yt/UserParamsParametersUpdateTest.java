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
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchUpdatesParams;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("Parameters")
public class UserParamsParametersUpdateTest extends AbstractUserParamsTest {

    @Test
    @Title("Обновление строкового параметра")
    public void userParamsStringParameterUpdateTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullStringParameter());

        var updatedParams = generationSteps.updateParamsStringValues(params);

        var init = singletonList(generationSteps.generateUpdateWithParams(params));
        var update = singletonList(generationSteps.generateUpdateWithParams(updatedParams));

        testsSteps.saveInitStateUpdateItAndCheckUpdatedParams(init, update);
    }

    @Test
    @Title("Обновление числового параметра")
    public void userParamsDoubleParameterUpdateTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateDoubleParameter());

        var updatedParams = generationSteps.updateParamsDoubleValues(params);

        var init = singletonList(generationSteps.generateUpdateWithParams(params));
        var update = singletonList(generationSteps.generateUpdateWithParams(updatedParams));

        testsSteps.saveInitStateUpdateItAndCheckUpdatedParams(init, update);
    }

    @Test
    @Title("Параметр остается неизменным")
    public void userParamsUnmodifiedParameterTest() throws InterruptedException {
        Param param = generationSteps.generateDoubleParameter();
        Param copyParam = new Param(param);

        var init = singletonList(generationSteps.generateUpdateWithParams(singletonList(param)));
        var update = singletonList(generationSteps.generateUpdateWithParams(singletonList(copyParam)));

        testsSteps.saveInitState(init);

        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(update);

        var paramsFromYt = dataSteps.readParamsFromYt();

        assertThat("Параметры не изменились", paramsFromYt, matchUpdatesParams(init));
    }
}
