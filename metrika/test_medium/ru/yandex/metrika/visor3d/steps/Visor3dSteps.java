package ru.yandex.metrika.visor3d.steps;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeoutException;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.protobuf.InvalidProtocolBufferException;
import org.awaitility.core.ConditionTimeoutException;
import org.joda.time.format.DateTimeFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.common.test.medium.YtClient;
import ru.yandex.metrika.dbclients.yt.TransactionAtomicity;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStat;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqSerializer;
import ru.yandex.metrika.visord.process.clickhouse.ClickHouseFinalEvent;
import ru.yandex.metrika.visord.process.lb.LogbrokerEventsProtoSerializer;
import ru.yandex.metrika.wv2.proto.LogbrokerMessages.LogbrokerMessage;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.stream.Collectors.toList;
import static org.awaitility.Awaitility.await;
import static org.joda.time.DateTime.now;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.common.test.medium.YtClient.buildYtPath;
import static ru.yandex.metrika.visor3d.tests.Matchers.matchWebVisorLogs;
import static ru.yandex.metrika.visor3d.tests.Matchers.matchWebVisorLogsWithMessages;
import static ru.yandex.metrika.visor3d.tests.Matchers.matchWebVisorLogsWithoutYT;
import static ru.yandex.metrika.visor3d.tests.Matchers.tablesNotExist;

@Component
public class Visor3dSteps {

    private static final Logger log = LoggerFactory.getLogger(Visor3dSteps.class);

    @Autowired
    private Visor3dSettings settings;

    @Autowired
    private Visor3dGenerationSteps generation;

    @Autowired
    private YtClient ytClient;

    @Autowired
    private LogbrokerClientAsyncFactory logbrokerClientAsyncFactory;

    private AsyncProducer producer;

    @Autowired
    private ProcessedMessagesStat processedMessagesStat;

    public Visor3dGenerationSteps generation() {
        return generation;
    }

    @Autowired
    @Qualifier("eventsConsumer")
    private SyncConsumer eventsConsumer;

    @Autowired
    @Qualifier("scrollsConsumer")
    private SyncConsumer scrollsConsumer;

    @Autowired
    @Qualifier("cryptaConsumer")
    private SyncConsumer cryptaConsumer;

    @Step("Подготовка")
    public void prepare() {
        log.debug("Подготовка");
        createYtTables();
        initLbProducer();
        processedMessagesStat.clear();
        clearOutputTopics();
    }

    private void initLbProducer() {
        producer = logbrokerClientAsyncFactory.asyncProducer(settings.getLogbrokerSourceWvLogTopic(), "sourceId".getBytes()).join();
        producer.init().join();
    }

    @Step("Создание таблиц в YT")
    public void createYtTables() {
        ytClient.clearMapNode(settings.getOutputYtPath());
        ytClient.createDynamicTable(buildYtPath(settings.getOutputYtPath(), getDividedDateSuffix()), EventPacket.class, Map.of("atomicity", TransactionAtomicity.none.toString()));
    }

    @Step("Очищаем выходные топики")
    public void clearOutputTopics() {
        cleanTopic(eventsConsumer);
        cleanTopic(cryptaConsumer);
        cleanTopic(scrollsConsumer);
    }

    @Step("Записываем некорректный чанк на вход, запускаем демон и проверяем результат")
    public void writeIncorrectChunkAndCheckResult(List<WebVisorLog> hits) {
        writeInputChunkAndWait(hits);

        Visor3dOutput actualOutput = readIncorrectOutput();

        assertThat("выходные таблицы отсутствуют", actualOutput, tablesNotExist());
    }

    @Step("Записываем корректный чанк на вход, запускаем демон и проверяем результат")
    public void writeCorrectChunkAndCheckResult(List<WebVisorLog> hits) {
        writeInputChunkAndWait(hits);
        Visor3dOutput actualOutput = readOutput();
        assertThat("выходные данные соответствуют логам ВебВизора", actualOutput, matchWebVisorLogs(hits));
    }

    @Step("Записываем корректный чанк на вход, запускаем демон и проверяем результат")
    public void writeCorrectChunkAndCheckResultWithMessages(List<WebVisorLog> hits) {
        writeInputChunkAndWait(hits);
        Visor3dOutput actualOutput = readOutput();
        assertThat("выходные данные соответствуют логам ВебВизора", actualOutput, matchWebVisorLogsWithMessages(hits));
    }

    @Step("Записываем корректный чанк на вход, запускаем демон и проверяем результат")
    public void writeCorrectChunkAndCheckResultWithoutYT(List<WebVisorLog> hits) {
        writeInputChunkAndWait(hits);
        Visor3dOutput actualOutput = readOutputWithoutYT();
        assertThat("выходные данные соответствуют логам ВебВизора", actualOutput, matchWebVisorLogsWithoutYT(hits));
    }

    public void writeInputChunkAndWait(List<WebVisorLog> hits) {
        try {
            writeInputLb(hits);

            processedMessagesStat.waitProcessing();
        } catch (IOException | InterruptedException ex) {
            throw new RuntimeException(ex);
        }
    }

    @Step("Записываем входные данные в топик логброкера")
    public void writeInputLb(List<WebVisorLog> hits) throws IOException {
        for (var hit : hits) {
            producer.write(hit.toTskv()).join();
        }

        processedMessagesStat.updateWrittenMessages(hits.size());
    }

    @Step("Получить выходные таблицы при некорректном входе")
    public Visor3dOutput readIncorrectOutput() {
        Boolean eventsTableEmpty = ytClient.select(buildYtPath(settings.getOutputYtPath(), getDividedDateSuffix()), EventPacket.class).size() == 0;
        return new Visor3dOutput()
                .withEventsTableEmpty(eventsTableEmpty);
    }

    @Step("Прочитать все выходные данные демона")
    public Visor3dOutput readOutput() {
        List<WebVisor2> webVisorEvents = readAllWebVisorEvents();
        List<ScrollPacket> scrolls = readAllScrolls();
        List<LogbrokerMessage> logbrokerMessages = readAllLogbrokerMessages();
        List<EventPacket> events = readAllEventPackets();
        return new Visor3dOutput()
                .withEvents(events)
                .withWebVisorEvents(webVisorEvents)
                .withScrolls(scrolls)
                .withLogbrokerMessages(logbrokerMessages);
    }

    @Step("Прочитать все выходные данные демона")
    public Visor3dOutput readOutputWithoutYT() {
        List<WebVisor2> webVisorEvents = readAllWebVisorEvents();
        List<ScrollPacket> scrolls = readAllScrolls();
        Boolean eventsTableEmpty = ytClient.select(buildYtPath(settings.getOutputYtPath(), getDividedDateSuffix()), EventPacket.class).size() == 0;
        return new Visor3dOutput()
                .withEventsTableEmpty(eventsTableEmpty)
                .withWebVisorEvents(webVisorEvents)
                .withScrolls(scrolls);
    }

    @Step("Прочесть все данные из YT таблицы")
    public List<EventPacket> readAllEventPackets() {
        return ytClient.select(buildYtPath(settings.getOutputYtPath(), getDividedDateSuffix()), EventPacket.class);
    }

    @Step("Прочитать все события WebVisor2 из локального Логброкера")
    public List<WebVisor2> readAllWebVisorEvents() {
        LogbrokerEventsProtoSerializer eventsProtoSerializer = new LogbrokerEventsProtoSerializer();
        ProtoSeqSerializer<List<ClickHouseFinalEvent>> protoSeqSerializer = new ProtoSeqSerializer<>(eventsProtoSerializer);

        List<ClickHouseFinalEvent> logbrokerMessages = new ArrayList<>();
        List<MessageBatch> messageBatches = readLogbrokerResult(eventsConsumer);
        logbrokerMessages.addAll(messageBatches.stream()
                .flatMap(messageBatch -> messageBatch.getMessageData().stream())
                .map(messageData -> protoSeqSerializer.deserialize(messageData.getRawData()))
                .flatMap(List::stream)
                .collect(toList()));
        List<WebVisor2> collect = logbrokerMessages.stream().map(WebVisor2::new).collect(toList());
        return collect;
    }

    @Step("Прочесть все скроллы из локального Логброкера")
    public List<ScrollPacket> readAllScrolls() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
                .configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);
        List<ScrollPacket> logbrokerMessages = new ArrayList<>();
        List<MessageBatch> messageBatches = readLogbrokerResult(scrollsConsumer);
        logbrokerMessages.addAll(messageBatches.stream()
                .flatMap(messageBatch -> messageBatch.getMessageData().stream())
                .map(messageData -> {
                    try {
                        return mapper
                                .readValue(messageData.getRawData(), new TypeReference<ScrollPacket>() {
                                });
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                })
                .collect(toList()));
        logbrokerMessages.removeIf(p -> p == null || p.getTable() == null || !p.getTable().endsWith("_1")); //remove sampled data
        logbrokerMessages.stream().filter(Objects::nonNull).filter(p -> p.getEvents() != null)
                .forEach(p -> p.setEventData(
                        new ByteString(p.getEvents()))); //rewrite setEventData with deserialized events
        return logbrokerMessages;
    }

    @Step("Прочесть все сообщения из локального Логброкера")
    public List<LogbrokerMessage> readAllLogbrokerMessages() {
        List<MessageBatch> messageBatches = readLogbrokerResult(cryptaConsumer);
        List<LogbrokerMessage> logbrokerMessages = messageBatches.stream()
                .flatMap(messageBatch -> messageBatch.getMessageData().stream())
                .map(messageData -> {
                    try {
                        return LogbrokerMessage.parser().parseFrom(messageData.getRawData());
                    } catch (InvalidProtocolBufferException e) {
                        throw new RuntimeException(e);
                    }
                })
                .collect(toList());
        return logbrokerMessages;
    }

    private List<MessageBatch> readLogbrokerResult(SyncConsumer syncConsumer) {
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
        return messageBatches;
    }

    private void cleanTopic(SyncConsumer syncConsumer) {
        try {
            var response = syncConsumer.read();
            while (response != null) {
                syncConsumer.commit(response.getCookie());
                response = syncConsumer.read();
            }
        } catch (InterruptedException | TimeoutException e) {
            e.printStackTrace();
        }
    }

    private static String getDateSuffix() {
        return DateTimeFormat.forPattern("yyyyMMdd").print(now());
    }

    private static String getDividedDateSuffix() {
        return DateTimeFormat.forPattern("yyyy-MM-dd").print(now());
    }

}
