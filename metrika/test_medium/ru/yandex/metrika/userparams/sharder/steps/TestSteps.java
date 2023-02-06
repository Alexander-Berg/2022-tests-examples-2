package ru.yandex.metrika.userparams.sharder.steps;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.qatools.allure.annotations.Step;

import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.metrika.api.management.client.external.userparams.UserParamAction.UPDATE;

@Component
public class TestSteps {
    @Autowired
    private DataSteps dataSteps;

    @Step("Подать данные на вход демону и проверить выходной топик")
    public void writeParamsAndCheckOutput(List<ListParamWrapper> params) throws InterruptedException {
        dataSteps.writeUserParamsToInputAndWaitProcessing(params);

        var output = dataSteps.readUserparamsUpdatesFromOutputTopic();

        assertThat(output).containsExactlyInAnyOrderElementsOf(expectedOutputWithInput(params));
    }


    private List<UserParamUpdate> expectedOutputWithInput(List<ListParamWrapper> params) {
        return params.stream().map(paramWrapper -> new UserParamUpdate(paramWrapper, UPDATE)).collect(Collectors.toList());
    }
}
