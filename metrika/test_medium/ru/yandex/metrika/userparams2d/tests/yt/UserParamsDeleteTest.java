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
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchParams;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
@Story("Parameters")
public class UserParamsDeleteTest extends AbstractUserParamsTest {

    @Test
    @Title("Удаление параметров")
    public void userParamsDeleteTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullDoubleParameter());

        var initState = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveInitState(initState);

        var update = singletonList(generationSteps.generateDeletingUpdateWithParams(params));

        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(update);

        var paramsFromYt = dataSteps.readDeletedParamsFromYt();

        assertThat("параметры отсутствуют", paramsFromYt, matchParams(params));
    }

    @Test
    @Title("Неизменность параметров параметров при удалении других параметров")
    public void userParamsUploadingsIgnoreDeleteTest() throws InterruptedException {
        Param param = generationSteps.generateFullDoubleParameter();

        Param paramToDelete = generationSteps.generateDoubleParameter();

        var initState = singletonList(generationSteps.generateUpdateWithParams(List.of(param, paramToDelete)));

        testsSteps.saveInitState(initState);

        var update = singletonList(generationSteps.generateDeletingUpdateWithParams(singletonList(paramToDelete)));

        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(update);

        var paramsFromYt = dataSteps.readParamsFromYt();

        assertThat("параметры остались неизменными", paramsFromYt, matchParams(List.of(param)));
    }
}
