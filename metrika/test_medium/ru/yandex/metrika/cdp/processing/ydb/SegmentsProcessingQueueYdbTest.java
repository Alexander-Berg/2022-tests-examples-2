package ru.yandex.metrika.cdp.processing.ydb;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Random;
import java.util.function.Consumer;
import java.util.stream.LongStream;

import com.yandex.ydb.table.query.Params;
import com.yandex.ydb.table.transaction.TxControl;
import com.yandex.ydb.table.values.PrimitiveValue;
import it.unimi.dsi.fastutil.longs.Long2LongLinkedOpenHashMap;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.processing.queue.SegmentsQueueItem;
import ru.yandex.metrika.cdp.processing.queue.SegmentsQueueItem.AwaitingStage;
import ru.yandex.metrika.cdp.processing.queue.SegmentsQueueItem.FinalStage;
import ru.yandex.metrika.cdp.processing.queue.SegmentsQueueItem.ProcessingStage;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManager;
import ru.yandex.metrika.util.collections.Try;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.cdp.processing.queue.SegmentsQueueItem.InactiveStage;
import static ru.yandex.metrika.cdp.processing.ydb.SegmentsProcessingQueueYdb.SEGMENTS_QUEUE_ITEM_TABLE_META;
import static ru.yandex.metrika.cdp.processing.ydb.SegmentsProcessingQueueYdb.SEGMENTS_QUEUE_TABLE_NAME;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class SegmentsProcessingQueueYdbTest {

    private static final String SEGMENTS_DATA_FOLDER = "segments_data";
    private static final String SEGMENTS_QUEUE_TABLE_PREFIX = EnvironmentHelper.ydbDatabase + "/" + SEGMENTS_DATA_FOLDER;
    private static final String SEGMENTS_QUEUE_TABLE_PATH = SEGMENTS_QUEUE_TABLE_PREFIX + "/" + SEGMENTS_QUEUE_TABLE_NAME;

    @BeforeClass
    public static void beforeClass() {
        YdbSetupUtil.setupYdbFolders(SEGMENTS_DATA_FOLDER);
    }

    @Autowired
    private SegmentsProcessingQueueYdb queue;

    @Autowired
    private YdbTemplate ydbTemplate;

    @Autowired
    private YdbTransactionManager ydbTransactionManager;

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(SEGMENTS_QUEUE_TABLE_PATH);
    }

    @Test
    public void testAddItem() {
        long segmentId = 1L;
        queue.addNewItem(segmentId);

        var itemO = getItem(segmentId);
        assertTrue(itemO.isPresent());

        var item = itemO.get();
        assertEquals(item.getStage(), AwaitingStage.AWAITING_EVALUATION);
        assertEquals(item.getPriority(), 0);
        assertEquals(item.getEvaluationVersion(), 0);
        assertEquals(item.getDiffVersion(), 0);
    }

    @Test
    public void testEvaluationProcess() {
        var item = new SegmentsQueueItem(1L);
        addItemToQueue(item);

        var testConsumer = new TestConsumer<SegmentsQueueItem>();
        var processed = queue.evaluateNextItem(testConsumer);
        assertTrue(processed);
        assertNotNull(testConsumer.reference);
        assertEquals(testConsumer.reference.getSegmentId(), item.getSegmentId());

        var itemFromQueueO = getItem(item.getSegmentId());
        assertTrue(itemFromQueueO.isPresent());

        var itemFromQueue = itemFromQueueO.get();
        assertEquals(itemFromQueue.getStage(), AwaitingStage.AWAITING_DIFF);
        assertThat(itemFromQueue.getEvaluationVersion(), greaterThan(item.getEvaluationVersion()));
    }

    @Test
    public void testDiffProcess() {
        var item = new SegmentsQueueItem(1L);
        AwaitingStage.AWAITING_EVALUATION.updateBeforeProcessing(item, Duration.ofMinutes(5));
        ProcessingStage.EVALUATION.updateAfterProcessingSuccess(item); // AWAITING_DIFF
        addItemToQueue(item);

        var testConsumer = new TestConsumer<SegmentsQueueItem>();
        var processed = queue.diffNextItem(testConsumer);
        assertTrue(processed);
        assertNotNull(testConsumer.reference);
        assertEquals(testConsumer.reference.getSegmentId(), item.getSegmentId());

        var itemFromQueueO = getItem(item.getSegmentId());
        assertTrue(itemFromQueueO.isPresent());

        var itemFromQueue = itemFromQueueO.get();
        assertEquals(itemFromQueue.getStage(), FinalStage.FINISH);
        assertNotNull(itemFromQueue.getProcessingFinish());
        assertEquals(itemFromQueue.getDiffVersion(), item.getEvaluationVersion());
    }

    @Test
    public void testPriority() {
        var item1 = new SegmentsQueueItem(1L);
        var item2 = new SegmentsQueueItem(2L);

        item1.setPriority(2L);
        item2.setPriority(1L); // smaller number - higher priority

        addItemToQueue(item1);
        addItemToQueue(item2);

        var testConsumer = new TestConsumer<SegmentsQueueItem>();
        var processed = queue.evaluateNextItem(testConsumer);
        assertTrue(processed);
        assertNotNull(testConsumer.reference);
        assertEquals(testConsumer.reference.getSegmentId(), item2.getSegmentId());
    }

    @Test
    public void testDiedInProgress() {
        var item = new SegmentsQueueItem(1L);
        AwaitingStage.AWAITING_EVALUATION.updateBeforeProcessing(item, Duration.ofMinutes(5));
        item.setLastHeartbeat(Instant.now().minus(Duration.ofMinutes(6))); // time is out
        addItemToQueue(item);

        var testConsumer = new TestConsumer<SegmentsQueueItem>();
        var processed = queue.evaluateNextItem(testConsumer);
        assertTrue(processed);
        assertNotNull(testConsumer.reference);
        assertEquals(testConsumer.reference.getSegmentId(), item.getSegmentId());

        var itemFromQueueO = getItem(item.getSegmentId());
        assertTrue(itemFromQueueO.isPresent());

        var itemFromQueue = itemFromQueueO.get();
        assertEquals(itemFromQueue.getStage(), AwaitingStage.AWAITING_DIFF);
        assertThat(itemFromQueue.getEvaluationVersion(), greaterThan(item.getEvaluationVersion()));
    }

    @Test
    public void testEvaluationFailure() {
        var item = new SegmentsQueueItem(1L);
        addItemToQueue(item);

        var testConsumerShouldFail = new TestConsumer<SegmentsQueueItem>(true);
        var evaluationTry = Try.of(() -> queue.evaluateNextItem(testConsumerShouldFail));
        assertTrue(evaluationTry.isFailure());

        var itemFromQueueO = getItem(item.getSegmentId());
        assertTrue(itemFromQueueO.isPresent());

        var itemFromQueue = itemFromQueueO.get();
        assertEquals(itemFromQueue.getStage(), AwaitingStage.AWAITING_EVALUATION);
        assertThat(itemFromQueue.getEvaluationVersion(), greaterThan(item.getEvaluationVersion()));
    }

    @Test
    public void testSendFinishedToProcess() {
        var ids = LongStream.range(1L, 11L).boxed().collect(toList());
        ids.forEach(id -> {
            var finishedItem = getFinishedItem(id);
            makeItemOld(finishedItem, 25);
            addItemToQueue(finishedItem);
        });

        queue.sendFinishedToProcessing();

        ids.forEach(id -> {
            var itemFromQueueO = getItem(id);
            assertTrue(itemFromQueueO.isPresent());

            var itemFromQueue = itemFromQueueO.get();
            assertEquals(itemFromQueue.getStage(), AwaitingStage.AWAITING_EVALUATION);
        });
    }

    private void makeItemOld(SegmentsQueueItem finishedItem, int hours) {
        finishedItem.setProcessingStart(
                finishedItem.getProcessingStart().minus(Duration.ofHours(hours))
        );
        finishedItem.setProcessingFinish(
                Objects.requireNonNull(finishedItem.getProcessingFinish())
                        .minus(Duration.ofHours(hours))
        );
    }

    @Test
    public void testTryToSendJustFinishedToProcess() {
        var ids = LongStream.range(1L, 11L).boxed().collect(toList());
        ids.forEach(id -> {
            var finishedItem = getFinishedItem(id);
            addItemToQueue(finishedItem);
        });

        queue.sendFinishedToProcessing();

        ids.forEach(id -> {
            var itemFromQueueO = getItem(id);
            assertTrue(itemFromQueueO.isPresent());

            var itemFromQueue = itemFromQueueO.get();
            assertEquals(itemFromQueue.getStage(), FinalStage.FINISH);
        });
    }

    @Test
    public void testDisableSegments() {
        var ids = LongStream.range(1L, 11L).boxed().collect(toList());
        ids.forEach(id -> {
            var finishedItem = getFinishedItem(id);
            addItemToQueue(finishedItem);
        });

        queue.disableItems(ids);

        ids.forEach(id -> {
            var itemFromQueueO = getItem(id);
            assertTrue(itemFromQueueO.isPresent());

            var itemFromQueue = itemFromQueueO.get();
            assertEquals(itemFromQueue.getStage(), InactiveStage.DISABLED);
        });
    }

    @Test
    public void testReenableSegments() {
        var ids = LongStream.range(1L, 11L).boxed().collect(toList());
        ids.forEach(id -> {
            var finishedItem = getFinishedItem(id);
            FinalStage.FINISH.updateOnDisable(finishedItem);
            addItemToQueue(finishedItem);
        });

        queue.sendDisabledToProcessing(ids);

        ids.forEach(id -> {
            var itemFromQueueO = getItem(id);
            assertTrue(itemFromQueueO.isPresent());

            var itemFromQueue = itemFromQueueO.get();
            assertEquals(itemFromQueue.getStage(), AwaitingStage.AWAITING_EVALUATION);
        });
    }

    @Test
    public void testGetMinValidVersions() {
        var item = new SegmentsQueueItem(1L);

        int minValidVersion = 10;
        item.setMinValidVersion(minValidVersion);

        addItemToQueue(item);

        var result = queue.getMinVersionsAsync(List.of(1L), QueryExecutionContext.read()).join();

        assertEquals(1, result.size());
        assertTrue(result.containsKey(item.getSegmentId()));
        assertEquals(minValidVersion, result.get(item.getSegmentId()));

    }

    @Test
    public void testGetManyMinValidVersionsInTransaction() {
        var random = new Random();
        var expectedMinValidVersions = new Long2LongLinkedOpenHashMap();
        var items = LongStream.range(1, 2500).mapToObj(segmentId -> {
            var item = new SegmentsQueueItem(segmentId);

            int minValidVersion = random.nextInt(10);
            item.setMinValidVersion(minValidVersion);

            expectedMinValidVersions.put(segmentId, minValidVersion);

            return item;
        }).collect(toList());

        addItemsToQueue(items);


        var result = ydbTransactionManager.inTransactionHandled(
                executionContext -> queue.getMinVersionsAsync(List.copyOf(expectedMinValidVersions.keySet()), executionContext)
        ).join();

        assertEquals(expectedMinValidVersions, result);
    }

    private void addItemToQueue(SegmentsQueueItem item) {
        addItemsToQueue(List.of(item));
    }

    private void addItemsToQueue(List<SegmentsQueueItem> items) {
        ydbTemplate.execute(
                "PRAGMA TablePathPrefix = \"" + SEGMENTS_QUEUE_TABLE_PREFIX + "\";\n" +
                        "DECLARE $segments AS " + SEGMENTS_QUEUE_ITEM_TABLE_META.getFullStructListType() + ";\n" +
                        "\n" +
                        "REPLACE INTO " + SEGMENTS_QUEUE_TABLE_NAME + "\n" +
                        "SELECT\n" +
                        "    " + SEGMENTS_QUEUE_ITEM_TABLE_META.getColumnNamesJoined() + "\n" +
                        "FROM AS_TABLE($segments);",
                Params.of("$segments", SEGMENTS_QUEUE_ITEM_TABLE_META.listValue(items)),
                TxControl.serializableRw()
        );
    }

    private Optional<SegmentsQueueItem> getItem(long segmentId) {
        return ydbTemplate.queryObject(
                "PRAGMA TablePathPrefix = \"" + SEGMENTS_QUEUE_TABLE_PREFIX + "\";\n" +
                        "DECLARE $segment_id AS Uint64;\n" +
                        "\n" +
                        "SELECT\n" +
                        "    " + SEGMENTS_QUEUE_ITEM_TABLE_META.getColumnNamesJoined() + "\n" +
                        "FROM " + SEGMENTS_QUEUE_TABLE_NAME + "\n" +
                        "WHERE segment_id = $segment_id;",
                Params.of("$segment_id", PrimitiveValue.uint64(segmentId)),
                SegmentsProcessingQueueYdb.ROW_MAPPER
        );
    }

    private static SegmentsQueueItem getFinishedItem(long segmentId) {
        var item = new SegmentsQueueItem(segmentId);
        AwaitingStage.AWAITING_EVALUATION.updateBeforeProcessing(item, Duration.ofMinutes(1));
        ProcessingStage.EVALUATION.updateAfterProcessingSuccess(item);
        AwaitingStage.AWAITING_DIFF.updateBeforeProcessing(item, Duration.ofMinutes(1));
        ProcessingStage.DIFF.updateAfterProcessingSuccess(item);
        return item;
    }

    private static class TestConsumer<T> implements Consumer<T> {
        private final boolean shouldFail;
        public T reference;

        private TestConsumer() {
            shouldFail = false;
        }

        public TestConsumer(boolean shouldFail) {
            this.shouldFail = shouldFail;
        }

        @Override
        public void accept(T t) {
            reference = t;
            if (shouldFail) {
                throw new RuntimeException("This was on purpose");
            }
        }
    }


    @Configuration
    @Import(YdbConfig.class)
    static class Config {

        @Bean
        public SegmentsProcessingQueueYdb segmentsProcessingQueueYdb(YdbTemplate ydbTemplate, YdbTransactionManager ydbTransactionManager) {
            return new SegmentsProcessingQueueYdb(ydbTemplate, ydbTransactionManager, SEGMENTS_QUEUE_TABLE_PREFIX, Optional.empty());
        }

    }

}
