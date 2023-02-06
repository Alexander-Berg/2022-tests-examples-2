package ru.yandex.metrika.direct.dict.target.phrases;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

import javax.annotation.PostConstruct;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.producer.AsyncProducer;
import ru.yandex.kikimr.persqueue.producer.async.AsyncProducerConfig;
import ru.yandex.metrika.direct.config.DirectDictJdbcTestConfig;
import ru.yandex.metrika.direct.config.DirectDictLogbrokerTestConfig;
import ru.yandex.metrika.direct.config.DirectDictYtTestConfig;
import ru.yandex.metrika.direct.config.MockedBazingaConfig;
import ru.yandex.metrika.direct.dict.common.DirectIdResolver;
import ru.yandex.metrika.lb.read.AbstractLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.read.LogbrokerConsumerFactory;
import ru.yandex.metrika.lb.read.SelfListeningStreamConsumer;
import ru.yandex.metrika.lb.read.processing.ProcessingStreamListener;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqBatchSerializer;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.concurrent.Pools;

import static metrika.AdvClickDictionaryUpdate.TTargetPhrase;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static ru.yandex.metrika.direct.dict.utils.LogbrokerUtils.allMessagesIsProcessed;

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {TargetPhrasesProcessorTest.TestConfig.class})
public class TargetPhrasesProcessorTest {

    @Autowired
    LogbrokerClientAsyncFactory lbFactory;
    @Autowired
    AsyncProducerConfig targetPhrasesProducerConfig;
    @Autowired
    ProtoSeqBatchSerializer<TTargetPhrase> serializer;
    @Autowired
    MySqlDynamicConditionsDao dynamicConditionsDao;

    @Autowired
    TargetPhraseProcessor spyingTargetPhrasesProcessor;

    @Autowired
    SelfListeningStreamConsumer targetPhraseConsumer;

    @PostConstruct
    public void startConsume() {
        targetPhraseConsumer.startConsume();
    }

    @Before
    public void resetSpy() {
        reset(spyingTargetPhrasesProcessor);
    }

    @Test
    public void simpleTest() throws Exception {
        // [0, 100)
        int size = 100;
        var data = genData(new Random(0), 0, size);
        CountDownLatch latch = allMessagesIsProcessed(spyingTargetPhrasesProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<DynamicConditionEntity> res = dynamicConditionsDao.getRange(0, size);
        assertThat(res, hasSize(size));
        List<String> expectedNames = getExpectedNames(data);
        List<String> actualNames = F.map(res, DynamicConditionEntity::conditionName);
        assertThat(actualNames, containsInAnyOrder(expectedNames.toArray()));
    }

    @Test
    public void nullTest() throws Exception {
        // [100, 200)

        int testOffset = 100;
        int size = 100;
        var data = genData(new Random(0), testOffset, size);
        dynamicConditionsDao.update(F.map(data, it ->
                new DynamicConditionEntity(it.getTargetPhraseID(), it.getOrderID(), "with zero", null)
        ));

        CountDownLatch latch = allMessagesIsProcessed(spyingTargetPhrasesProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<DynamicConditionEntity> res = dynamicConditionsDao.getRange(testOffset, size);
        assertThat(res, hasSize(size));
        List<String> expectedNames = getExpectedNames(data);
        List<String> actualNames = F.map(res, DynamicConditionEntity::conditionName);
        assertThat(actualNames, containsInAnyOrder(expectedNames.toArray()));
    }

    @Test
    public void severalMessagesTest() throws Exception {
        // [1000, 6000)
        int testOffset = 1000;
        int size = 500;

        var random = new Random(0);
        int numberOfMessageSequence = 10;
        var msgs = IntStream.range(0, numberOfMessageSequence)
                .mapToObj(i -> genData(random, testOffset + size * i, size))
                .toList();

        int totalNumberOfMessages = size * numberOfMessageSequence;
        CountDownLatch latch = allMessagesIsProcessed(spyingTargetPhrasesProcessor, totalNumberOfMessages);

        for (var m : msgs) {
            writeData(m);
        }

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<DynamicConditionEntity> res = dynamicConditionsDao.getRange(testOffset, totalNumberOfMessages);
        assertThat(res, hasSize(totalNumberOfMessages));
    }

    @Test
    public void timeoutTest() throws Exception {
        // [6000, 6200)
        int testOffset = 6000;
        var size = 100;

        var oldData = genData(new Random(0), testOffset, size);
        long oldTime = Instant.now().toEpochMilli() - 2 * TestConfig.TIMEOUT;
        dynamicConditionsDao.update(F.map(oldData, it ->
                new DynamicConditionEntity(it.getTargetPhraseID(), it.getOrderID(), "outdated name", oldTime)
        ));

        var recentData = genData(new Random(0), testOffset + size, size);
        long recentTime = Instant.now().toEpochMilli() - 10;
        dynamicConditionsDao.update(F.map(recentData, it ->
                new DynamicConditionEntity(it.getTargetPhraseID(), it.getOrderID(), "actual name", recentTime)
        ));

        int totalNumberOfMessages = 2 * size;
        CountDownLatch latch = allMessagesIsProcessed(spyingTargetPhrasesProcessor, totalNumberOfMessages);

        writeData(oldData);
        writeData(recentData);

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<DynamicConditionEntity> resWithOldData = dynamicConditionsDao.getRange(testOffset, size);
        assertThat(resWithOldData, hasSize(size));
        List<String> expectedNames = getExpectedNames(oldData);
        List<String> actualOldNames = F.map(resWithOldData, DynamicConditionEntity::conditionName);
        assertThat(actualOldNames, containsInAnyOrder(expectedNames.toArray()));

        List<DynamicConditionEntity> resWithRecentData = dynamicConditionsDao.getRange(testOffset + size, size);
        assertThat(resWithRecentData, hasSize(size));
        List<String> actualRecentNames = F.map(resWithRecentData, DynamicConditionEntity::conditionName);
        assertThat(actualRecentNames, everyItem(equalTo("actual name")));
    }

    private List<TTargetPhrase> genData(Random rnd, int offset, int size) {
        return IntStream.range(offset, offset + size)
                .mapToObj(
                        i -> TTargetPhrase.newBuilder()
                                .setOrderID(Math.abs(rnd.nextInt()))
                                .setTargetPhraseID(i)
                                .build()
                )
                .toList();
    }

    private void writeData(List<TTargetPhrase> data) {
        try (AsyncProducer producer = lbFactory.asyncProducer(targetPhrasesProducerConfig).join()) {
            producer.init().join();
            producer.write(serializer.serialize(data)).join();
        }
    }

    private List<String> getExpectedNames(List<TTargetPhrase> data) {
        return F.map(data, it -> TestConfig
                .infoConverter(new DynamicConditionInfo(it.getOrderID(), it.getTargetPhraseID()))
                .getConditionName()
        );
    }

    @Configuration
    @Import({
            DirectDictLogbrokerTestConfig.class,
            MockedBazingaConfig.class,
            DirectDictYtTestConfig.class,
            DirectDictJdbcTestConfig.class
    })
    static class TestConfig {

        static final long TIMEOUT = TimeUnit.SECONDS.toMillis(30);

        static DynamicCondition infoConverter(DynamicConditionInfo info) {
            return new DynamicCondition(info.getDynCondId(), info.getOrderId(), "name#" + info.getDynCondId());
        }

        @Bean
        public DirectIdResolver<DynamicConditionInfo, DynamicCondition> dummyDynamicConditionResolver() {
            return info -> F.map(info, TestConfig::infoConverter);
        }


        @Bean
        public TargetPhraseProcessor spyingTargetPhrasesProcessor(
                MySqlDynamicConditionsDao mySqlDynamicConditionsDao,
                DirectIdResolver<DynamicConditionInfo, DynamicCondition> dummyDynamicConditionResolver
        ) {
            var processor = new TargetPhraseProcessor(
                    mySqlDynamicConditionsDao, dummyDynamicConditionResolver,
                    Pools.newNamedFixedThreadPool(2, "target-phrases-processor-pool")
            );
            processor.setUpdateTimeout(TIMEOUT);
            return spy(processor);
        }

        @Bean
        public SelfListeningStreamConsumer targetPhrasesConsumer(
                LogbrokerConsumerFactory lbkxConsumerFactory,
                AbstractLogbrokerConsumerConfig targetPhrasesConsumerConfig,
                TargetPhraseProcessor spyingTargetPhrasesProcessor,
                ProtoSeqBatchSerializer<TTargetPhrase> protoSeqTargetPhrasesSerializer
        ) {
            return lbkxConsumerFactory.processingConsumer(
                    targetPhrasesConsumerConfig,
                    ProcessingStreamListener.withProcessor(spyingTargetPhrasesProcessor)
                            .withBatchSerializer(protoSeqTargetPhrasesSerializer)
                            .withoutSorting()
            );
        }
    }
}
