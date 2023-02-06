package ru.yandex.metrika.userparams2d.steps;


import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamKey;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.UserParamLBCHRow;
import ru.yandex.metrika.util.collections.Lists2;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchLbRowsUpdate;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchNanoLbRowsUpdate;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchUpdatesClientUserId;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchUpdatesOwners;
import static ru.yandex.metrika.userparams2d.tests.Matchers.matchUpdatesParams;

@Component
public class TestsSteps {

    @Autowired
    private DataSteps dataSteps;

    @Step("Подать апдейты на вход демона и проверить владельцев")
    public void saveParamUpdatesAndCheckOwners(List<UserParamUpdate> paramUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(paramUpdates);

        var owners = dataSteps.readParamOwnersFromYt();

        assertThat("Владельцы соответствуют поданным на вход данным", owners, matchUpdatesOwners(paramUpdates));
    }

    @Step("Подать апдейты на вход демона и проверить параметры")
    public void saveParamUpdatesAndCheckParams(List<UserParamUpdate> paramUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(paramUpdates);

        var params = dataSteps.readParamsFromYt();

        assertThat("Параметры соответствуют поданным на вход данным", params, matchUpdatesParams(paramUpdates));
    }

    @Step("Подать апдейты на вход демона и проверить что выходные топики пустые")
    public void saveParamUpdatesAndCheckTopicsAreEmpty(List<UserParamUpdate> paramUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(paramUpdates);


        List<UserParamLBCHRow> gigaContent = dataSteps.readDataFromOutputGigaTopic();
        List<UserParamLBCHRow> nanoContent = dataSteps.readDataFromOutputNanoTopic();

        assertThat("Giga топик пуст", gigaContent, empty());
        assertThat("Nano топик пуст", nanoContent, empty());
    }

    @Step("Подать апдейты на вход демона и проверить выходные топики")
    public void saveUpdatesAndCheckTopics(List<UserParamUpdate> paramUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(paramUpdates);

        List<UserParamLBCHRow> gigaContent = dataSteps.readDataFromOutputGigaTopic();
        List<UserParamLBCHRow> nanoContent = dataSteps.readDataFromOutputNanoTopic();

        assertThat("Данные в гига топике соответствуют хитам", gigaContent, matchLbRowsUpdate(paramUpdates));
        assertThat("Данные в нано топике соответствуют хитам", nanoContent, matchNanoLbRowsUpdate(paramUpdates));
    }

    @Step("Подать хиты на вход демона и проверить что пишем только в giga топик")
    public void saveUpdatesAndCheckOnlyGigaTopicIsWritten(List<UserParamUpdate> paramUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(paramUpdates);

        List<UserParamLBCHRow> gigaContent = dataSteps.readDataFromOutputGigaTopic();
        List<UserParamLBCHRow> nanoContent = dataSteps.readDataFromOutputNanoTopic();

        assertThat("Параметры в giga топике соответствуют данным в хитах", gigaContent, matchLbRowsUpdate(paramUpdates));
        assertThat("Nano топик пуст", nanoContent, empty());
    }

    @Step("Подать хиты на вход демона и проверить что корректно пишем в nano топик")
    public void saveUpdatesAndCheckNanoTopic(List<UserParamUpdate> paramUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(paramUpdates);

        List<UserParamLBCHRow> nanoContent = dataSteps.readDataFromOutputNanoTopic();

        assertThat("Данные в нано топике соответствуют хитам", nanoContent, matchNanoLbRowsUpdate(paramUpdates));
    }

    @Step("Подготовить начальное состояние")
    public List<UserParamLBCHRow> saveInitState(List<UserParamUpdate> initParamUpdates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(initParamUpdates);

        dataSteps.clearOutputNanoTopic();
        return dataSteps.readDataFromOutputGigaTopic();
    }

    @Step("Подготовить начальное состояние и проверить обновление овнеров")
    public void saveInitStateUpdateItAndCheckUpdatedOwners(List<UserParamUpdate> initState, List<UserParamUpdate> updates) throws InterruptedException {
        saveInitState(initState);

        dataSteps.writeParamUpdatesFromApiToInputTopicAndWaitProcessing(updates);

        var owners = dataSteps.readParamOwnersFromYt();

        assertThat("Владельцы соответствуют поданным на вход данным", owners, matchUpdatesOwners(Lists2.concat(initState, updates)));
    }

    @Step("Подготовить начальное состояние и проверить обновление параметров")
    public void saveInitStateUpdateItAndCheckUpdatedParams(List<UserParamUpdate> initState, List<UserParamUpdate> updates) throws InterruptedException {
        saveInitState(initState);

        dataSteps.writeParamUpdatesFromApiToInputTopicAndWaitProcessing(updates);

        var params = dataSteps.readParamsFromYt();

        assertThat("Параметры соответствуют поданным на вход данным", params, matchUpdatesParams(updates));
    }

    @Step("Подготовить начальное состояние и проверить обновление версии параметров")
    public void saveInitStateUpdateItAndCheckParamVersion(List<UserParamUpdate> initState, List<UserParamUpdate> updates) throws InterruptedException {
        saveInitState(initState);

        var initParams = dataSteps.readParamsFromYt();

        dataSteps.writeParamUpdatesFromApiToInputTopicAndWaitProcessing(updates);

        var updatedParams = dataSteps.readParamsFromYt();

        assertThat("Версии параметров обновлены корректно", isEveryParamVersionUpdatedCorrectly(initParams, updatedParams), equalTo(true));
    }

    @Step("Подготовить начальное состояние и проверить обновление версии параметров")
    public void saveInitStateUpdateItAndCheckLBParamVersion(List<UserParamUpdate> initState, List<UserParamUpdate> updates) throws InterruptedException {
        var initParams = saveInitState(initState);

        dataSteps.writeParamUpdatesFromApiToInputTopicAndWaitProcessing(updates);

        var updatedParams = dataSteps.readDataFromOutputGigaTopic();

        assertThat("Версии параметров обновлены корректно", isEveryLbParamVersionUpdatedCorrectly(initParams, updatedParams), equalTo(true));
    }

    @Step("Записать апдейты clientUserId и проверить табличку с метчингом")
    public void saveClientUserIdsAndCheckMatchingTables(List<UserParamUpdate> updates) throws InterruptedException {
        dataSteps.writeParamUpdatesToInputTopicAndWaitProcessing(updates);

        var writtenClientUserIds = dataSteps.readClientUserIdMatchingFromYt();

        assertThat("ClientUserId записаны корректно", writtenClientUserIds, matchUpdatesClientUserId(updates));
    }

    private boolean isEveryParamVersionUpdatedCorrectly(List<Param> initParams, List<Param> updatedParams) {
        var oldState = initParams.stream().collect(Collectors.toMap(Param::getKey, Function.identity()));
        var currentState = updatedParams.stream().collect(Collectors.toMap(Param::getKey, Function.identity()));

        return currentState.entrySet().stream()
                .allMatch(entry -> oldState.get(entry.getKey()).getVersion() + 1 == entry.getValue().getVersion());
    }

    private boolean isEveryLbParamVersionUpdatedCorrectly(List<UserParamLBCHRow> initParams, List<UserParamLBCHRow> updatedParams) {
        var oldState = initParams.stream().collect(Collectors.toMap(row -> new ParamKey(new ParamOwnerKey(row.counterId(), row.userId()), row.fullPath()), Function.identity()));
        var currentState = updatedParams.stream().collect(Collectors.toMap(row -> new ParamKey(new ParamOwnerKey(row.counterId(), row.userId()), row.fullPath()), Function.identity()));

        return currentState.entrySet().stream()
                .allMatch(entry -> oldState.get(entry.getKey()).version() + 1 == entry.getValue().version());
    }
}
