package ru.yandex.metrika.userparams2d.tests.lb;

import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams2d.config.UserParams2dTestConfig;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchLbRowsDelete;


@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = UserParams2dTestConfig.class)
public class UserParamLogbrokerDeleteTest extends AbstractUserParamsLogbrokerTest {

    @Test
    @Title("Удаление параметров")
    public void userParamsDeleteTest() throws InterruptedException {
        List<Param> params = singletonList(generationSteps.generateFullDoubleParameter());

        var initState = singletonList(generationSteps.generateUpdateWithParams(params));
        testsSteps.saveInitState(initState);

        var update = singletonList(generationSteps.generateDeletingUpdateWithParams(params));
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(update);

        var paramsFromLB = dataSteps.readDataFromOutputGigaTopic();
        assertThat("не изменившиеся параметры отсутствуют", paramsFromLB, matchLbRowsDelete(update));
    }

    @Test
    @Title("Удаление не затрагивает другие параметры")
    public void userParamsUploadingsIgnoreDeleteTest() throws InterruptedException {
        Param param = generationSteps.generateFullDoubleParameter();
        Param paramToDelete = generationSteps.generateDoubleParameter();

        var initState = singletonList(generationSteps.generateUpdateWithParams(List.of(param, paramToDelete)));
        testsSteps.saveInitState(initState);

        var update = singletonList(generationSteps.generateDeletingUpdateWithParams(singletonList(paramToDelete)));
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(update);

        var paramsFromLB = dataSteps.readDataFromOutputGigaTopic();

        assertThat("параметры остались неизменными", paramsFromLB, matchLbRowsDelete(update));
    }
}
