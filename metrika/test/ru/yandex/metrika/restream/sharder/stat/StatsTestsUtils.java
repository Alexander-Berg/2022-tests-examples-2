package ru.yandex.metrika.restream.sharder.stat;

import java.util.Arrays;
import java.util.Collections;

import com.google.common.base.Joiner;
import com.google.protobuf.ByteString;
import it.unimi.dsi.fastutil.longs.LongRBTreeSet;
import it.unimi.dsi.fastutil.longs.LongSortedSet;

import ru.yandex.metrika.restream.proto.Restream;

public class StatsTestsUtils {

    static final String HOST_ID = "localhost";
    static final String HOST_ID_2 = "localhost_2";
    static final String HOST_ID_3 = "localhost_2";

    static final int COUNTER_ID = 1;
    static final int COUNTER_ID_2 = 2;
    static final Restream.VisitLite EMPTY_VISIT = Restream.VisitLite.newBuilder().setCounterID(COUNTER_ID).build();
    static final Restream.VisitLite EMPTY_VISIT_2 = Restream.VisitLite.newBuilder().setCounterID(COUNTER_ID_2).build();
    static final Restream.VisitLite BIG_VISIT = Restream.VisitLite.newBuilder().setCounterID(COUNTER_ID)
            .setStartURL(ByteString.copyFromUtf8("https://ya.ru/" + Joiner.on("").join(Collections.nCopies(100_000, "1"))))
            .build();
    static final Restream.VisitLite BIG_VISIT_2 = BIG_VISIT.toBuilder().setCounterID(COUNTER_ID_2).build();

    static Restream.VisitWithSegments vs(Restream.VisitLite visitLite) {
        return Restream.VisitWithSegments.newBuilder().setVisit(visitLite).build();
    }

    static LongSortedSet slotIds(long... longs) {
        var treeSet = new LongRBTreeSet();
        Arrays.stream(longs).forEach(treeSet::add);
        return treeSet;
    }
}
