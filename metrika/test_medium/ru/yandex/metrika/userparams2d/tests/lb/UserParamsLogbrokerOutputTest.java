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
public class UserParamsLogbrokerOutputTest extends AbstractUserParamsLogbrokerTest {

    @Test
    @Title("Параметры только больших счетчиков пишутся в топик")
    public void gigaParamsTest() throws InterruptedException {
        List<Param> params = generationSteps.generateParamsWithBigCounter(1);

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveUpdatesAndCheckOnlyGigaTopicIsWritten(updates);
    }

    @Test
    @Title("Параметры только небольших счетчиков пишутся в топик")
    public void nanoParamsTest() throws InterruptedException {
        List<Param> params = generationSteps.generateParamsWithNanoCounter(1);

        var updates = singletonList(generationSteps.generateUpdateWithParams(params));

        testsSteps.saveUpdatesAndCheckNanoTopic(updates);
    }

    @Test
    @Title("Смешанные параметры пишутся в топик")
    public void differentParamsTest() throws InterruptedException {
        List<Param> gigaParams = generationSteps.generateParamsWithBigCounter(1);
        List<Param> nanoParams = generationSteps.generateParamsWithNanoCounter(1);

        var gigaUpdate = generationSteps.generateUpdateWithParams(gigaParams);
        var nanoUpdate = generationSteps.generateUpdateWithParams(nanoParams);

        var updates = List.of(gigaUpdate, nanoUpdate);

        testsSteps.saveUpdatesAndCheckTopics(updates);
    }

    @Test
    @Title("Измененные параметры пишутся в топики")
    public void modifiedParamsTest() throws InterruptedException {
        List<Param> gigaParams = generationSteps.generateParamsWithBigCounter(1);
        List<Param> nanoParams = generationSteps.generateParamsWithNanoCounter(1);

        var gigaInitState = generationSteps.generateUpdateWithParams(gigaParams);
        var nanoInitState = generationSteps.generateUpdateWithParams(nanoParams);

        var initState = List.of(gigaInitState, nanoInitState);

        testsSteps.saveInitState(initState);

        var updatedGigaParams = generationSteps.updateParamsDoubleValues(gigaParams);
        var updatedNanoParams = generationSteps.updateParamsStringValues(nanoParams);

        var gigaUpdate = generationSteps.generateUpdateWithParams(updatedGigaParams);
        var nanoUpdate = generationSteps.generateUpdateWithParams(updatedNanoParams);

        var updates = List.of(gigaUpdate, nanoUpdate);

        testsSteps.saveUpdatesAndCheckTopics(updates);
    }

    @Test
    @Title("Не измененный параметр не пишется в топик")
    public void unmodifiedParamTest() throws InterruptedException {
        Param param = generationSteps.generateStringParameter();

        Param copyParam = new Param(param);

        var initState = generationSteps.generateUpdateWithParams(singletonList(param));
        testsSteps.saveInitState(singletonList(initState));

        var update = generationSteps.generateUpdateWithParams(singletonList(copyParam));

        testsSteps.saveParamUpdatesAndCheckTopicsAreEmpty(singletonList(update));
    }
}
