package ru.yandex.metrika.direct.dict.banners;

import java.time.Instant;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
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

import static metrika.AdvClickDictionaryUpdate.TBanner;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static ru.yandex.metrika.direct.dict.banners.YtBannersIdMapDao.YtBannerIdToBid;
import static ru.yandex.metrika.direct.dict.utils.LogbrokerUtils.allMessagesIsProcessed;

/**
 * Следим, чтобы id не пересекались у разных тестов
 */
@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {DirectBannersProcessorTest.BgTestConfig.class})
public class DirectBannersProcessorTest {

    @Autowired
    LogbrokerClientAsyncFactory lbFactory;
    @Autowired
    AsyncProducerConfig bannersProducerConfig;
    @Autowired
    ProtoSeqBatchSerializer<TBanner> serializer;
    @Autowired
    YtBannersIdMapDao ytBannersMapIdDao;

    @Autowired
    BannersProcessor spyingBannersProcessor;

    @Autowired
    SelfListeningStreamConsumer bannerConsumer;

    @PostConstruct
    public void startConsume() {
        bannerConsumer.startConsume();
    }

    @Before
    public void resetSpy() {
        reset(spyingBannersProcessor);
    }

    @Test
    public void simpleTest() throws Exception {
        // [0, 100)
        int size = 100;
        var data = genData(new Random(0), 0, size);
        CountDownLatch latch = allMessagesIsProcessed(spyingBannersProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerIdToBid> res = ytBannersMapIdDao.getRange(0, size);
        assertThat(res, hasSize(size));
        List<Long> expectedNames = getExpectedBid(data);
        List<Long> actualNames = F.map(res, YtBannersIdMapDao.YtBannerIdToBid::bid);
        assertThat(actualNames, containsInAnyOrder(expectedNames.toArray()));
    }

    @Test
    public void nullTest() throws Exception {
        // [100, 200)

        int testOffset = 100;
        int size = 100;
        var data = genData(new Random(0), testOffset, size);
        ytBannersMapIdDao.update(F.map(data, it ->
                new YtBannerIdToBid(it.getBannerID(), it.getBannerID(), null)
        ));

        CountDownLatch latch = allMessagesIsProcessed(spyingBannersProcessor, size);

        writeData(data);
        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerIdToBid> res = ytBannersMapIdDao.getRange(testOffset, size);
        assertThat(res, hasSize(size));
        List<Long> expectedBid = getExpectedBid(data);
        List<Long> actualBid = F.map(res, YtBannerIdToBid::bid);
        assertThat(actualBid, containsInAnyOrder(expectedBid.toArray()));
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
        CountDownLatch latch = allMessagesIsProcessed(spyingBannersProcessor, totalNumberOfMessages);

        for (var m : msgs) {
            writeData(m);
        }

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerIdToBid> res = ytBannersMapIdDao.getRange(testOffset, totalNumberOfMessages);
        assertThat(res, hasSize(totalNumberOfMessages));
    }

    @Test
    public void timeoutTest() throws Exception {
        // [6000, 6200)
        int testOffset = 6000;
        var size = 100;

        var oldData = genData(new Random(0), testOffset, size);
        long oldTime = Instant.now().toEpochMilli() - 2 * BgTestConfig.TIMEOUT;
        ytBannersMapIdDao.update(F.map(oldData, it ->
                new YtBannerIdToBid(it.getBannerID(), it.getBannerID() - 77, oldTime)
        ));

        var recentData = genData(new Random(0), testOffset + size, size);
        long recentTime = Instant.now().toEpochMilli() - 10;
        ytBannersMapIdDao.update(F.map(recentData, it ->
                new YtBannerIdToBid(it.getBannerID(), it.getBannerID() + 42, recentTime)
        ));

        int totalNumberOfMessages = 2 * size;
        CountDownLatch latch = allMessagesIsProcessed(spyingBannersProcessor, totalNumberOfMessages);

        writeData(oldData);
        writeData(recentData);

        assertTrue(latch.await(10, TimeUnit.SECONDS));

        List<YtBannerIdToBid> resWithOldData = ytBannersMapIdDao.getRange(testOffset, size);
        assertThat(resWithOldData, hasSize(size));
        List<Long> expectedOldBid = getExpectedBid(oldData);
        List<Long> actualOldBid = F.map(resWithOldData, YtBannerIdToBid::bid);
        assertThat(actualOldBid, containsInAnyOrder(expectedOldBid.toArray()));

        List<YtBannerIdToBid> resWithRecentData = ytBannersMapIdDao.getRange(testOffset + size, size);
        assertThat(resWithRecentData, hasSize(size));
        List<Long> expectedRecentBid = F.map(recentData, it -> it.getBannerID() + 42);
        List<Long> actualRecentBid = F.map(resWithRecentData, YtBannerIdToBid::bid);
        assertThat(actualRecentBid, containsInAnyOrder(expectedRecentBid.toArray()));

    }

    private List<TBanner> genData(Random rnd, int offset, int size) {
        return IntStream.range(offset, offset + size)
                .mapToObj(i -> TBanner.newBuilder().setOrderID(rnd.nextInt()).setBannerID(i).build())
                .toList();
    }

    private void writeData(List<TBanner> data) {
        try (AsyncProducer producer = lbFactory.asyncProducer(bannersProducerConfig).join()) {
            producer.init().join();
            producer.write(serializer.serialize(data)).join();
        }
    }

    private List<Long> getExpectedBid(List<TBanner> data) {
        return F.map(data, it -> BgTestConfig.infoConverter(new BannerInfo(it)).getBid());
    }

    @Configuration
    @Import({
            DirectDictLogbrokerTestConfig.class,
            MockedBazingaConfig.class,
            DirectDictYtTestConfig.class
    })
    static class BgTestConfig {

        static final long TIMEOUT = TimeUnit.SECONDS.toMillis(30);

        static BannerResponse infoConverter(BannerInfo info) {
            return new BannerResponse(
                    info.getBannerId(), "title#" + info.getBannerId(), "body#" + info.getBannerId(),
                    info.getBannerId() + 7
            );
        }

        @Bean
        public DirectIdResolver<BannerInfo, BannerResponse> dummyBannersResolver() {
            return info -> F.map(info, BgTestConfig::infoConverter);
        }

        @Bean
        public BannersProcessor spyingBannersProcessor(
                YtBannersPersistenceService ytBannersPersistenceService,
                DirectIdResolver<BannerInfo, BannerResponse>  dummyBannersResolver
        ) {
            var processor = new BannersProcessor(
                    ytBannersPersistenceService, dummyBannersResolver, Executors.newFixedThreadPool(5)
            );
            processor.setUpdateTimeout(TIMEOUT);
            return spy(processor);
        }

        @Bean
        public SelfListeningStreamConsumer bannerConsumer(
                LogbrokerConsumerFactory consumerFactory,
                AbstractLogbrokerConsumerConfig bannersConsumerConfig,
                BannersProcessor spyingBannersProcessor,
                BatchSerializer<TBanner> protoSeqBannersSerializer
        ) {
            return consumerFactory.processingConsumer(
                    bannersConsumerConfig,
                    ProcessingStreamListener.withProcessor(spyingBannersProcessor)
                            .withBatchSerializer(protoSeqBannersSerializer)
                            .withoutSorting()
            );
        }
    }
}
