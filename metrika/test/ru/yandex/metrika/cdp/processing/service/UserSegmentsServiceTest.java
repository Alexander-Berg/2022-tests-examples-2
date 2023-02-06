package ru.yandex.metrika.cdp.processing.service;

import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

import it.unimi.dsi.fastutil.longs.Long2LongLinkedOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2LongMap;
import it.unimi.dsi.fastutil.longs.Long2LongOpenHashMap;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.cdp.processing.dao.UserSegmentsDao;
import ru.yandex.metrika.cdp.processing.dto.segments.UserSegments;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManager;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManagerStub;
import ru.yandex.metrika.util.collections.DiffItem;

import static java.util.concurrent.CompletableFuture.completedFuture;
import static java.util.stream.Collectors.toMap;
import static org.junit.Assert.assertEquals;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.util.collections.DiffItem.added;
import static ru.yandex.metrika.util.collections.DiffItem.removed;
import static ru.yandex.metrika.util.collections.F.id;

public class UserSegmentsServiceTest {

    private static final Long USER_ID_1 = 1L;
    private static final Long USER_ID_2 = 2L;
    private static final Long USER_ID_3 = 3L;

    private static final Long TARGET_SEGMENT_ID = 1L;
    private static final Long OTHER_SEGMENT_ID_1 = 2L;
    private static final Long OTHER_SEGMENT_ID_2 = 3L;
    private static final Long OTHER_SEGMENT_ID_3 = 4L;

    private static final Long OLD_VERSION = 1L;
    private static final Long NEW_VERSION = 2L;


    private final UserSegmentsDao userSegmentsDao = mock(UserSegmentsDao.class);
    private final SegmentsMinValidVersionProviderStub segmentsMinValidVersionProvider = new SegmentsMinValidVersionProviderStub();
    private final YdbTransactionManager ydbTransactionManager = new YdbTransactionManagerStub();

    private final UserSegmentsService userSegmentsService = new UserSegmentsService(userSegmentsDao, segmentsMinValidVersionProvider, ydbTransactionManager, Optional.empty(), Optional.of(3));


    @Before
    public void setUp() {
        segmentsMinValidVersionProvider.clear();
    }

    @Test
    public void addSegmentsToState() {
        var diffItems = List.of(added(USER_ID_1));
        var oldState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION), 1L);
        var expectedState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, TARGET_SEGMENT_ID, NEW_VERSION), 2L);

        testUpdateSegmentsCase(diffItems, USER_ID_1, oldState, expectedState);
    }

    @Test
    public void deleteSegmentFromState() {
        var diffItems = List.of(removed(USER_ID_1));
        var oldState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, TARGET_SEGMENT_ID, NEW_VERSION), 1L);
        var expectedState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION), 2L);

        testUpdateSegmentsCase(diffItems, USER_ID_1, oldState, expectedState);
    }

    @Test
    public void addSegmentToStateWithCleanUp() {
        var diffItems = List.of(added(USER_ID_1));
        var oldState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION), 1L);
        var expectedState = new UserSegments(USER_ID_1, segments(TARGET_SEGMENT_ID, NEW_VERSION), 2L);

        segmentsMinValidVersionProvider.addWithInvalidVersion(OTHER_SEGMENT_ID_1);

        testUpdateSegmentsCase(diffItems, USER_ID_1, oldState, expectedState);
    }

    @Test
    public void mixedAddedAndRemovedSegmentsToState() {
        var diffItems = List.of(added(USER_ID_1), removed(USER_ID_2));
        var oldStates = List.of(
                new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION), 1L),
                new UserSegments(USER_ID_2, segments(OTHER_SEGMENT_ID_2, OLD_VERSION, TARGET_SEGMENT_ID, OLD_VERSION), 1L)
        );

        var expectedStates = List.of(
                new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, TARGET_SEGMENT_ID, NEW_VERSION), 2L),
                new UserSegments(USER_ID_2, segments(OTHER_SEGMENT_ID_2, OLD_VERSION), 2L)
        );

        testUpdateSegmentsCase(diffItems, List.of(USER_ID_1, USER_ID_2), oldStates, expectedStates);
    }

    @Test
    public void shrinkToSizeState() {
        var diffItems = List.of(added(USER_ID_1));
        var oldState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, OTHER_SEGMENT_ID_2, OLD_VERSION, OTHER_SEGMENT_ID_3, OLD_VERSION), 1L);
        var expectedState = new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_2, OLD_VERSION, OTHER_SEGMENT_ID_3, OLD_VERSION, TARGET_SEGMENT_ID, NEW_VERSION), 2L);

        testUpdateSegmentsCase(diffItems, USER_ID_1, oldState, expectedState);
    }

    @Test
    public void batchToResend() {
        int batchSize = 3;

        var oldStates = List.of(
                new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, OTHER_SEGMENT_ID_2, OLD_VERSION), 1L),
                new UserSegments(USER_ID_2, segments(OTHER_SEGMENT_ID_1, OLD_VERSION), 1L),
                new UserSegments(USER_ID_3, segments(OTHER_SEGMENT_ID_3, OLD_VERSION), 1L)
        );

        var expected = List.of(
                new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, OTHER_SEGMENT_ID_2, OLD_VERSION), 2L),
                new UserSegments(USER_ID_2, segments(OTHER_SEGMENT_ID_1, OLD_VERSION), 2L),
                new UserSegments(USER_ID_3, segments(OTHER_SEGMENT_ID_3, OLD_VERSION), 2L)
        );


        testBatchToResendCase(batchSize, oldStates, expected);
    }

    @Test
    public void batchToResendWithCleanUp() {
        int batchSize = 3;

        var oldStates = List.of(
                new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_1, OLD_VERSION, OTHER_SEGMENT_ID_2, OLD_VERSION), 1L),
                new UserSegments(USER_ID_2, segments(OTHER_SEGMENT_ID_1, NEW_VERSION), 1L),
                new UserSegments(USER_ID_3, segments(OTHER_SEGMENT_ID_3, OLD_VERSION), 1L)
        );

        segmentsMinValidVersionProvider.addWithVersion(OTHER_SEGMENT_ID_1, NEW_VERSION);
        segmentsMinValidVersionProvider.addWithVersion(OTHER_SEGMENT_ID_3, NEW_VERSION);

        var expected = List.of(
                new UserSegments(USER_ID_1, segments(OTHER_SEGMENT_ID_2, OLD_VERSION), 2L),
                new UserSegments(USER_ID_2, segments(OTHER_SEGMENT_ID_1, NEW_VERSION), 2L),
                new UserSegments(USER_ID_3, segments(), 2L)
        );


        testBatchToResendCase(batchSize, oldStates, expected);
    }

    @Test(expected = IllegalArgumentException.class)
    public void tooBigBatchToResend() {
        userSegmentsService.getBatchToResendAsync(1001);
    }

    private void testUpdateSegmentsCase(List<DiffItem<Long>> diffs, @SuppressWarnings("SameParameterValue") long userId, UserSegments oldState, UserSegments expectedState) {
        testUpdateSegmentsCase(diffs, List.of(userId), List.of(oldState), List.of(expectedState));

    }

    private void testUpdateSegmentsCase(List<DiffItem<Long>> diffs, List<Long> userIds, List<UserSegments> oldStates, List<UserSegments> expectedStates) {
        when(userSegmentsDao.getAsync(eq(userIds), any())).thenReturn(completedFuture(oldStates));
        when(userSegmentsDao.saveAsync(any(), any())).thenReturn(completedFuture(null));

        var userSegments = userSegmentsService.updateUserSegmentsAsync(TARGET_SEGMENT_ID, NEW_VERSION, diffs).join();

        assertEquals(expectedStates, userSegments);
    }

    private void testBatchToResendCase(int batchSize, List<UserSegments> oldStates, List<UserSegments> expected) {
        when(userSegmentsDao.getBatchUpdatedBeforeTimestampAsync(any(), eq(batchSize), any()))
                .thenReturn(completedFuture(oldStates));

        when(userSegmentsDao.saveAsync(any(), any())).thenReturn(completedFuture(null));

        var toResend = userSegmentsService.getBatchToResendAsync(batchSize).join();

        assertEquals(expected, toResend);
    }

    public Long2LongLinkedOpenHashMap segments(long... longs) {
        assert longs.length % 2 == 0;
        var mapSize = longs.length / 2;
        long[] keys = new long[mapSize];
        long[] values = new long[mapSize];

        for (int i = 0; i < mapSize; i++) {
            keys[i] = longs[2*i];
            values[i] = longs[2*i + 1];
        }

        return new Long2LongLinkedOpenHashMap(keys, values);
    }

    private static final class SegmentsMinValidVersionProviderStub implements SegmentsMinValidVersionProvider {
        private final Map<Long, Long> state = new HashMap<>();
        private boolean validByDefault = true;

        @Override
        public CompletableFuture<Long2LongMap> getMinVersionsAsync(Collection<Long> ids, QueryExecutionContext executionContext) {
            return CompletableFuture.completedFuture(
                    new Long2LongOpenHashMap(
                        ids.stream().collect(toMap(id(), id -> state.getOrDefault(id, validByDefault ? 0L : Long.MAX_VALUE)))
                    )
            );
        }

        public void addWithVersion(long segmentId, long minValidVersion) {
            state.put(segmentId, minValidVersion);
        }

        public void addWithValidVersion(long segmentId) {
            state.put(segmentId, 0L);
        }

        public void addWithInvalidVersion(long segmentId) {
            state.put(segmentId, Long.MAX_VALUE);
        }

        public void clear() {
            state.clear();
        }

        public void setValidByDefault(boolean validByDefault) {
            this.validByDefault = validByDefault;
        }
    }
}
