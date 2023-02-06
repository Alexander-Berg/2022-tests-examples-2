package ru.yandex.metrika.restream.state_walker.processing;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import javax.annotation.Nonnull;

import com.google.api.client.util.Lists;
import com.google.common.primitives.UnsignedInteger;
import com.google.common.primitives.UnsignedLong;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.segments.SegmentRetargeting;
import ru.yandex.metrika.api.management.client.segments.SegmentStatus;
import ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.replica.ReplicaStub;
import ru.yandex.metrika.restream.collector.proto.Collector.RebuildRequest;
import ru.yandex.metrika.restream.dto.UserSegmentProfile;
import ru.yandex.metrika.restream.dto.UserSegmentProfile.Key;
import ru.yandex.metrika.restream.processing.ProfilesProcessor;
import ru.yandex.metrika.restream.segments.RestreamSegment;
import ru.yandex.metrika.restream.ydb.UserSegmentsProfilesDaoYdb;
import ru.yandex.metrika.restream.ydb.UserSegmentsProfilesDaoYdbTest;

import static org.hamcrest.Matchers.empty;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext.write;
import static ru.yandex.metrika.restream.ProfilesTestUtil.profile;
import static ru.yandex.metrika.restream.ProfilesTestUtil.visit;
import static ru.yandex.metrika.restream.state_walker.processing.StateWalker.toRebuildRequest;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class StateWalkerTest {

    private static final Duration visitTTL = Duration.ofDays(10);
    private static final Duration profileTTL = Duration.ofDays(20);

    private static final Duration noCleanUpDuration = Duration.ofDays(1);

    @Autowired
    public UserSegmentsProfilesDaoYdb dao;
    @Autowired
    public ProfilesProcessor profilesProcessor;
    @Autowired
    public ReplicaStub<Integer, RestreamSegment> replica;
    @Autowired
    public LogbrokerWriterStub<RebuildRequest> writerStub;

    public StateWalker.Config config;

    private Instant now;
    private int nowSeconds;

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(EnvironmentHelper.ydbDatabase + "/" + UserSegmentsProfilesDaoYdb.TABLE_NAME);
        now = Instant.now();
        nowSeconds = (int) now.getEpochSecond();
        config = new StateWalker.Config();
        config.setNoCleanUpDuration(noCleanUpDuration);
        replica.clear();
        writerStub.clear();
    }

    @Test
    public void walkOnEmptyState() {
        var walker = createWalker();
        var from = new Key(0, 0, 0);
        var to = new Key(UnsignedLong.MAX_VALUE.longValue(), 0, 0);

        var allData = Lists.newArrayList(dao.readTable(from, to));
        assertThat(allData, empty());

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to);

        allData = Lists.newArrayList(dao.readTable(from, to));
        assertThat(allData, empty());
    }

    @Nonnull
    private List<UserSegmentProfile> buildStateContent() {
        var keys = keysOrderedByHash(5);
        return List.of(
                new UserSegmentProfile( // empty profile with old enough lastMatched visit
                        keys.get(0).getUserId(), keys.get(0).getSegmentId(), 2, now.minus(noCleanUpDuration.plusDays(1)), profile(false)
                ),
                new UserSegmentProfile(
                        keys.get(1),
                        profile(true, visit(1, 2, nowSeconds, 1, 1))
                ),
                new UserSegmentProfile(
                        keys.get(2), // compactable
                        profile(true, visit(1, 3, nowSeconds, 1, 1), visit(1, 3, nowSeconds, 2, 1))
                ),
                new UserSegmentProfile(
                        keys.get(3), // compactable
                        profile(true, visit(1, 4, nowSeconds, 1, 1), visit(1, 4, nowSeconds, 2, 1))
                ),
                new UserSegmentProfile(
                        keys.get(4), // to be deleted if actual segment version 3
                        profile(true, visit(2, 5, (int) now.minus(noCleanUpDuration.plusDays(1)).getEpochSecond(), 1, 1))
                )
        );
    }

    @Test
    public void walkAndProcessNotEmptyState() {
        // by default limits are big enough to process all rows
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to); // walker should reach end of range

        var allData = Lists.newArrayList(dao.readTable(from, to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getFullyProcessedRebuildRequests());
    }

    @Nonnull
    private List<RebuildRequest> getFullyProcessedRebuildRequests() {
        var original = buildStateContent();
        return List.of(
                toRebuildRequest(original.get(2)),
                toRebuildRequest(original.get(3))
        );
    }

    @Test
    public void walkStopsOnReadLimit() {
        config.setMaxReadSize(2);
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, usps.get(1).asKey()); // should stop after 2 rows due to read limit

        var allData = Lists.newArrayList(dao.readTable(from, to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveNoMessages();
    }

    @Test
    public void walkerStopsOnUpdatesLimit() {
        config.setMaxUpdateSize(2);
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, usps.get(2).asKey()); // should stop after 3 rows due to update limit

        var allData = Lists.newArrayList(dao.readTable(from, to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getRebuildRequestsAfterStopDueToUpdateLimit());
    }

    @Nonnull
    private List<RebuildRequest> getRebuildRequestsAfterStopDueToUpdateLimit() {
        var original = buildStateContent();
        return List.of(
                toRebuildRequest(original.get(2))
        );
    }

    @Test
    public void walkDoesNotTouchRowsOutOfRange() {
        // by default limits are big enough to process all rows
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(1).asKey(); // starting from second row here
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to); // walker should reach end of range

        var allData = Lists.newArrayList(dao.readTable(usps.get(0).asKey(), to));
        assertEquals(usps, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getProcessedStartingFromSecondRowRebuildRequests());
    }

    @Nonnull
    private List<RebuildRequest> getProcessedStartingFromSecondRowRebuildRequests() {
        var original = buildStateContent();
        return List.of(
                toRebuildRequest(original.get(2)),
                toRebuildRequest(original.get(3))
        );
    }

    @Test
    public void walkSendsToRebuildOutdatedSegmentVersions() {
        // by default limits are big enough to process all rows
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();
        var lastRowSegmentId = usps.get(usps.size() - 1).getSegmentId();
        setSegmentActualVersion(lastRowSegmentId, 3);

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to); // walker should reach end of range

        var allData = Lists.newArrayList(dao.readTable(usps.get(0).asKey(), to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getFullyProcessedRequestsIfLastSendToRebuild());
    }

    private void setSegmentActualVersion(int segmentId, @SuppressWarnings("SameParameterValue") int segmentVersion) {
        replica.add(
                new RestreamSegment(
                        1, segmentId, "stub", segmentVersion, SegmentStatus.active,
                        SegmentRetargeting.ALLOW, StreamabilityClass.NOT_STREAMABLE, true, now
                )
        );
    }

    @Test
    public void walkSendsToRebuildNotRetargetingSegmentsData() {
        // by default limits are big enough to process all rows
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();
        var lastRowSegmentId = usps.get(usps.size() - 1).getSegmentId();
        markSegmentNotRetargeting(lastRowSegmentId);

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to); // walker should reach end of range

        var allData = Lists.newArrayList(dao.readTable(usps.get(0).asKey(), to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getFullyProcessedRequestsIfLastSendToRebuild());
    }

    private void markSegmentNotRetargeting(int segmentId) {
        replica.add(
                new RestreamSegment(
                        1, segmentId, "stub", 1, SegmentStatus.active,
                        SegmentRetargeting.ALLOW, StreamabilityClass.NOT_STREAMABLE, false, now
                )
        );
    }

    @Test
    public void walkSendsToRebuildNotActiveSegmentsData() {
        // by default limits are big enough to process all rows
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();
        var lastRowSegmentId = usps.get(usps.size() - 1).getSegmentId();
        markSegmentNotActive(lastRowSegmentId);

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to); // walker should reach end of range

        var allData = Lists.newArrayList(dao.readTable(usps.get(0).asKey(), to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getFullyProcessedRequestsIfLastSendToRebuild());
    }

    private void markSegmentNotActive(int segmentId) {
        replica.add(
                new RestreamSegment(
                        1, segmentId, "stub", 1, SegmentStatus.deleted,
                        SegmentRetargeting.ALLOW, StreamabilityClass.NOT_STREAMABLE, true, now
                )
        );
    }

    @Test
    public void walkSendsToRebuildSegmentsWithNotAllowedRetargetingData() {
        // by default limits are big enough to process all rows
        var walker = createWalker();

        var usps = buildStateContent();
        var from = usps.get(0).asKey();
        var to = getNexKey(usps.get(usps.size() - 1).asKey());

        dao.saveProfiles(usps, write()).join();
        var lastRowSegmentId = usps.get(usps.size() - 1).getSegmentId();
        markSegmentNotAllowRetargeting(lastRowSegmentId);

        var walkEnd = walker.walk(from, to);
        assertEquals(walkEnd, to); // walker should reach end of range

        var allData = Lists.newArrayList(dao.readTable(usps.get(0).asKey(), to));
        assertEquals(usps.subList(1, 5)/*first deleted*/, allData);

        writerStub.assertHaveOnlyMessagesInOrder(getFullyProcessedRequestsIfLastSendToRebuild());
    }

    private void markSegmentNotAllowRetargeting(int segmentId) {
        replica.add(
                new RestreamSegment(
                        1, segmentId, "stub", 1, SegmentStatus.active,
                        SegmentRetargeting.NOT_ALLOW, StreamabilityClass.NOT_STREAMABLE, true, now
                )
        );
    }

    @Nonnull
    private List<RebuildRequest> getFullyProcessedRequestsIfLastSendToRebuild() {
        var original = buildStateContent();
        return List.of(
                toRebuildRequest(original.get(2)),
                toRebuildRequest(original.get(3)),
                toRebuildRequest(original.get(4))
        );
    }

    @Nonnull
    private StateWalker createWalker() {
        return new StateWalker(dao, replica, profilesProcessor, config, writerStub);
    }

    private UserSegmentProfile compacted(UserSegmentProfile userSegmentProfile) {
        return userSegmentProfile.updateProfile(profilesProcessor.compact(userSegmentProfile.getProfile()));
    }

    private static List<Key> keysOrderedByHash(@SuppressWarnings("SameParameterValue") int size) {
        return IntStream.rangeClosed(1, size).mapToObj(i -> new Key(i, i)).sorted().collect(Collectors.toList());
    }

    private static Key getNexKey(Key key) {
        if (Integer.compareUnsigned(key.getSegmentId(), UnsignedInteger.MAX_VALUE.intValue()) < 0) {
            return new Key(key.getUserIdHash(), key.getUserId(), key.getSegmentId() + 1);
        }
        if (Long.compareUnsigned(key.getUserId(), UnsignedLong.MAX_VALUE.longValue()) < 0) {
            return new Key(key.getUserIdHash(), key.getUserId() + 1, 0);
        }
        if (Long.compareUnsigned(key.getUserIdHash(), UnsignedLong.MAX_VALUE.longValue()) < 0) {
            return new Key(key.getUserIdHash() + 1, 0, 0);
        }
        throw new NoSuchElementException("Key " + key + " is already biggest key");
    }

    @Configuration
    @Import(UserSegmentsProfilesDaoYdbTest.Config.class)
    public static class Config {
        @Bean
        public ProfilesProcessor profilesProcessor() {
            return new ProfilesProcessor(visitTTL, profileTTL);
        }

        @Bean
        public ReplicaStub<Integer, RestreamSegment> replicaStub() {
            return new ReplicaStub<>();
        }

        @Bean
        public LogbrokerWriterStub<RebuildRequest> writerStub() {
            return new LogbrokerWriterStub<>();
        }
    }

}
