package ru.yandex.metrika.cloud.formatter.common;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.function.Function;
import java.util.stream.Stream;

import javax.annotation.Nonnull;

import org.junit.Test;

import ru.yandex.kikimr.persqueue.consumer.StreamConsumer;
import ru.yandex.kikimr.persqueue.consumer.StreamListener;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageMeta;
import ru.yandex.metrika.cloud.formatter.common.util.FakeLbPool;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.serialization.protoseq.ProtoSeqBatchSerializer;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.concurrent.Pools;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.aMapWithSize;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.equalTo;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;
import static ru.yandex.kikimr.persqueue.compression.CompressionCodec.ZSTD;

public class ExactlyOnceLbTransferTest {

    static final BatchSerializer<Integer> INT_SERIALIZER = new ProtoSeqBatchSerializer<>(new ProtoSerializer<>() {

        @Nonnull
        @Override
        public Integer deserialize(ByteBuffer byteBuffer) {
            return byteBuffer.getInt();
        }

        @Override
        public byte[] serialize(Integer i) {
            return ByteBuffer.allocate(4).putInt(i).array();
        }
    });

    static final ExecutorService EXECUTOR = Pools.newNamedFixedThreadPool(10, "test-pool");

    @Test
    public void testMapWithoutParallelWithoutSharding() {
        FakeLbPool fakePool = new FakeLbPool();
        Function<Integer, Integer> mapFunction = i -> i * 7;
        ExactlyOnceLbTransfer<Integer, Integer> lbTransfer = new ExactlyOnceLbTransfer<>(
                fakePool,
                (i, meta) -> new ShardAddress(null, null),
                INT_SERIALIZER, INT_SERIALIZER,
                mapFunction,
                EXECUTOR
        );
        lbTransfer.setMapChunkSize(100000);
        var data = genInData(10, 10, 10);
        StreamConsumer mockedConsumer = createMockedConsumer(data);


        lbTransfer.startNewConsumer(mockedConsumer);


        List<Integer> actualData = fakePool.readFlatData(INT_SERIALIZER);

        assertThat(fakePool.getCache().size(), equalTo(1));


        List<Integer> originalFlatData = readFlatDataFromResponse(data);
        List<Integer> expectedDataList = F.map(originalFlatData, mapFunction);

        assertThat(actualData, containsInAnyOrder(expectedDataList.toArray()));
    }

    @Test
    public void testParallelMapWithoutSharding() {
        FakeLbPool fakePool = new FakeLbPool();
        Function<Integer, Integer> mapFunction = i -> i * 7;
        ExactlyOnceLbTransfer<Integer, Integer> lbTransfer = new ExactlyOnceLbTransfer<>(
                fakePool,
                (i, meta) -> new ShardAddress(null, null),
                INT_SERIALIZER, INT_SERIALIZER,
                mapFunction,
                EXECUTOR
        );
        lbTransfer.setMapChunkSize(1);
        var data = genInData(15, 15, 15);
        StreamConsumer mockedConsumer = createMockedConsumer(data);


        lbTransfer.startNewConsumer(mockedConsumer);


        List<Integer> actualData = fakePool.readFlatData(INT_SERIALIZER);

        assertThat(fakePool.getCache().size(), equalTo(1));


        List<Integer> originalFlatData = readFlatDataFromResponse(data);
        List<Integer> expectedDataList = F.map(originalFlatData, mapFunction);

        assertThat(actualData, containsInAnyOrder(expectedDataList.toArray()));
    }

    @Test
    public void testParallelMapWithSharding() {
        FakeLbPool fakePool = new FakeLbPool();
        Function<Integer, Integer> mapFunction = i -> i * 7;
        int shardNumber = 5;
        ExactlyOnceLbTransfer<Integer, Integer> lbTransfer = new ExactlyOnceLbTransfer<>(
                fakePool,
                (i, meta) -> new ShardAddress(null, i % shardNumber),
                INT_SERIALIZER, INT_SERIALIZER,
                mapFunction,
                EXECUTOR
        );
        lbTransfer.setMapChunkSize(3);
        var data = genInData(15, 15, 150);
        StreamConsumer mockedConsumer = createMockedConsumer(data);


        lbTransfer.startNewConsumer(mockedConsumer);


        List<Integer> actualData = fakePool.readFlatData(INT_SERIALIZER);

        assertThat(fakePool.getCache(), aMapWithSize(shardNumber));


        List<Integer> originalFlatData = readFlatDataFromResponse(data);
        List<Integer> expectedDataList = F.map(originalFlatData, mapFunction);

        assertThat(actualData, containsInAnyOrder(expectedDataList.toArray()));
    }

    @Test
    public void testParallelMapWithShardingFromDifferentPartitions() {
        FakeLbPool fakePool = new FakeLbPool();
        Function<Integer, Integer> mapFunction = i -> i * 7;
        int shardNumber = 5;
        ExactlyOnceLbTransfer<Integer, Integer> lbTransfer = new ExactlyOnceLbTransfer<>(
                fakePool,
                (i, meta) -> new ShardAddress(null, i % shardNumber),
                INT_SERIALIZER, INT_SERIALIZER,
                mapFunction,
                EXECUTOR
        );
        lbTransfer.setMapChunkSize(3);
        int origPartitionNumber = 15;
        var data = genInData(origPartitionNumber, 15, 150, true);
        StreamConsumer mockedConsumer = createMockedConsumer(data);


        lbTransfer.startNewConsumer(mockedConsumer);


        List<Integer> actualData = fakePool.readFlatData(INT_SERIALIZER);

        assertThat(fakePool.getCache(), aMapWithSize(origPartitionNumber * shardNumber));


        List<Integer> originalFlatData = readFlatDataFromResponse(data);
        List<Integer> expectedDataList = F.map(originalFlatData, mapFunction);

        assertThat(actualData, containsInAnyOrder(expectedDataList.toArray()));
    }

    private StreamConsumer createMockedConsumer(ConsumerReadResponse data) {
        StreamConsumer mockedConsumer = mock(StreamConsumer.class);

        doAnswer(invocation -> {
            StreamListener listener = invocation.getArgument(0);
            StreamListener.ReadResponder fakeResponder = mock(StreamListener.ReadResponder.class);

            listener.onRead(data, fakeResponder);
            return null;
        }).when(mockedConsumer).startConsume(any(StreamListener.class));

        return mockedConsumer;
    }

    private List<Integer> readFlatDataFromResponse(ConsumerReadResponse response) {
        return response.getBatches().stream().flatMap(messageBatch ->
                messageBatch.getMessageData().stream().flatMap(messageData ->
                        INT_SERIALIZER.deserialize(messageData.getDecompressedData()).stream()
                )
        ).toList();
    }

    private ConsumerReadResponse genInData(int batchesCount, int messageCountInBatch, int dataListSize) {
        return genInData(batchesCount, messageCountInBatch, dataListSize, false);
    }

    private ConsumerReadResponse genInData(
            int batchesCount, int messageCountInBatch, int dataListSize, boolean fromDifferentPartition
    ) {
        var batches = new ArrayList<MessageBatch>(batchesCount);
        for (int bi = 0; bi < batchesCount; bi++) {
            var messages = new ArrayList<MessageData>(messageCountInBatch);
            for (int mi = 0; mi < messageCountInBatch; mi++) {
                int offset = (bi * messageCountInBatch + mi);
                int start = offset * dataListSize;
                var dataList = genIntegerList(start, dataListSize);
                messages.add(
                        new MessageData(
                                ZSTD.compressData(INT_SERIALIZER.serialize(dataList)), offset,
                                new MessageMeta(
                                        ("kek#" + bi).getBytes(), offset,
                                        0, 0, null, ZSTD, null
                                )
                        )
                );
            }
            int partition = (fromDifferentPartition) ? bi : 42;
            batches.add(new MessageBatch("some-topic", partition, messages));
        }
        return new ConsumerReadResponse(batches, 13);

    }

    private List<Integer> genIntegerList(int s, int size) {
        return Stream.iterate(s, i -> i + 1).limit(size).toList();
    }

}
