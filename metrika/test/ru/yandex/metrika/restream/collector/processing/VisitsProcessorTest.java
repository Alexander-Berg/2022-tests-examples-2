package ru.yandex.metrika.restream.collector.processing;

import java.time.Duration;
import java.time.Instant;
import java.util.stream.Stream;

import javax.annotation.Nonnull;

import com.codahale.metrics.MetricRegistry;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManagerStub;
import ru.yandex.metrika.lb.read.processing.LbReadProcessingTestUtil;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.restream.dto.UserSegmentProfile.Key;
import ru.yandex.metrika.restream.processing.ProfilesProcessor;
import ru.yandex.metrika.restream.proto.Restream;
import ru.yandex.metrika.retargeting.BsSegment;
import ru.yandex.metrika.retargeting.BsSegmentTestUtil;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class VisitsProcessorTest {

    private final MetricRegistry metricRegistry = new MetricRegistry();
    private final ProfilesProcessor profilesProcessor = new ProfilesProcessor(Duration.ofDays(1), Duration.ofDays(10));
    private final UserSegmentProfilesDaoStub daoStub = new UserSegmentProfilesDaoStub();
    private final LogbrokerWriterStub<BsSegment> writerStub = new LogbrokerWriterStub<>();
    private final YdbTransactionManagerStub transactionManagerStub = new YdbTransactionManagerStub();

    private final VisitsProcessor visitsProcessor = new VisitsProcessor(
            transactionManagerStub,
            daoStub,
            profilesProcessor,
            writerStub,
            1,
            Integer.MAX_VALUE
    );

    @Before
    public void setUp() {
        daoStub.clear();
        writerStub.clear();
        visitsProcessor.afterPropertiesSet();
    }

    @Test
    public void simpleNewVersionOnEmptyState() {
        var userId = 2;
        var segmentId = 1000000001;
        var timestamp = (int) Instant.now().getEpochSecond();
        var processedVisit = processedVisit(userId, segmentId, timestamp, 1, 1, 1);

        process(processedVisit);

        var userSegmentProfile = daoStub.state.get(new Key(userId, segmentId));
        assertFalse(userSegmentProfile.isToDelete());
        assertEquals(1, userSegmentProfile.getRevision());
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(timestamp, segmentId, userId, false, 1)
        );
    }

    @Test
    public void plusVersionAndThenMinusOnEmptyState() {
        var userId = 2;
        var segmentId = 1000000001;
        var timestamp = (int) Instant.now().getEpochSecond();
        var processedVisit = processedVisit(userId, segmentId, timestamp, 1, 1, 1);

        process(processedVisit);

        var minusSignVisit = processedVisit.toBuilder().setSign(-1).build();
        process(minusSignVisit);

        var userSegmentProfile = daoStub.state.get(new Key(userId, segmentId));
        assertTrue(userSegmentProfile.isToDelete());
        assertEquals(2, userSegmentProfile.getRevision());
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(timestamp, segmentId, userId, false, 1),
                new BsSegment(timestamp, segmentId, userId, true, 2)
        );
    }

    @Test
    public void minusVersionAndThenPlusOnEmptyState() {
        var userId = 2;
        var segmentId = 1000000001;
        var timestamp = (int) Instant.now().getEpochSecond();
        var processedVisit = processedVisit(userId, segmentId, timestamp, 1, 1, -1);

        process(processedVisit);

        var plusSignVisit = processedVisit.toBuilder().setSign(1).build();
        process(plusSignVisit);

        var userSegmentProfile = daoStub.state.get(new Key(userId, segmentId));
        assertTrue("Expected empty profile but got " + userSegmentProfile.getProfile(), userSegmentProfile.isToDelete());
        assertEquals(1, userSegmentProfile.getRevision());
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(timestamp, segmentId, userId, true, 1),
                new BsSegment(timestamp, segmentId, userId, true, 1)
        );
    }

    @Test
    public void plusVersionAndThenMinusOnNotEmptyState() {
        var userId = 2;
        var segmentId = 1000000001;
        var firstTimestamp = (int) Instant.now().minusSeconds(1000).getEpochSecond();
        var secondTimestamp = (int) Instant.now().getEpochSecond();
        var firstProcessedVisit = processedVisit(userId, segmentId, firstTimestamp, 1, 1, 1);

        process(firstProcessedVisit);

        var secondProcessedVisit = processedVisit(userId, segmentId, secondTimestamp, 2, 1, 1);
        process(secondProcessedVisit);

        var minusSignSecondVisit = secondProcessedVisit.toBuilder().setSign(-1).build();
        process(minusSignSecondVisit);

        var userSegmentProfile = daoStub.state.get(new Key(userId, segmentId));
        assertFalse(userSegmentProfile.isToDelete());
        assertEquals(3, userSegmentProfile.getRevision());
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(firstTimestamp, segmentId, userId, false, 1),
                new BsSegment(secondTimestamp, segmentId, userId, false, 2),
                new BsSegment(firstTimestamp, segmentId, userId, false, 3)
        );
    }

    @Test
    public void minusVersionAndThenPlusOnNotEmptyState() {
        var userId = 2;
        var segmentId = 1000000001;
        var firstTimestamp = (int) Instant.now().minusSeconds(1000).getEpochSecond();
        var secondTimestamp = (int) Instant.now().getEpochSecond();
        var firstProcessedVisit = processedVisit(userId, segmentId, firstTimestamp, 1, 1, 1);

        process(firstProcessedVisit);

        var secondProcessedVisit = processedVisit(userId, segmentId, secondTimestamp, 2, 1, -1);
        process(secondProcessedVisit);

        var plusSignSecondVisit = secondProcessedVisit.toBuilder().setSign(1).build();
        process(plusSignSecondVisit);

        var userSegmentProfile = daoStub.state.get(new Key(userId, segmentId));
        assertFalse(userSegmentProfile.isToDelete());
        assertEquals(2, userSegmentProfile.getRevision());
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(firstTimestamp, segmentId, userId, false, 1),
                new BsSegment(firstTimestamp, segmentId, userId, false, 2),
                new BsSegment(firstTimestamp, segmentId, userId, false, 2)
        );
    }

    private void process(Restream.ProcessedVisit processedVisit) {
        visitsProcessor.process(1, Stream.of(LbReadProcessingTestUtil.lbMessage(processedVisit))).join();
    }

    @Nonnull
    private static Restream.ProcessedVisit processedVisit(int userId, int segmentId, int timestamp, long visitId, int visitVersion, int sign) {
        return Restream.ProcessedVisit.newBuilder()
                .setCounterID(1)
                .setUserID(userId)
                .setVisitID(visitId)
                .setUTCStartTime(timestamp)
                .setVisitVersion(visitVersion)
                .setSign(sign)
                .addMatchedSegments(
                        Restream.SegmentReference.newBuilder()
                                .setSegmentId(segmentId)
                                .setVersion(1)
                                .build()
                ).build();
    }

}
