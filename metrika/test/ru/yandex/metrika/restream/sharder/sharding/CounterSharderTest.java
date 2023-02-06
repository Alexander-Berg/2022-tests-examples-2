package ru.yandex.metrika.restream.sharder.sharding;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Test;

import ru.yandex.metrika.restream.proto.Restream;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.restream.sharder.sharding.ShardingTestUtils.sr;

public class CounterSharderTest {


    @Test
    public void emptyShardingTable() {
        var shardingTable = new ShardingTable(List.of());

        var segmentSharder = new CounterSharder(shardingTable);

        var sharding = segmentSharder.getSharding(0);

        assertTrue("Should be no sharding info for counter 0", sharding.isEmpty());
    }

    @Test
    public void unknownCounterId() {
        var shardingTable = new ShardingTable(List.of(
                new ShardingTableRow(1, 0, 1., List.of(sr(1, 1)))
        ));

        var segmentSharder = new CounterSharder(shardingTable);

        var sharding = segmentSharder.getSharding(2);

        assertTrue("Should be no sharding info for counter 2", sharding.isEmpty());
    }

    @Test
    public void staticallyShardedSegment() {
        var row = new ShardingTableRow(1, 0, 1., List.of(sr(1, 1)));
        var shardingTable = new ShardingTable(List.of(
                row
        ));

        var segmentSharder = new CounterSharder(shardingTable);

        for (int i = 0; i < 1000; i++) {
            var sharding = segmentSharder.getSharding(1);
            var segmentReference = Restream.SegmentReference.newBuilder().setSegmentId(1).setVersion(1).build();
            assertThat(sharding, equalTo(Optional.of(row)));
        }
    }

    @Test
    public void dynamicallyShardedSegment() {
        var row1 = new ShardingTableRow(1, 0, 1., List.of(sr(1, 1)));
        var row2 = new ShardingTableRow(1, 1, 1., List.of(sr(1, 1)));
        var shardingTable = new ShardingTable(List.of(row1, row2));

        var segmentSharder = new CounterSharder(shardingTable);

        var thousandSharding = IntStream.range(0, 1000).mapToObj(i -> segmentSharder.getSharding(1)).collect(Collectors.toList());

        // при корректной реализации вероятность того, что какой либо из двух вариантов не встретится ни разу за 1000
        // попыток равно 1 / 2^1000
        // если запускать этот тесть каждую наносекунду ближайший миллион лет, то вероятность того, что он упадёт
        // примерно 3 * 10^-279
        var segmentReference = Restream.SegmentReference.newBuilder().setSegmentId(1).setVersion(1).build();
        assertThat(thousandSharding, hasItem(Optional.of(row1)));
        assertThat(thousandSharding, hasItem(Optional.of(row2)));
    }
}
