package ru.yandex.metrika.userparams2d.steps;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeoutException;

import org.awaitility.core.ConditionTimeoutException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.common.test.medium.YtClient;
import ru.yandex.metrika.lb.serialization.Serializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwner;
import ru.yandex.metrika.userparams.UserParamLBCHRow;
import ru.yandex.metrika.userparams.YtParamRowWrapper;
import ru.yandex.metrika.userparams2d.config.UserParamsSettings;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.stream.Collectors.toList;
import static org.awaitility.Awaitility.await;

@Component
public class DataSteps {

    Logger log = LoggerFactory.getLogger(DataSteps.class);

    @Autowired
    @Qualifier("outputGigaConsumer")
    private SyncConsumer outputGigaConsumer;

    @Autowired
    @Qualifier("outputNanoConsumer")
    private SyncConsumer outputNanoConsumer;

    @Autowired
    @Qualifier("waitingInputWriter")
    private WaitingLogbrokerWriter<UserParamUpdate> inputWriter;

    @Autowired
    @Qualifier("waitingApiInputWriter")
    private WaitingLogbrokerWriter<UserParamUpdate> apiInputWriter;

    @Autowired
    private Serializer<UserParamLBCHRow> userParamSerializer;

    @Autowired
    private YtClient ytClient;

    @Autowired
    private UserParamsSettings settings;


    @Step("Подать параметры на вход демону")
    public void writeParamUpdatesToInputTopic(List<UserParamUpdate> params) {
        log.info("writing params {} ot input topic", params);
        inputWriter.writeBatchAsync(params).join();
    }


    @Step("Подать параметры, записанные через api, на вход демону")
    public void writeParamUpdatesFromApiToInputTopic(List<UserParamUpdate> params) {
        apiInputWriter.writeBatchAsync(params).join();
    }

    @Step("Подождать пока все данные, поданные на вход, обработаются")
    public void waitProcessing() throws InterruptedException {
        inputWriter.waitProcessing();
    }

    @Step("Подать параметры на вход демону и подождать пока они обработаются")
    public void writeParamUpdatesToInputTopicAndWaitProcessing(List<UserParamUpdate> params) throws InterruptedException {
        writeParamUpdatesToInputTopic(params);

        waitProcessing();
    }

    @Step("подать параметры, записанные через API, на вход демону и подождать пока они обработаются")
    public void writeParamUpdatesFromApiToInputTopicAndWaitProcessing(List<UserParamUpdate> params) throws InterruptedException {
        writeParamUpdatesFromApiToInputTopic(params);

        waitProcessing();
    }

    @Step("Прочитать данные, записанные в гига топик")
    public List<UserParamLBCHRow> readDataFromOutputGigaTopic() {
        return readResultFromLogbroker(outputGigaConsumer, userParamSerializer);
    }

    @Step("Прочитать данные, записанные в нано топик")
    public List<UserParamLBCHRow> readDataFromOutputNanoTopic() {
        return readResultFromLogbroker(outputNanoConsumer, userParamSerializer);
    }

    @Step("Прочитать параметры записанные в YT")
    public List<Param> readParamsFromYt() {
        return ytClient.select(settings.getParamsYtTable(), YtParamRowWrapper.class)
                .stream()
                .filter(row -> !row.getDeleted())
                .map(YtParamRowWrapper::getParam)
                .toList();
    }

    @Step("Прочитать параметры, помеченные как удаленные в YT")
    public List<Param> readDeletedParamsFromYt() {
        return ytClient.select(settings.getParamsYtTable(), YtParamRowWrapper.class)
                .stream()
                .filter(YtParamRowWrapper::getDeleted)
                .map(YtParamRowWrapper::getParam)
                .toList();
    }

    @Step("Прочитать овнеров записанных в YT")
    public List<ParamOwner> readParamOwnersFromYt() {
        return ytClient.select(settings.getParamOwnersYtTable(), ParamOwner.class);
    }

    @Step("Прочитать содержимое таблички с clientUserId из YT")
    public List<ParamOwner> readClientUserIdMatchingFromYt() {
        return ytClient.select(settings.getClientUserIdMatchingYtTable(), ParamOwner.class);
    }

    @Step("Очистить выходной гига топик")
    public void clearOutputGigaTopic() {
        clearLogbroker(outputGigaConsumer);
    }

    @Step("Очистить выходной нано топик")
    public void clearOutputNanoTopic() {
        clearLogbroker(outputNanoConsumer);
    }

    private <T> List<T> readResultFromLogbroker(SyncConsumer syncConsumer, Serializer<T> serializer) {
        ArrayList<MessageBatch> messageBatches = new ArrayList<>();
        boolean isAnyRead = true;
        while (isAnyRead) {
            try {
                await().atMost(3000, MILLISECONDS)
                        .pollInterval(100, MILLISECONDS)
                        .ignoreException(InterruptedException.class)
                        .until(() -> {
                            ConsumerReadResponse read = syncConsumer.read();
                            if (read != null && read.getBatches() != null && read.getBatches().size() > 0) {
                                messageBatches.addAll(read.getBatches());
                                syncConsumer.commit(read.getCookie());
                                Thread.sleep(1000);
                                return true;
                            }
                            return false;
                        });
            } catch (ConditionTimeoutException e) {
                isAnyRead = false;
            }
        }

        return messageBatches.stream()
                .flatMap(messageBatch -> messageBatch.getMessageData().stream())
                .map(messageData -> serializer.deserialize(messageData.getRawData()))
                .collect(toList());
    }

    private void clearLogbroker(SyncConsumer consumer) {
        boolean isAnyRead = true;
        while (isAnyRead) {
            try {
                ConsumerReadResponse read = consumer.read();
                if (read != null && read.getBatches() != null && read.getBatches().size() > 0) {
                    consumer.commit(read.getCookie());
                } else {
                    isAnyRead = false;
                }
            } catch (InterruptedException | TimeoutException ignored) {
            }
        }
    }
}

