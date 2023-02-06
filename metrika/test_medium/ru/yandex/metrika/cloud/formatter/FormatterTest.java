package ru.yandex.metrika.cloud.formatter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.google.common.collect.Lists;
import com.google.protobuf.ByteString;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.StreamConsumer;
import ru.yandex.kikimr.persqueue.consumer.stream.StreamConsumerConfig;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.metrika.cloud.formatter.common.ExactlyOnceLbTransfer;
import ru.yandex.metrika.cloud.formatter.config.CloudFormatterLbTestConfig;
import ru.yandex.metrika.cloud.formatter.config.CloudFormatterTransferTestConfig;
import ru.yandex.metrika.lb.read.SimpleLogbrokerStreamListener;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqBatchSerializer;
import ru.yandex.metrika.util.collections.F;

import static java.lang.Thread.sleep;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.metrika.cloud.formatter.config.CloudFormatterLbTestConfig.TEST_CLOUD_VISITS_TOPIC;
import static ru.yandex.metrika.cloud.formatter.config.CloudFormatterLbTestConfig.TEST_FORMATTED_CLOUD_VISITS_TOPIC;
import static ru.yandex.metrika.cloud.formatter.config.CloudFormatterLbTestConfig.TOPICS_PARTITIONS;
import static ru.yandex.metrika.cloud.proto.FormattedVisitOuterClass.FormattedVisit;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {FormatterTest.TestConfig.class})
public class FormatterTest {

    @Autowired
    LogbrokerClientAsyncFactory factory;

    @Autowired
    ProtoSeqBatchSerializer<FormattedVisit> serializer;

    @Autowired
    AsyncProducerConfig inputWriterConfig;

    @Autowired
    ExactlyOnceLbTransfer<FormattedVisit, FormattedVisit> visitFormatter;

    @Autowired
    StreamConsumerConfig baseStreamConsumerConfigForVisits;

    @Autowired
    StreamConsumerConfig validatingConsumerConfig;

    @Test
    public void testFormatting() throws InterruptedException, TimeoutException {
        final int totalSize = 10000;

        var data = genData(totalSize);
        Random rnd = new Random(0);
        Collections.shuffle(data, rnd);
        var dataParts = Lists.partition(data, 100);

        F.sequence(
                IntStream.range(0, dataParts.size())
                        .mapToObj(i -> {
                            var config = new AsyncProducerConfig.Builder(inputWriterConfig)
                                    .setSourceId(("i = " + i).getBytes())
                                    .build();
                            return factory.asyncProducer(config)
                                    .thenCompose(producer -> producer.init().thenApply(r -> producer))
                                    .thenCompose(producer -> producer.write(serializer.serialize(dataParts.get(i))));
                        })
                        .toList()
        );

        var consumers = IntStream.range(0, TOPICS_PARTITIONS)
                .mapToObj(i -> factory.streamConsumer(baseStreamConsumerConfigForVisits).join())
                .toList();

        consumers.forEach(visitFormatter::startNewConsumer);

        ConcurrentLinkedQueue<FormattedVisit> result = new ConcurrentLinkedQueue<>();

        StreamConsumer reader = factory.streamConsumer(validatingConsumerConfig).join();
        reader.startConsume(
                new SimpleLogbrokerStreamListener() {
                    @Override
                    public void onRead(ConsumerReadResponse read, ReadResponder readResponder) {
                        read.getBatches().forEach(batch ->
                                batch.getMessageData().forEach(messageData ->
                                        result.addAll(serializer.deserialize(messageData.getDecompressedData()))
                                )
                        );
                        readResponder.commit();
                        System.out.println(result.size() + " of " + totalSize + " have been read");
                    }
                }
        );

        while (result.size() < totalSize) {
            sleep(1500);
            System.out.println("waiting... " + result.size() + "/" + totalSize);
        }

        Assert.assertThat(result, hasSize(totalSize));

        var resultCounters = F.map(result, FormattedVisit::getCounterID);
        var expectedCounters = F.map(data, FormattedVisit::getCounterID);
        Assert.assertThat(resultCounters, containsInAnyOrder(expectedCounters.toArray()));
    }


    private ArrayList<FormattedVisit> genData(int size) {
        return IntStream.range(0, size)
                .mapToObj(i -> genDefaultVisitBuilder().setCounterID(i).build())
                .collect(Collectors.toCollection(ArrayList::new));
    }

    private FormattedVisit.Builder genDefaultVisitBuilder() {
        return FormattedVisit.newBuilder()
                .setCounterID(0)
                .setDuration(10)
                .setEndURL(ByteString.copyFromUtf8("endUrl"))
                .setStartURL(ByteString.copyFromUtf8("startUrl"))
                .setIsBounce(false)
                .setReferer(ByteString.copyFromUtf8("referer"))
                .setSign(1)
                .setStartDate(12345)
                .setVisitID(42);
    }

    @Configuration
    @Import({CloudFormatterLbTestConfig.class, CloudFormatterTransferTestConfig.class})
    static class TestConfig {
        @Bean
        AsyncProducerConfig inputWriterConfig() {
            return AsyncProducerConfig
                    .builder(TEST_CLOUD_VISITS_TOPIC, "default".getBytes())
                    .build();
        }

        @Bean
        StreamConsumerConfig validatingConsumerConfig() {
            return StreamConsumerConfig
                    .builder(List.of(TEST_FORMATTED_CLOUD_VISITS_TOPIC), "/test/consumer")
                    .build();
        }
    }
}
