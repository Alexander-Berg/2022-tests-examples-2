package ru.yandex.metrika.remarketingd.process;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import com.google.common.collect.ImmutableMap;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.logging.log4j.Level;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.mockito.hamcrest.MockitoHamcrest;

import ru.yandex.metrika.api.constructor.contr.CounterBignessService;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentRetargeting;
import ru.yandex.metrika.api.management.client.segments.SegmentSource;
import ru.yandex.metrika.api.management.client.segments.SegmentStatus;
import ru.yandex.metrika.api.management.client.segments.streamabillity.StreamabilityClass;
import ru.yandex.metrika.remarketingd.RemarketingdSettings;
import ru.yandex.metrika.remarketingd.entity.SegmentVisit;
import ru.yandex.metrika.remarketingd.entity.Visit;
import ru.yandex.metrika.remarketingd.export.BSExporter;
import ru.yandex.metrika.remarketingd.export.ExportChunk;
import ru.yandex.metrika.remarketingd.export.UserSegment;
import ru.yandex.metrika.remarketingd.storage.HashMapBSStateStorage;
import ru.yandex.metrika.retargeting.CollectorSegmentData;
import ru.yandex.metrika.retargeting.SegmentProvider;
import ru.yandex.metrika.retargeting.SegmentsUpdate;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.anyList;
import static org.mockito.Matchers.anyMap;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.any;
import static org.mockito.Mockito.anyInt;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

/**
 * User: hamilkar
 * Date: 26.02.15
 * Time: 18:29
 */
public class SegmentProcessorTest {

    private SegmentProcessor<String> segmentProcessor;
    private Set<CollectorSegmentData> collector;   // ага, это БК
    private VisitsProvider visitsProvider;
    private HashMapBSStateStorage bsStateStorage;
    private SegmentProvider segmentProvider;
    private CounterBignessService counterBignessService;
    private int currentTime;
    private int shard = 1;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);

        collector = new HashSet<>();
        BSExporter bsExporter = mock(BSExporter.class);
        doAnswer(x -> {
            ExportChunk chunk = (ExportChunk) x.getArguments()[0];
            collector.removeAll(chunk.getToDelete());
            collector.addAll(chunk.getToAdd());
            return null;
        }).when(bsExporter).exportToCollector(any(), anyMap());

        visitsProvider = mock(VisitsProvider.class);
        segmentProvider = mock(SegmentProvider.class);
        bsStateStorage = spy(HashMapBSStateStorage.class);
        counterBignessService = mock(CounterBignessService.class);

        bsStateStorage.setCounterBignessService(counterBignessService);

        segmentProcessor = spy(new SegmentProcessor<>());
        segmentProcessor.setExporter(bsExporter);
        segmentProcessor.setStateStorage(bsStateStorage);
        segmentProcessor.setVisitsProvider(visitsProvider);
        segmentProcessor.setSegmentProvider(segmentProvider);
        segmentProcessor.setThisProxy(segmentProcessor);
        segmentProcessor.setSettings(new RemarketingdSettings());
        segmentProcessor.setCounterBignessService(counterBignessService);
        segmentProcessor.setStreamableClasses(new HashSet<>());
        currentTime = (int) (System.currentTimeMillis() / 1000);
    }


    /** По сегменту 0 визитов -> 1 визит */
    @Test
    public void test1() {
        SegmentVisit segmentVisit = create(1, 1, 1, currentTime);
        CollectorSegmentData bsSegment = bsSegment(segmentVisit);
        Segment segment = new Segment(1, 1, "segment 1", "expression");

        when(visitsProvider.getAllVisitsForSmall(contains(segment), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.singletonList(segmentVisit), Collections.emptyList()));
        when(visitsProvider.getAllVisitsForSmall(notContains(segment), anyInt(), eq(shard)))
                .thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(empty(), anyInt(), eq(shard))).thenReturn(Collections.emptyList());
        when(visitsProvider.getGoodVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), Collections.singletonList(segment), ""));

        segmentProcessor.run(shard);

        assertEquals(1, collector.size());
        assertTrue(collector.contains(bsSegment));
        assertEquals(1, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit));
    }


    /** По сегменту 1 визитов -> 0 визитов */
    @Test
    public void test2() {
        SegmentVisit segmentVisit = new SegmentVisit(1, false, 1, 1, 1, currentTime, 0, 0);
        CollectorSegmentData bsSegment = bsSegment(segmentVisit);
        Segment segment = new Segment(1, 1, "segment 1", "expression");
        collector.add(bsSegment);
        add(segmentVisit);

        when(visitsProvider.getAllVisitsForSmall(contains(segment), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.emptyList(), Collections.singletonList(segmentVisit)));
        when(visitsProvider.getAllVisitsForSmall(notContains(segment), anyInt(), eq(shard)))
                .thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(empty(), anyInt(), eq(shard))).thenReturn(Collections.emptyList());
        when(visitsProvider.getGoodVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        Mockito.doNothing().when(bsStateStorage).reload(anyInt(), anyList());
        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), Collections.singletonList(segment), ""));

        segmentProcessor.run(shard);

        assertTrue(collector.isEmpty());
        assertTrue(bsStateStorage.isEmpty());
    }


    /** По сегменту 1 визит -> 2 визита (должно измениться время) */
    @Test
    public void test3() {
        SegmentVisit segmentVisit1 = create(1,1, 1, currentTime);
        SegmentVisit segmentVisit2 = create(1, 1, 2, currentTime - 1);
        CollectorSegmentData bsSegment1 = bsSegment(segmentVisit1);
        CollectorSegmentData bsSegment2 = bsSegment(segmentVisit2);
        Segment segment = new Segment(1, 1, "segment 1", "expression");
        collector.add(bsSegment1);
        add(segmentVisit1);

        when(visitsProvider.getAllVisitsForSmall(contains(segment), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Arrays.asList(segmentVisit1, segmentVisit2), Collections.emptyList()));
        when(visitsProvider.getAllVisitsForSmall(notContains(segment), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(empty(), anyInt(), eq(shard))).thenReturn(Collections.emptyList());
        when(visitsProvider.getGoodVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), Collections.singletonList(segment), ""));

        segmentProcessor.run(shard);

        assertEquals(1, collector.size());
        assertTrue(collector.contains(bsSegment2));
        assertEquals(2, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit2));
        assertTrue(bsStateStorage.contains(segmentVisit1));
    }


    /** По сегменту 1 визит -> 1 визит, но другой */
    @Test
    public void test4() {
        SegmentVisit segmentVisit1 = create(1, 1, 1, currentTime);
        SegmentVisit segmentVisit2 = create(1, 1, 2, currentTime - 1);
        CollectorSegmentData bsSegment1 = bsSegment(segmentVisit1);
        CollectorSegmentData bsSegment2 = bsSegment(segmentVisit2);
        Segment segment = new Segment(1, 1, "segment 1", "expression");
        collector.add(bsSegment1);
        add(segmentVisit1);

        when(visitsProvider.getAllVisitsForSmall(contains(segment), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.singletonList(segmentVisit2), Collections.singletonList(segmentVisit1)));
        when(visitsProvider.getAllVisitsForSmall(notContains(segment), anyInt(), eq(shard)))
                .thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(empty(), anyInt(), eq(shard))).thenReturn(Collections.emptyList());
        when(visitsProvider.getGoodVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), Collections.singletonList(segment),  ""));

        segmentProcessor.run(shard);

        assertEquals(1, collector.size());
        assertTrue(collector.contains(bsSegment2));
        assertEquals(1, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit2));
    }


    /** По сегменту 2 визита -> 1 визит (более старый, т.е. новый удалился) */
    @Test
    public void test5() {
        SegmentVisit segmentVisit1 = create(1, 1, 1, currentTime);
        SegmentVisit segmentVisit2 = create(1, 1, 2, currentTime - 1);
        CollectorSegmentData bsSegment1 = bsSegment(segmentVisit1);
        CollectorSegmentData bsSegment2 = bsSegment(segmentVisit2);
        Segment segment = new Segment(1, 1, "segment 1", "expression");
        collector.add(bsSegment2);
        add(segmentVisit1, segmentVisit2);

        when(visitsProvider.getAllVisitsForSmall(contains(segment), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.singletonList(segmentVisit1), Collections.singletonList(segmentVisit2)));
        when(visitsProvider.getAllVisitsForSmall(notContains(segment), anyInt(), eq(shard)))
                .thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(empty(), anyInt(), eq(shard))).thenReturn(Collections.emptyList());
        when(visitsProvider.getGoodVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), Collections.singletonList(segment), ""));

        segmentProcessor.run(shard);

        assertEquals(1, collector.size());
        assertTrue(collector.contains(bsSegment1));
        assertEquals(1, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit1));
    }


    /** Появление сегмента */
    @Test
    public void test6() {
        SegmentVisit segmentVisit = create(1, 1, 1, currentTime);
        CollectorSegmentData bsSegment = bsSegment(segmentVisit);
        Segment segment = new Segment(1, 1, "segment 1", "expression");

        when(visitsProvider.getAllVisitsForSmall(empty(), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.emptyList(), Collections.emptyList()));
        when(visitsProvider.getAllVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(contains(segment), anyInt(), eq(shard))).thenReturn(Collections.singletonList(segmentVisit));
        when(visitsProvider.getGoodVisitsForSmall(notContains(segment), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.singletonList(segment), Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), ""));

        segmentProcessor.run(shard);

        assertEquals(1, collector.size());
        assertTrue(collector.contains(bsSegment));
        assertEquals(1, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit));
    }


    /** Изменение сегмента */
    @Test
    public void test7() {
        SegmentVisit segmentVisit = create(1, 1, 1, currentTime);
        CollectorSegmentData bsSegment = bsSegment(segmentVisit);
        Segment segment = new Segment(1, 1, "segment 1", "expression");
        collector.add(bsSegment);
        add(segmentVisit);

        when(visitsProvider.getAllVisitsForSmall(empty(), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.emptyList(), Collections.emptyList()));
        when(visitsProvider.getAllVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(contains(segment), anyInt(), eq(shard))).thenReturn(Collections.singletonList(segmentVisit));
        when(visitsProvider.getGoodVisitsForSmall(notContains(segment), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.singletonList(segment), Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), ""));

        segmentProcessor.run(shard);

        assertEquals(1, collector.size());
        assertTrue(collector.contains(bsSegment));
        assertEquals(1, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit));
    }


    /** Удаление сегмента */
    @Test
    public void test8() {
        SegmentVisit segmentVisit = create(1, 1, 1, currentTime);
        CollectorSegmentData bsSegment = bsSegment(segmentVisit);
        Segment segment = new Segment(1, 1, "segment 1", "expression", 1, 123L, true, SegmentStatus.active, SegmentSource.API, SegmentRetargeting.ALLOW, StreamabilityClass.NOT_STREAMABLE);
        collector.add(bsSegment);
        add(segmentVisit);

        when(visitsProvider.getAllVisitsForSmall(empty(), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.emptyList(), Collections.emptyList()));
        when(visitsProvider.getAllVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(empty(), anyInt(), eq(shard))).thenReturn(Collections.emptyList());
        when(visitsProvider.getGoodVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        Mockito.doNothing().when(bsStateStorage).reload(anyInt(), anyList());
        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Collections.emptyList(), Collections.singletonList(segment), Collections.emptyList(), Collections.emptyList(), ""));

        segmentProcessor.run(shard);

        assertTrue(collector.isEmpty());
        assertTrue(bsStateStorage.isEmpty());
    }


    /** Появление двух сегментов, 1 визит подходит под оба */
    @Test
    public void test9() {
        SegmentVisit segmentVisit1 = create(1, 1, 1, currentTime);
        SegmentVisit segmentVisit2 = create(2, 1, 1, currentTime);
        CollectorSegmentData bsSegment1 = bsSegment(segmentVisit1);
        CollectorSegmentData bsSegment2 = bsSegment(segmentVisit2);
        Segment segment1 = new Segment(1, 1, "segment 1", "expression");
        Segment segment2 = new Segment(2, 1, "segment 2", "expression");

        when(visitsProvider.getAllVisitsForSmall(empty(), anyInt(), eq(shard)))
                .thenReturn(Pair.of(Collections.emptyList(), Collections.emptyList()));
        when(visitsProvider.getAllVisitsForSmall(notEmpty(), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(visitsProvider.getGoodVisitsForSmall(contains(segment1, segment2), anyInt(), eq(shard)))
                .thenReturn(Arrays.asList(segmentVisit1, segmentVisit2));
        when(visitsProvider.getGoodVisitsForSmall(contains(segment1), anyInt(), eq(shard)))
                .thenReturn(Collections.singletonList(segmentVisit1));
        when(visitsProvider.getGoodVisitsForSmall(contains(segment2), anyInt(), eq(shard)))
                .thenReturn(Collections.singletonList(segmentVisit2));
        when(visitsProvider.getGoodVisitsForSmall(notContains(segment1, segment2), anyInt(), eq(shard))).thenThrow(new RuntimeException());

        when(segmentProvider.next(shard)).thenReturn(
                new SegmentsUpdate<>(Arrays.asList(segment1, segment2), Collections.emptyList(), Collections.emptyList(), Collections.emptyList(), ""));

        segmentProcessor.run(shard);

        assertEquals(2, collector.size());
        assertTrue(collector.contains(bsSegment1));
        assertTrue(collector.contains(bsSegment2));
        assertEquals(2, bsStateStorage.size(shard));
        assertTrue(bsStateStorage.contains(segmentVisit1));
        assertTrue(bsStateStorage.contains(segmentVisit2));
    }

    private SegmentVisit create(int segmentId, long userId, long visitId, int timestamp) {
        return new SegmentVisit(segmentId, true, 1, userId, visitId, timestamp, 0, 0);
    }


    private void add(SegmentVisit segmentVisit) {
        bsStateStorage.addSegments(ImmutableMap.of(UserSegment.create(segmentVisit.getUserID(), segmentVisit.getSegmentID(), false, 1, 0),
                Collections.singletonList(new Visit(segmentVisit.getVisitID(), segmentVisit.getVisitStartTime(), segmentVisit.getVisitVersion()))), shard);
    }

    private void add(SegmentVisit segmentVisit1, SegmentVisit segmentVisit2) {
        if (segmentVisit1.getSegmentID() != segmentVisit2.getSegmentID() ||
                segmentVisit1.getUserID() != segmentVisit2.getUserID()) {
            add(segmentVisit1);
            add(segmentVisit2);
        } else {
            bsStateStorage.addSegments(ImmutableMap.of(UserSegment.create(segmentVisit1.getUserID(), segmentVisit1.getSegmentID(), false, 1, 0),
                    Arrays.asList(
                            new Visit(segmentVisit1.getVisitID(), segmentVisit1.getVisitStartTime(), segmentVisit1.getVisitVersion()),
                            new Visit(segmentVisit2.getVisitID(), segmentVisit2.getVisitStartTime(), segmentVisit2.getVisitVersion())
                    )
            ), shard);
        }
    }

    public static <T> Collection<T> notContains(T... elements) {
        return MockitoHamcrest.argThat(new BaseMatcher<Collection<T>>() {

            @Override
            public void describeTo(Description description) {
                description.appendText("collection contains one of: " + Arrays.toString(elements));
            }

            @Override
            public boolean matches(Object collection) {
                if (collection == null) {
                    return true;
                }
                for (T element : elements) {
                    if (((Collection) collection).contains(element)) {
                        return false;
                    }
                }
                return true;
            }
        });
    }

    public static <T> Collection<T> contains(T... elements) {
        return MockitoHamcrest.argThat(new BaseMatcher<Collection<T>>() {

            @Override
            public void describeTo(Description description) {
                description.appendText("collection doesn't contains one of: " + Arrays.toString(elements));
            }

            @Override
            public boolean matches(Object collection) {
                if (collection == null) {
                    return false;
                }
                for (T element : elements) {
                    if (!((Collection) collection).contains(element)) {
                        return false;
                    }
                }
                return true;
            }
        });
    }

    public static <T> Collection<T> empty() {
        return MockitoHamcrest.argThat(new BaseMatcher<Collection<T>>() {

            @Override
            public void describeTo(Description description) {
                description.appendText("collection is not empty");
            }

            @Override
            public boolean matches(Object collection) {
                return collection == null || ((Collection) collection).isEmpty();
            }
        });
    }

    public static <T> Collection<T> notEmpty() {
        return MockitoHamcrest.argThat(new BaseMatcher<Collection<T>>() {

            @Override
            public void describeTo(Description description) {
                description.appendText("collection is empty");
            }

            @Override
            public boolean matches(Object collection) {
                return collection != null && !((Collection) collection).isEmpty();
            }
        });
    }

    private static CollectorSegmentData bsSegment(SegmentVisit segmentVisit) {
        return new CollectorSegmentData(segmentVisit.getVisitStartTime(), segmentVisit.getSegmentID(), segmentVisit.getUserID(), segmentVisit.getVisitID(), false, segmentVisit.getSegmentVersion(), segmentVisit.getVisitVersion());
    }
}
