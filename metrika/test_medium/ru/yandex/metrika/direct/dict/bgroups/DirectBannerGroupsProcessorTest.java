package ru.yandex.metrika.direct.dict.bgroups;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

import javax.annotation.PostConstruct;

import metrika.AdvClickDictionaryUpdate.TBannerGroup;
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
import ru.yandex.metrika.lb.serialization.BatchSerializer;
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

/**
 * Следим, чтобы group_id не пересекались у разных тестов
 */
@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {DirectBannerGroupsProcessorTest.BgTestConfig.class})
public class DirectBannerGroupsProcessorTest {

    @Autowired
    LogbrokerClientAsyncFactory lbFactory;
    @Autowired
    AsyncProducerConfig bannerGroupsProducerConfig;
    @Autowired
    ProtoSeqBatchSerializer<TBannerGroup> serializer;
    @Autowired
    YtBannerGroupsDao ytBannerGroupsDao;

    @Autowired
    BannerGroupsProcessor spyingBannerGroupsProcessor;

    @Autowired
    SelfListeningStreamConsumer bannerGroupConsumer;

    @PostConstruct
    public void startConsume() {
        bannerGroupConsumer.startConsume();
    }

    @Before
    public void resetSpy() {
        reset(spyingBannerGroupsProcessor);
    }

    @Test
    public void simpleTest() throws Exception {
        // [0, 100)
        int size = 100;
        var data = genData(new Random(0), 0, size);
        CountDownLatch latch = allMessagesIsProcessed(spyingBannerGroupsProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerGroupsDao.YtBannerGroup> res = ytBannerGroupsDao.getRange(0, size);
        assertThat(res, hasSize(size));
        List<String> expectedNames = getExpectedNames(data);
        List<String> actualNames = F.map(res, YtBannerGroupsDao.YtBannerGroup::groupName);
        assertThat(actualNames, containsInAnyOrder(expectedNames.toArray()));
    }

    @Test
    public void nullTest() throws Exception {
        // [100, 200)

        int testOffset = 100;
        int size = 100;
        var data = genData(new Random(0), testOffset, size);
        ytBannerGroupsDao.update(F.map(data, it ->
                new YtBannerGroupsDao.YtBannerGroup(it.getBannerGroupID(), it.getOrderID(), "group with null", null)
        ));

        CountDownLatch latch = allMessagesIsProcessed(spyingBannerGroupsProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerGroupsDao.YtBannerGroup> res = ytBannerGroupsDao.getRange(testOffset, size);
        assertThat(res, hasSize(size));
        List<String> expectedNames = getExpectedNames(data);
        List<String> actualNames = F.map(res, YtBannerGroupsDao.YtBannerGroup::groupName);
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
        CountDownLatch latch = allMessagesIsProcessed(spyingBannerGroupsProcessor, totalNumberOfMessages);

        for (var m : msgs) {
            writeData(m);
        }

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerGroupsDao.YtBannerGroup> res = ytBannerGroupsDao.getRange(testOffset, totalNumberOfMessages);
        assertThat(res, hasSize(totalNumberOfMessages));
    }

    @Test
    public void timeoutTest() throws Exception {
        // [6000, 6200)
        int testOffset = 6000;
        var size = 100;

        var oldData = genData(new Random(0), testOffset, size);
        long oldTime = Instant.now().toEpochMilli() - 2 * BgTestConfig.TIMEOUT;
        ytBannerGroupsDao.update(F.map(oldData, it ->
                new YtBannerGroupsDao.YtBannerGroup(it.getBannerGroupID(), it.getOrderID(), "outdated name", oldTime)
        ));

        var recentData = genData(new Random(0), testOffset + size, size);
        long recentTime = Instant.now().toEpochMilli() - 10;
        ytBannerGroupsDao.update(F.map(recentData, it ->
                new YtBannerGroupsDao.YtBannerGroup(it.getBannerGroupID(), it.getOrderID(), "actual name", recentTime)
        ));

        int totalNumberOfMessages = 2 * size;
        CountDownLatch latch = allMessagesIsProcessed(spyingBannerGroupsProcessor, totalNumberOfMessages);

        writeData(oldData);
        writeData(recentData);

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerGroupsDao.YtBannerGroup> resWithOldData = ytBannerGroupsDao.getRange(testOffset, size);
        assertThat(resWithOldData, hasSize(size));
        List<String> expectedNames = getExpectedNames(oldData);
        List<String> actualOldNames = F.map(resWithOldData, YtBannerGroupsDao.YtBannerGroup::groupName);
        assertThat(actualOldNames, containsInAnyOrder(expectedNames.toArray()));

        List<YtBannerGroupsDao.YtBannerGroup> resWithRecentData = ytBannerGroupsDao.getRange(testOffset + size, size);
        assertThat(resWithRecentData, hasSize(size));
        List<String> actualRecentNames = F.map(resWithRecentData, YtBannerGroupsDao.YtBannerGroup::groupName);
        assertThat(actualRecentNames, everyItem(equalTo("actual name")));
    }

    private List<TBannerGroup> genData(Random rnd, int offset, int size) {
        return IntStream.range(offset, offset + size)
                .mapToObj(i -> TBannerGroup.newBuilder().setOrderID(rnd.nextInt()).setBannerGroupID(i).build())
                .toList();
    }

    private void writeData(List<TBannerGroup> data) {
        try (AsyncProducer producer = lbFactory.asyncProducer(bannerGroupsProducerConfig).join()) {
            producer.init().join();
            producer.write(serializer.serialize(data)).join();
        }
    }

    private List<String> getExpectedNames(List<TBannerGroup> data) {
        return F.map(data, it -> BgTestConfig.infoConverter(new BannerGroupRequestInfo(it)).getGroupName());
    }

    @Configuration
    @Import({
            DirectDictLogbrokerTestConfig.class,
            MockedBazingaConfig.class,
            DirectDictYtTestConfig.class
    })
    static class BgTestConfig {

        static final long TIMEOUT = TimeUnit.SECONDS.toMillis(30);

        static BannerGroup infoConverter(BannerGroupRequestInfo info) {
            return new BannerGroup(info.getGroupId(), info.getOrderId(), "name#" + info.getGroupId());
        }

        @Bean
        public DirectIdResolver<BannerGroupRequestInfo, BannerGroup> dummyBannersResolver() {
            return info -> F.map(info, BgTestConfig::infoConverter);
        }


        @Bean
        public BannerGroupsProcessor spyingBannerGroupsProcessor(
                YtBannerGroupsDao ytBannerGroupsDao,
                DirectIdResolver<BannerGroupRequestInfo, BannerGroup> bannersResolver
        ) {
            var processor = new BannerGroupsProcessor(
                    ytBannerGroupsDao, bannersResolver, Executors.newFixedThreadPool(5)
            );
            processor.setUpdateTimeout(TIMEOUT);
            return spy(processor);
        }

        @Bean
        public SelfListeningStreamConsumer bannerGroupConsumer(
                LogbrokerConsumerFactory consumerFactory,
                AbstractLogbrokerConsumerConfig bannerGroupsConsumerConfig,
                BannerGroupsProcessor spyingBannerGroupsProcessor,
                BatchSerializer<TBannerGroup> protoSeqBannerGroupsSerializer
        ) {
            return consumerFactory.processingConsumer(
                    bannerGroupsConsumerConfig,
                    ProcessingStreamListener.withProcessor(spyingBannerGroupsProcessor)
                            .withBatchSerializer(protoSeqBannerGroupsSerializer)
                            .withoutSorting()
            );
        }
    }
}
