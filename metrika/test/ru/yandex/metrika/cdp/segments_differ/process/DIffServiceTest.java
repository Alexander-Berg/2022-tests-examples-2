package ru.yandex.metrika.cdp.segments_differ.process;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

import com.vividsolutions.jts.util.Assert;
import it.unimi.dsi.fastutil.longs.Long2LongLinkedOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2LongOpenHashMap;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.audience.util.RetargetingId;
import ru.yandex.audience.util.RetargetingType;
import ru.yandex.metrika.cdp.processing.dao.UserSegmentsDao;
import ru.yandex.metrika.cdp.processing.dto.segments.BigbPayload;
import ru.yandex.metrika.cdp.processing.dto.segments.UserSegments;
import ru.yandex.metrika.cdp.processing.service.SegmentsMinValidVersionProvider;
import ru.yandex.metrika.cdp.processing.service.UserSegmentsService;
import ru.yandex.metrika.cdp.segments_differ.dao.EvaluationSnaphotDao;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManager;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManagerStub;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;
import ru.yandex.metrika.util.collections.CloseableIterable;
import ru.yandex.metrika.util.collections.CloseableIterator;

import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class DIffServiceTest {
    private static final Long USER_ID_1 = 1L;
    private static final Long USER_ID_2 = 2L;

    private static final Long SEGMENT_ID_1 = 1L;
    private static final Long SEGMENT_ID_2 = 2L;
    private static final Long SEGMENT_ID_3 = 3L;
    private static final Long SEGMENT_ID_4 = 4L;

    private static final Long OLD_VERSION = 1L;
    private static final Long NEW_VERSION = 2L;

    private final UserSegmentsDao userSegmentsDao = mock(UserSegmentsDao.class);
    private final SegmentsMinValidVersionProvider segmentsMinValidVersionProvider = mock(SegmentsMinValidVersionProvider.class);
    private final YdbTransactionManager ydbTransactionManager = new YdbTransactionManagerStub();

    private final UserSegmentsService userSegmentsService = new UserSegmentsService(userSegmentsDao, segmentsMinValidVersionProvider, ydbTransactionManager, Optional.empty(), Optional.of(3));

    private final EvaluationSnaphotDao evaluationSnaphotDao = mock(EvaluationSnaphotDao.class);
    private final LogbrokerWriterStub<BigbPayload> changedUserSegmentsDownstream = new LogbrokerWriterStub<>();

    private final DiffService service = new DiffService(evaluationSnaphotDao, userSegmentsService, changedUserSegmentsDownstream);

    @Before
    public void init() {
        changedUserSegmentsDownstream.clear();
    }

    @Test
    public void addedUserWithStateToSegment() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1, USER_ID_2);

        Long2LongLinkedOpenHashMap segmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2}, new long[]{OLD_VERSION});
        UserSegments userSegments = new UserSegments(USER_ID_2, segmentsMap, 1L);
        Long2LongLinkedOpenHashMap expectedSegmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2, SEGMENT_ID_1}, new long[]{OLD_VERSION, NEW_VERSION});
        UserSegments expected = new UserSegments(USER_ID_2, expectedSegmentsMap, 2L);

        checkTestCase(prevIteration, lastIteration, List.of(USER_ID_2), List.of(userSegments), List.of(expected));
    }

    @Test
    public void addedUserWithoutStateToSegment() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1, USER_ID_2);
        Long2LongLinkedOpenHashMap expectedSegmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_1}, new long[]{NEW_VERSION});
        UserSegments expected = new UserSegments(USER_ID_2, expectedSegmentsMap, 1L);

        checkTestCase(prevIteration, lastIteration,  List.of(USER_ID_2), List.of(), List.of(expected));
    }

    @Test
    public void addedUserWithThisSegmentInState() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1, USER_ID_2);
        Long2LongLinkedOpenHashMap segmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_1}, new long[]{OLD_VERSION});
        UserSegments userSegments = new UserSegments(USER_ID_2, segmentsMap, 1L);
        UserSegments expected = new UserSegments(USER_ID_2, segmentsMap, 2L);

        checkTestCase(prevIteration, lastIteration, List.of(USER_ID_2), List.of(userSegments), List.of(expected));
    }

    @Test
    public void removedUserWithStateFromSegment() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1, USER_ID_2);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1);
        Long2LongLinkedOpenHashMap segmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_1, SEGMENT_ID_2}, new long[]{OLD_VERSION, OLD_VERSION});
        UserSegments userSegments = new UserSegments(USER_ID_2, segmentsMap, 1L);
        Long2LongLinkedOpenHashMap expectedSegmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2}, new long[]{OLD_VERSION});
        UserSegments expected = new UserSegments(USER_ID_2, expectedSegmentsMap, 2L);

        checkTestCase(prevIteration, lastIteration, List.of(USER_ID_2), List.of(userSegments), List.of(expected));
    }

    @Test
    public void removedUserWithoutThisSegmentInState() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1, USER_ID_2);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1);
        Long2LongLinkedOpenHashMap segmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2}, new long[]{OLD_VERSION});
        UserSegments userSegments = new UserSegments(USER_ID_2, segmentsMap, 1L);
        UserSegments expected = new UserSegments(USER_ID_2, segmentsMap, 2L);

        checkTestCase(prevIteration, lastIteration, List.of(USER_ID_2), List.of(userSegments), List.of(expected));
    }

    @Test
    public void removedUserWithoutStateFromSegment() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1, USER_ID_2);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1);
        UserSegments expected = new UserSegments(USER_ID_2, new Long2LongLinkedOpenHashMap(), 1L);

        checkTestCase(prevIteration, lastIteration, List.of(USER_ID_2), List.of(), List.of(expected));
    }

    @Test
    public void limitingSegmentsCount() {
        CloseableIterable<Long> prevIteration = makeClosable(USER_ID_1);
        CloseableIterable<Long> lastIteration = makeClosable(USER_ID_1, USER_ID_2);
        Long2LongLinkedOpenHashMap segmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2, SEGMENT_ID_3, SEGMENT_ID_4}, new long[]{OLD_VERSION, OLD_VERSION, OLD_VERSION});
        UserSegments userSegments = new UserSegments(USER_ID_2, segmentsMap, 1L);
        Long2LongLinkedOpenHashMap expectedSegmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_3, SEGMENT_ID_4, SEGMENT_ID_1}, new long[]{OLD_VERSION, OLD_VERSION, NEW_VERSION});
        UserSegments expected = new UserSegments(USER_ID_2, expectedSegmentsMap, 2L);

        checkTestCase(prevIteration, lastIteration, List.of(USER_ID_2), List.of(userSegments), List.of(expected));
    }

    @Test
    public void compareUnsignedLong() {
        // тут парсятся значения для того чтобы проверить как воспримет DiffIterator unsigned long-значения больше 2^63 - 1
        long first = Long.parseUnsignedLong("9026766571550328479");
        long second = Long.parseUnsignedLong("9368411141562928859");

        CloseableIterable<Long> prevIteration = makeClosable(first);
        CloseableIterable<Long> lastIteration = makeClosable(first, second);

        Long2LongLinkedOpenHashMap segmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2}, new long[]{OLD_VERSION});
        UserSegments userSegments = new UserSegments(second, segmentsMap, 1L);
        Long2LongLinkedOpenHashMap expectedSegmentsMap = new Long2LongLinkedOpenHashMap(new long[]{SEGMENT_ID_2, SEGMENT_ID_1}, new long[]{OLD_VERSION, NEW_VERSION});
        UserSegments expected = new UserSegments(second, expectedSegmentsMap, 2L);

        checkTestCase(prevIteration, lastIteration, List.of(second), List.of(userSegments), List.of(expected));
    }

    @Test
    public void cleanUpByMinValidVersion() {

    }

    private void checkTestCase(CloseableIterable<Long> prevIteration, CloseableIterable<Long> lastIteration, List<Long> changedUserIds, List<UserSegments> states, List<UserSegments> statesToSave) {
        when(evaluationSnaphotDao.getIterableBySegmentAndVersion(SEGMENT_ID_1, OLD_VERSION))
                .thenReturn(prevIteration);
        when(evaluationSnaphotDao.getIterableBySegmentAndVersion(SEGMENT_ID_1, NEW_VERSION))
                .thenReturn(lastIteration);

        when(userSegmentsDao.getAsync(eq(changedUserIds), any()))
                .thenReturn(CompletableFuture.completedFuture(states));
        when(userSegmentsDao.saveAsync(any(), any()))
                .thenReturn(CompletableFuture.completedFuture(null));

        when(segmentsMinValidVersionProvider.getMinVersionsAsync(any(), any()))
                .thenReturn(CompletableFuture.completedFuture(new Long2LongOpenHashMap()));

        service.processDiff(SEGMENT_ID_1, NEW_VERSION, OLD_VERSION);

        verify(evaluationSnaphotDao).getIterableBySegmentAndVersion(SEGMENT_ID_1, OLD_VERSION);
        verify(evaluationSnaphotDao).getIterableBySegmentAndVersion(SEGMENT_ID_1, NEW_VERSION);
        verify(userSegmentsDao).getAsync(eq(changedUserIds), any());

        verify(userSegmentsDao).saveAsync(eq(statesToSave), any());

        List<BigbPayload> gotBigbPayloads = changedUserSegmentsDownstream.getMessages();

        Assert.equals(statesToSave.size(), gotBigbPayloads.size());

        for (int i = 0; i < statesToSave.size(); i++) {
            UserSegments state = statesToSave.get(i);
            BigbPayload payload = gotBigbPayloads.get(i);

            Assert.equals(state.getUserId(), payload.getYandexuid());
            Set<Long> expectedPayloadSegments = state.getSegments().keySet().stream()
                    .map(segment_id -> RetargetingId.getSourceId(RetargetingType.cdp_segment, segment_id))
                    .collect(Collectors.toSet());
            Assert.equals(expectedPayloadSegments, payload.getSegments());
        }
    }

    @SafeVarargs
    private static <T> CloseableIterable<T> makeClosable(T... elements) {
        var iterator = CloseableIterator.wrap(Arrays.asList(elements).iterator());
        return CloseableIterable.from(iterator);
    }
}
