package ru.yandex.metrika.userparams.sharder.steps;

import java.util.ArrayList;
import java.util.List;

import org.awaitility.core.ConditionTimeoutException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.proto.UserParamsProtoSerializer;
import ru.yandex.metrika.userparams.proto.UserParamsUpdateProtoSerializer;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.stream.Collectors.toList;
import static org.awaitility.Awaitility.await;

@Component
public class DataSteps {

    @Autowired
    @Qualifier("inputConsumer")
    private SyncConsumer inputConsumer;

    @Autowired
    @Qualifier("outputConsumer")
    private SyncConsumer outputConsumer;

    @Autowired
    private WaitingLogbrokerWriter<ListParamWrapper> downstream;

    private final UserParamsUpdateProtoSerializer userParamsUpdateSerializer = new UserParamsUpdateProtoSerializer(new UserParamsProtoSerializer());


    @Step("Записать тестовые данные во входной топик")
    public void writeUserparamsToInputTopic(List<ListParamWrapper> params) {
        downstream.writeBatchAsync(params).join();
    }

    @Step("Подождать пока данные обработаются процессором")
    public void waitProcessing() throws InterruptedException {
        downstream.waitProcessing();
    }

    @Step("Записать тестовые данные во входной топик их обработки")
    public void writeUserParamsToInputAndWaitProcessing(List<ListParamWrapper> params) throws InterruptedException {
        writeUserparamsToInputTopic(params);

        waitProcessing();
    }

    @Step("Прочитать параметры посетителей из выходного топика")
    public List<UserParamUpdate> readUserparamsUpdatesFromOutputTopic() {
        return readResultFromLogbroker(outputConsumer, userParamsUpdateSerializer);
    }

    public void resetWaitingLogbrokerWriter() {
        downstream.clear();
    }

    private <T> List<T> readResultFromLogbroker(SyncConsumer syncConsumer, ProtoSerializer<T> serializer) {
        List<MessageBatch> messageBatches = new ArrayList<>();
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
}
