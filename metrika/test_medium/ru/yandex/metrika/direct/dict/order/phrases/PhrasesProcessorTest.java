package ru.yandex.metrika.direct.dict.order.phrases;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

import javax.annotation.PostConstruct;

import metrika.AdvClickDictionaryUpdate.TOrderPhrase;
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
@ContextConfiguration(classes = {PhrasesProcessorTest.TestConfig.class})
public class PhrasesProcessorTest {

    @Autowired
    LogbrokerClientAsyncFactory lbFactory;
    @Autowired
    AsyncProducerConfig phrasesProducerConfig;
    @Autowired
    ProtoSeqBatchSerializer<TOrderPhrase> serializer;
    @Autowired
    YtPhrasesDao ytPhrasesDao;

    @Autowired
    PhrasesProcessor spyingPhrasesProcessor;

    @Autowired
    SelfListeningStreamConsumer phraseConsumer;

    @PostConstruct
    public void startConsume() {
        phraseConsumer.startConsume();
    }

    @Before
    public void resetSpy() {
        reset(spyingPhrasesProcessor);
    }

    @Test
    public void simpleTest() throws Exception {
        // [0, 100)
        int size = 100;
        var data = genData(new Random(0), 0, size);
        CountDownLatch latch = allMessagesIsProcessed(spyingPhrasesProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtPhrase> res = ytPhrasesDao.getRange(0, size);
        assertThat(res, hasSize(size));
        List<String> expectedNames = getExpectedNames(data);
        List<String> actualNames = F.map(res, YtPhrase::getName);
        assertThat(actualNames, containsInAnyOrder(expectedNames.toArray()));
    }

    @Test
    public void nullTest() throws Exception {
        // [100, 200)

        int testOffset = 100;
        int size = 100;
        var data = genData(new Random(0), testOffset, size);
        ytPhrasesDao.update(F.map(data, it ->
                new YtPhrase(it.getPhraseID(), "with zero", 0)
        ));

        CountDownLatch latch = allMessagesIsProcessed(spyingPhrasesProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtPhrase> res = ytPhrasesDao.getRange(testOffset, size);
        assertThat(res, hasSize(size));
        List<String> expectedNames = getExpectedNames(data);
        List<String> actualNames = F.map(res, YtPhrase::getName);
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
        CountDownLatch latch = allMessagesIsProcessed(spyingPhrasesProcessor, totalNumberOfMessages);

        for (var m : msgs) {
            writeData(m);
        }

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtPhrase> res = ytPhrasesDao.getRange(testOffset, totalNumberOfMessages);
        assertThat(res, hasSize(totalNumberOfMessages));
    }

    @Test
    public void timeoutTest() throws Exception {
        // [6000, 6200)
        int testOffset = 6000;
        var size = 100;

        var oldData = genData(new Random(0), testOffset, size);
        long oldTime = Instant.now().toEpochMilli() - 2 * TestConfig.TIMEOUT;
        ytPhrasesDao.update(F.map(oldData, it ->
                new YtPhrase(it.getPhraseID(), "outdated name", oldTime)
        ));

        var recentData = genData(new Random(0), testOffset + size, size);
        long recentTime = Instant.now().toEpochMilli() - 10;
        ytPhrasesDao.update(F.map(recentData, it ->
                new YtPhrase(it.getPhraseID(), "actual name", recentTime)
        ));

        int totalNumberOfMessages = 2 * size;
        CountDownLatch latch = allMessagesIsProcessed(spyingPhrasesProcessor, totalNumberOfMessages);

        writeData(oldData);
        writeData(recentData);

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtPhrase> resWithOldData = ytPhrasesDao.getRange(testOffset, size);
        assertThat(resWithOldData, hasSize(size));
        List<String> expectedNames = getExpectedNames(oldData);
        List<String> actualOldNames = F.map(resWithOldData, YtPhrase::getName);
        assertThat(actualOldNames, containsInAnyOrder(expectedNames.toArray()));

        List<YtPhrase> resWithRecentData = ytPhrasesDao.getRange(testOffset + size, size);
        assertThat(resWithRecentData, hasSize(size));
        List<String> actualRecentNames = F.map(resWithRecentData, YtPhrase::getName);
        assertThat(actualRecentNames, everyItem(equalTo("actual name")));
    }

    private List<TOrderPhrase> genData(Random rnd, int offset, int size) {
        return IntStream.range(offset, offset + size)
                .mapToObj(i -> TOrderPhrase.newBuilder().setOrderID(rnd.nextInt()).setPhraseID(i).build())
                .toList();
    }

    private void writeData(List<TOrderPhrase> data) {
        try (AsyncProducer producer = lbFactory.asyncProducer(phrasesProducerConfig).join()) {
            producer.init().join();
            producer.write(serializer.serialize(data)).join();
        }
    }

    private List<String> getExpectedNames(List<TOrderPhrase> data) {
        return F.map(data, it -> TestConfig.infoConverter(new PhraseInfo(it)).text());
    }

    @Configuration
    @Import({
            DirectDictLogbrokerTestConfig.class,
            MockedBazingaConfig.class,
            DirectDictYtTestConfig.class
    })
    static class TestConfig {

        static final long TIMEOUT = TimeUnit.SECONDS.toMillis(30);

        static Phrase infoConverter(PhraseInfo info) {
            return new Phrase(info.getPhraseId(), "name#" + info.getPhraseId());
        }

        @Bean
        public DirectIdResolver<PhraseInfo, Phrase> dummyPhrasesResolver() {
            return info -> F.map(info, TestConfig::infoConverter);
        }


        @Bean
        public PhrasesProcessor spyingPhrasesProcessor(
                YtPhrasesDao ytPhrasesDao,
                DirectIdResolver<PhraseInfo, Phrase> dummyPhrasesResolver
        ) {
            var processor = new PhrasesProcessor(
                    ytPhrasesDao, dummyPhrasesResolver, Executors.newFixedThreadPool(5)
            );
            processor.setUpdateTimeout(TIMEOUT);
            return spy(processor);
        }

        @Bean
        public SelfListeningStreamConsumer phraseConsumer(
                LogbrokerConsumerFactory consumerFactory,
                AbstractLogbrokerConsumerConfig phrasesConsumerConfig,
                PhrasesProcessor spyingPhrasesProcessor,
                ProtoSeqBatchSerializer<TOrderPhrase> protoSeqPhrasesSerializer
        ) {
            return consumerFactory.processingConsumer(
                    phrasesConsumerConfig,
                    ProcessingStreamListener.withProcessor(spyingPhrasesProcessor)
                            .withBatchSerializer(protoSeqPhrasesSerializer)
                            .withoutSorting()
            );
        }
    }
}
