package ru.yandex.metrika.retargeting;

public class BsSegmentTestUtil {

    public static boolean sameBsSegments(BsSegment l, BsSegment r) {
        return l.getSegmentId() == r.getSegmentId() &&
                l.getUid() == r.getUid() &&
                l.getTimestamp() == r.getTimestamp() &&
                l.isDelete() == r.isDelete() &&
                l.getRevision() == r.getRevision();
    }

}
