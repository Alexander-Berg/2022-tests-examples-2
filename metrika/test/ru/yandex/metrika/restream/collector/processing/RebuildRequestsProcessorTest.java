package ru.yandex.metrika.restream.collector.processing;

import java.time.Duration;
import java.time.Instant;
import java.util.stream.Stream;

import javax.annotation.Nonnull;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.segments.SegmentRetargeting;
import ru.yandex.metrika.api.management.client.segments.SegmentStatus;
import ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManagerStub;
import ru.yandex.metrika.lb.read.processing.LbReadProcessingTestUtil;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.replica.ReplicaStub;
import ru.yandex.metrika.restream.collector.proto.Collector;
import ru.yandex.metrika.restream.dto.UserSegmentProfile;
import ru.yandex.metrika.restream.processing.ProfilesProcessor;
import ru.yandex.metrika.restream.segments.RestreamSegment;
import ru.yandex.metrika.retargeting.BsSegment;
import ru.yandex.metrika.retargeting.BsSegmentTestUtil;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.restream.ProfilesTestUtil.matchedProfile;
import static ru.yandex.metrika.restream.ProfilesTestUtil.visit;

public class RebuildRequestsProcessorTest {

    private final ProfilesProcessor profilesProcessor = new ProfilesProcessor(Duration.ofDays(1), Duration.ofDays(10));
    private final UserSegmentProfilesDaoStub daoStub = new UserSegmentProfilesDaoStub();
    private final ReplicaStub<Integer, RestreamSegment> replicaStub = new ReplicaStub<>();
    private final LogbrokerWriterStub<BsSegment> writerStub = new LogbrokerWriterStub<>();
    private final YdbTransactionManagerStub transactionManagerStub = new YdbTransactionManagerStub();

    private final RebuildRequestsProcessor rebuildRequestsProcessor = new RebuildRequestsProcessor(
            daoStub,
            replicaStub,
            transactionManagerStub,
            profilesProcessor,
            writerStub,
            1000
    );

    private Instant now;
    private int nowSeconds;

    @Before
    public void setUp() {
        daoStub.clear();
        writerStub.clear();
        replicaStub.clear();
        now = Instant.now();
        nowSeconds = (int) now.getEpochSecond();
    }

    @Test
    public void rebuildWithNoSegmentInfo() {
        var profile = matchedProfile(visit(1, 1, nowSeconds, 1, 1));
        var key = new UserSegmentProfile.Key(1, 1);
        var usp = new UserSegmentProfile(key, profile);

        daoStub.state.put(key, usp);

        process(keyToRequest(key));

        var fromDao = daoStub.state.get(key);
        assertThat(fromDao, equalTo(usp));
        writerStub.assertHaveOnlyMessagesInOrder(
                new BsSegment(nowSeconds, 1, 1, false, 1)
        );

    }

    @Test
    public void rebuildWithActualSegmentInfo() {
        var profile = matchedProfile(visit(1, 1, nowSeconds, 1, 1));
        var key = new UserSegmentProfile.Key(1, 1);
        var usp = new UserSegmentProfile(key, profile);

        daoStub.state.put(key, usp);
        // сегмент полностью подходящий под все условия (версия, статус, ретаргетинг)
        // не должен приводить к каким либо обновлениям
        replicaStub.add(new RestreamSegment(1, 1, "stub", 1, SegmentStatus.active, SegmentRetargeting.ALLOW, StreamabilityClass.NOT_STREAMABLE, true, now));

        process(keyToRequest(key));

        var fromDao = daoStub.state.get(key);
        assertThat(fromDao, equalTo(usp));
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(nowSeconds, 1, 1, false, 1)
        );

    }

    @Test
    public void rebuildWithOutdatedSegmentVersionInfo() {
        var profile = matchedProfile(visit(1, 1, nowSeconds, 1, 1));
        var key = new UserSegmentProfile.Key(1, 1);
        var usp = new UserSegmentProfile(key, profile);

        daoStub.state.put(key, usp);
        // сегмент с версией больше чем в профиле, а значит нужно удалять
        replicaStub.add(new RestreamSegment(1, 1, "stub", 2, SegmentStatus.active, SegmentRetargeting.ALLOW, StreamabilityClass.NOT_STREAMABLE, true, now));

        process(keyToRequest(key));

        var fromDao = daoStub.state.get(key);
        assertTrue(fromDao.isToDelete());
        assertThat(fromDao.getRevision(), equalTo(2L));
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(nowSeconds, 1, 1, true, 2)
        );

    }

    @Test
    public void rebuildWithForSegmentWithNotAllowedRetargeting() {
        var profile = matchedProfile(visit(1, 1, nowSeconds, 1, 1));
        var key = new UserSegmentProfile.Key(1, 1);
        var usp = new UserSegmentProfile(key, profile);

        daoStub.state.put(key, usp);
        // сегмент, на котором запретили ретаргетинг
        replicaStub.add(new RestreamSegment(1, 1, "stub", 1, SegmentStatus.active, SegmentRetargeting.NOT_ALLOW, StreamabilityClass.NOT_STREAMABLE, true, now));

        process(keyToRequest(key));

        var fromDao = daoStub.state.get(key);
        assertTrue(fromDao.isToDelete());
        assertThat(fromDao.getRevision(), equalTo(2L));
        writerStub.assertHaveOnlyMessagesInOrder(
                BsSegmentTestUtil::sameBsSegments,
                new BsSegment(nowSeconds, 1, 1, true, 2)
        );
    }

    @Nonnull
    private Collector.RebuildRequest keyToRequest(UserSegmentProfile.Key key) {
        return Collector.RebuildRequest.newBuilder().setUserID(key.getUserId()).setSegmentID(key.getSegmentId()).build();
    }

    private void process(Collector.RebuildRequest rebuildRequest) {
        rebuildRequestsProcessor.process(1, Stream.of(LbReadProcessingTestUtil.lbMessage(rebuildRequest))).join();
    }
}
