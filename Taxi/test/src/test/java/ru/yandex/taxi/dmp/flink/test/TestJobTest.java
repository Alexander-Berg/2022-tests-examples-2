package ru.yandex.taxi.dmp.flink.test;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeoutException;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.lang3.RandomUtils;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.kikimr.persqueue.LogbrokerClientFactory;
import ru.yandex.kikimr.persqueue.auth.Credentials;
import ru.yandex.kikimr.persqueue.consumer.BatchingStreamConsumer;
import ru.yandex.kikimr.persqueue.consumer.BatchingStreamListener;
import ru.yandex.kikimr.persqueue.consumer.stream.StreamConsumerConfig;
import ru.yandex.kikimr.persqueue.consumer.transport.message.CommitMessage;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerInitResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.kikimr.persqueue.proxy.ProxyBalancer;
import ru.yandex.taxi.dmp.flink.connectors.logbroker.common.SerializableSupplier;

@Disabled
public class TestJobTest {
    private static final Logger log = LoggerFactory.getLogger(TestJobTest.class);

    private static final String GROCERY_TOPIC = "/logbroker-playground/sashbel/testing-grocery-offers";
    private static final String TOPIC = "/logbroker-playground/kateleb/demo_raw_data";

//    private static final String TOPIC_OUT = "/logbroker-playground/kateleb/demo_ods_out_data";
//    private static final String CONSUMER = "/logbroker-playground/kateleb/test-consumer";

    private static final String TOPIC_OUT = "/logbroker-playground/sashbel/demo-topic-kl-out";
    private static final String CONSUMER = "/logbroker-playground/sashbel/demo-kl-consumer";

    @Test
    public void generateInputData() throws ExecutionException, InterruptedException, JsonProcessingException {
        var proxyBalancer = new ProxyBalancer("vla.logbroker.yandex.net");
        LogbrokerClientFactory lbFactory = new LogbrokerClientFactory(proxyBalancer);

        var config = AsyncProducerConfig
                .builder(TOPIC, StandardCharsets.UTF_8.encode("kateleb-test").array())
                .setCredentialsProvider(getLogbrokerOAuthToken())
                .build();

        var names = new String[]{"Vladimir", "Alexander", "Natalya", "Oleg", "Konstantin",
                "Valeriy", "Alexandra", "Mikhail", "Alexey", "Maksim", "Maksim", "Maksim",
                "Pavel", "Anton", "Semen", "Alexander", "Fedor", "Dmitriy", "Ivan"};

        ObjectMapper objectMapper = new ObjectMapper();

        try (var producer = lbFactory.asyncProducer(config)) {
            producer.init().get();

            var i = 0;
            while (true) {
                Map<String, Object> values = new HashMap<>();
                values.put("name", names[i]);
                values.put("b", RandomUtils.nextInt(1, 500));
                values.put("c", RandomUtils.nextInt(500, 1500));
                values.put("create_time", LocalDateTime.now().toString());

                String json = objectMapper.writeValueAsString(values);
                System.out.printf("Write %s \n", json);
                producer.write(json.getBytes(StandardCharsets.UTF_8)).get();
                i += 1;
                if (i == names.length) {
                    i = 0;
                }
                Thread.sleep(1000);
            }
        }
    }

    @Test
    public void readInput() throws InterruptedException, TimeoutException {
        var proxyBalancer = new ProxyBalancer("vla.logbroker.yandex.net");
        LogbrokerClientFactory lbFactory = new LogbrokerClientFactory(proxyBalancer);
        var proxyBalancerSas = new ProxyBalancer("sas.logbroker.yandex.net");
        LogbrokerClientFactory lbFactorySas = new LogbrokerClientFactory(proxyBalancerSas);
        var config = StreamConsumerConfig
                .builder(Collections.singleton(GROCERY_TOPIC), CONSUMER)
                .setCredentialsProvider(getLogbrokerOAuthToken())
                .build();
//        var consumer = lbFactory.batchingStreamConsumer(config);
//
//        readMessages(consumer);
        var consumerVla = lbFactory.batchingStreamConsumer(config);
        var consumerSas = lbFactorySas.batchingStreamConsumer(config);

        readMessages(consumerSas);
        readMessages(consumerVla);

        Thread.sleep(10 * 60 * 60 * 1000);
    }

    @Test
    public void readOutput() throws InterruptedException, TimeoutException {
        var proxyBalancerVla = new ProxyBalancer("vla.logbroker.yandex.net");
        LogbrokerClientFactory lbFactoryVla = new LogbrokerClientFactory(proxyBalancerVla);

        var proxyBalancerSas = new ProxyBalancer("sas.logbroker.yandex.net");
        LogbrokerClientFactory lbFactorySas = new LogbrokerClientFactory(proxyBalancerSas);

        var config = StreamConsumerConfig
                .builder(Collections.singleton(TOPIC_OUT), CONSUMER)
                .setCredentialsProvider(getLogbrokerOAuthToken())
                .build();
        var consumerVla = lbFactoryVla.batchingStreamConsumer(config);
        var consumerSas = lbFactorySas.batchingStreamConsumer(config);

        readMessages(consumerSas);
        readMessages(consumerVla);

        Thread.sleep(10 * 60 * 60 * 1000);

    }

    private void readMessages(BatchingStreamConsumer consumer) throws InterruptedException, TimeoutException {
        consumer.startConsume(
                new BatchingStreamListener() {
                    @Override
                    public void onInit(ConsumerInitResponse init) {

                    }

                    @Override
                    public void onRead(ConsumerReadResponse readResponse, ReadResponder readResponder) {
                        if (readResponse != null) {
                            readResponse.getBatches().forEach(batch -> {
                                batch.getMessageData().forEach(data -> {
                                    var str = new String(data.getDecompressedData(), StandardCharsets.UTF_8);
                                    System.out.println(str);
                                });
                            });
                            readResponder.commit(Collections.singletonList(readResponse.getCookie()));
                        }
                    }

                    @Override
                    public void onCommit(CommitMessage commit) {

                    }

                    @Override
                    public void onClose() {

                    }

                    @Override
                    public void onError(Throwable e) {

                    }
                }
        );
    }

    private SerializableSupplier<Credentials> getLogbrokerOAuthToken() {
        var token = readFileFromHome(".logbroker", "token");
        return () -> Credentials.oauth(token);
    }

    private String readFileFromHome(String... path) {
        try {
            return readFile(Paths.get(System.getProperty("user.home"), path));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private String readFile(Path path) throws IOException {
        var reader = Files.newBufferedReader(path);
        try {
            return reader.readLine();
        } finally {
            reader.close();
        }
    }

}
