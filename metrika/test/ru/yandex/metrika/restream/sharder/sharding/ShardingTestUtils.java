package ru.yandex.metrika.restream.sharder.sharding;

import ru.yandex.metrika.restream.proto.Restream;

public class ShardingTestUtils {

    static Restream.SegmentReference sr(int segmentId, int version) {
        return Restream.SegmentReference.newBuilder().setSegmentId(segmentId).setVersion(version).build();
    }

}
