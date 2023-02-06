package ru.yandex.metrika.restream.sharder.sharding;

import java.util.List;
import java.util.TreeSet;

import org.junit.Test;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;
import static ru.yandex.metrika.restream.sharder.sharding.ShardingTestUtils.sr;

public class ShardingTableBuilderTest {

    @Test
    public void singleShardSegment() {
        var shardingTableBuilderService = new ShardingTableBuilder(1, () -> List.of(
                new CounterShardingInfo(1, 0, List.of(sr(1, 1)))
        ));

        var rows = shardingTableBuilderService.buildShardingTable().getRows();

        assertThat(rows, equalTo(new TreeSet<>(List.of(
                new ShardingTableRow(1, 0, 1., List.of(sr(1, 1)))
        ))));
    }

    @Test
    public void twoShardsSegment() {
        var shardingTableBuilderService = new ShardingTableBuilder(2, () -> List.of(
                new CounterShardingInfo(1, 1, List.of(sr(1, 1)))
        ));

        var rows = shardingTableBuilderService.buildShardingTable().getRows();

        assertThat(rows, equalTo(new TreeSet<>(List.of(
                new ShardingTableRow(1, 0, 1. / 2, List.of(sr(1, 1))),
                new ShardingTableRow(1, 1, 1. / 2, List.of(sr(1, 1)))
        ))));

    }

    @Test
    public void segmentOnShardsEdge() {
        var shardingTableBuilderService = new ShardingTableBuilder(2, () -> List.of(
                new CounterShardingInfo(1, 1., List.of(sr(1, 1))),
                new CounterShardingInfo(2, 1., List.of(sr(2, 1))),
                new CounterShardingInfo(3, 1., List.of(sr(3, 1)))
        ));

        var rows = shardingTableBuilderService.buildShardingTable().getRows();

        assertThat(rows, equalTo(new TreeSet<>(List.of(
                new ShardingTableRow(1, 0, 2. / 3, List.of(sr(1, 1))),
                new ShardingTableRow(2, 0, 1. / 3, List.of(sr(2, 1))),
                new ShardingTableRow(2, 1, 1. / 3, List.of(sr(2, 1))),
                new ShardingTableRow(3, 1, 2. / 3, List.of(sr(3, 1)))
        ))));
    }

    @Test
    public void segmentBiggerThenShard() {
        var shardingTableBuilderService = new ShardingTableBuilder(3, () -> List.of(
                new CounterShardingInfo(1, 1, List.of(sr(1, 1))),
                new CounterShardingInfo(2, 58, List.of(sr(2, 1))),
                new CounterShardingInfo(3, 1, List.of(sr(3, 1)))
        ));

        var rows = shardingTableBuilderService.buildShardingTable().getRows();

        assertThat(rows, equalTo(new TreeSet<>(List.of(
                new ShardingTableRow(1, 0, 1., List.of(sr(1, 1))),
                new ShardingTableRow(2, 0, 19., List.of(sr(2, 1))),
                new ShardingTableRow(2, 1, 20., List.of(sr(2, 1))),
                new ShardingTableRow(2, 2, 19., List.of(sr(2, 1))),
                new ShardingTableRow(3, 2, 1., List.of(sr(3, 1)))
        ))));
    }

    @Test
    public void segmentsWithDifferentVersions() {
        var shardingTableBuilderService = new ShardingTableBuilder(2, () -> List.of(
                new CounterShardingInfo(1, 1., List.of(sr(1, 4))),
                new CounterShardingInfo(2, 1., List.of(sr(2, 7)))
        ));

        var rows = shardingTableBuilderService.buildShardingTable().getRows();

        assertThat(rows, equalTo(new TreeSet<>(List.of(
                new ShardingTableRow(1,0, 1, List.of(sr(1, 4))),
                new ShardingTableRow(2,1, 2, List.of(sr(2, 7)))
        ))));
    }

    @Test
    public void zeroWeightCounter() {
        var shardingTableBuilderService = new ShardingTableBuilder(2, () -> List.of(
                new CounterShardingInfo(1, 1, List.of(sr(1, 1))),
                new CounterShardingInfo(2, 0, List.of(sr(2, 1))),
                new CounterShardingInfo(3, 1, List.of(sr(3, 1)))
        ));

        var rows = shardingTableBuilderService.buildShardingTable().getRows();

        assertThat(rows, equalTo(new TreeSet<>(List.of(
                new ShardingTableRow(1, 0, 1., List.of(sr(1, 1))),
                new ShardingTableRow(2, 1, 0, List.of(sr(2, 1))),
                new ShardingTableRow(3, 1, 1., List.of(sr(3, 1)))
        ))));
    }
}
