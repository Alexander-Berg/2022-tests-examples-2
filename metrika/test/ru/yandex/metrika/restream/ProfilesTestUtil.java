package ru.yandex.metrika.restream;

import java.util.Arrays;

import ru.yandex.metrika.restream.collector.proto.Collector;

public class ProfilesTestUtil {

    public static Collector.Profile matchedProfile(Collector.VisitData... visitData) {
        return profile(true, visitData);
    }

    public static Collector.Profile profile(boolean match, Collector.VisitData... visitsData) {
        return Collector.Profile.newBuilder()
                .addAllVisitsData(Arrays.asList(visitsData))
                .setMatch(match)
                .build();
    }


    public static Collector.VisitData visit(int segmentVersion, long visitID, int utcStartTime, int visitVersion, int sign) {
        return Collector.VisitData.newBuilder()
                .setSegmentVersion(segmentVersion)
                .setVisitID(visitID)
                .setUTCStartTime(utcStartTime)
                .setVisitVersion(visitVersion)
                .setSign(sign)
                .build();
    }
}
