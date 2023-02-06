package ru.yandex.metrika.restream.processing;

import java.time.Duration;
import java.time.Instant;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.restream.ProfilesTestUtil;
import ru.yandex.metrika.restream.collector.proto.Collector;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.restream.ProfilesTestUtil.matchedProfile;
import static ru.yandex.metrika.restream.ProfilesTestUtil.profile;

public class ProfilesProcessorTest {

    private ProfilesProcessor profilesProcessor;
    private int nowSeconds;
    private int betweenTTLsSeconds;
    private int notRelevantSeconds;

    @Before
    public void setUp() {
        profilesProcessor = new ProfilesProcessor(Duration.ofDays(1), Duration.ofDays(10));
        nowSeconds = (int) Instant.now().getEpochSecond();
        betweenTTLsSeconds = nowSeconds - (int) Duration.ofDays(2).toSeconds();
        notRelevantSeconds = nowSeconds - (int) Duration.ofDays(20).toSeconds();
    }

    @Test
    public void compactEmpty() {
        assertEquals(
                profile(false),
                profilesProcessor.compact(profile(false))
        );
    }

    @Test
    public void compactNotMatch() {
        assertEquals(
                profile(false, visit(1, 1, -1)),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, 1), visit(1, 1, -1))
                )
        );
    }

    @Test
    public void compactNotMatchMultipleVisits() {
        assertEquals(
                profile(false, visit(1, 1, -1), visit(2, 5, -1)),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, 1), visit(1, 1, -1),
                        visit(2, 2, 1), visit(2, 2, -1), visit(2, 5, 1), visit(2, 5, -1)
                ))
        );
    }

    @Test
    public void compactNotMatchNotFullHistory() {
        assertEquals(
                profile(false, visit(1, 5, -1)),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 2, 1)/* no 2, -1 here*/, visit(1, 5, 1), visit(1, 5, -1)
                ))
        );
    }

    @Test
    public void compactUsual() {
        assertEquals(
                matchedProfile(visit(1, 6, 1)),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 5, 1), visit(1, 5, -1), visit(1, 6, 1)
                ))
        );
    }

    @Test
    public void compactUsualMultipleVisits() {
        assertEquals(
                matchedProfile(
                        visit(1, 3, 1),
                        visit(2, 6, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, 1), visit(1, 1, -1), visit(1, 2, 1), visit(1, 2, -1), visit(1, 3, 1),
                        visit(2, 5, 1), visit(2, 5, -1), visit(2, 6, 1)
                ))
        );
    }

    @Test
    public void compactUsualOneVisitToEmpty() {
        assertEquals(
                matchedProfile(
                        visit(1, 2, -1),
                        visit(2, 6, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, 1), visit(1, 1, -1), visit(1, 2, 1), visit(1, 2, -1),
                        visit(2, 5, 1), visit(2, 5, -1), visit(2, 6, 1)
                ))
        );
    }

    @Test
    public void compactWithMissingVersions() {
        assertEquals(
                matchedProfile(
                        visit(1, 6, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 4, 1), visit(1, 4, -1), visit(1, 5, 1), visit(1, 6, 1)
                ))
        );
    }

    @Test
    public void compactWithDuplicates() {
        assertEquals(
                matchedProfile(
                        visit(1, 6, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 4, 1), visit(1, 4, -1), visit(1, 5, 1), visit(1, 6, 1)
                ))
        );
    }

    @Test
    public void compactWithHangingMinusSignVersion() {
        assertEquals(
                profile(false, visit(1, 6, -1)),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 4, 1), visit(1, 4, -1), visit(1, 5, 1), visit(1, 6, -1)
                ))
        );
    }

    @Test
    public void compactWithDifferentSegmentVersions() {
        assertEquals(
                matchedProfile(
                        // остаётся только последняя версия сегмента
                        visit(2, 2, 2, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, 1, 1), visit(1, 1, 1, -1),
                        visit(2, 2, 1, 1), visit(2, 2, 1, -1), visit(2, 2, 2, 1)
                ))
        );
    }

    @Test
    public void compactRemoveBetweenTTLsVisitsIfHasRecentVisits() {
        assertEquals(
                matchedProfile(
                        visit(2, 6, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, betweenTTLsSeconds, 1, 1), visit(1, 1, betweenTTLsSeconds, 1, -1), visit(1, 1, betweenTTLsSeconds, 2, 1),
                        visit(2, 5, 1), visit(2, 5, -1), visit(2, 6, 1)
                ))
        );
    }

    @Test
    public void compactRemoveNotRelevantVisitsIfHasRecentVisits() {
        assertEquals(
                matchedProfile(
                        visit(2, 6, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, notRelevantSeconds, 2, 1),
                        visit(2, 5, 1), visit(2, 5, -1), visit(2, 6, 1)
                ))
        );
    }

    @Test
    public void compactLeaveLastRelevantVisitBetweenTTLs() {
        assertEquals(
                matchedProfile(
                        visit(1, 4, betweenTTLsSeconds + 2, 1, 1)
                ),
                profilesProcessor.compact(matchedProfile(
                        visit(1, 1, notRelevantSeconds, 3, 1),
                        visit(1, 2, betweenTTLsSeconds, 3, 1),
                        visit(1, 3, betweenTTLsSeconds + 1, 6, 1),
                        visit(1, 4, betweenTTLsSeconds + 2, 1, 1)
                ))
        );
    }

    @Test
    public void compactFilteringBySegmentVersion() {
        assertEquals(
                profile(false),
                profilesProcessor.compactFiltering(
                        matchedProfile(
                                visit(1, 1, 1, 1), visit(1, 1, 1, -1),
                                visit(2, 2, 1, 1), visit(2, 2, 1, -1), visit(2, 2, 2, 1)
                        ),
                        vd -> vd.getSegmentVersion() >= 3
                )
        );
    }

    @Test(expected = IllegalArgumentException.class)
    public void compactOutOfOrderSegmentVersions() {
        profilesProcessor.compact(matchedProfile(
                visit(2, 1, 1, 1),
                visit(1, 1, 1, 1)
        ));
    }

    @Test(expected = IllegalArgumentException.class)
    public void compactOutOfOrderVisits() {
        profilesProcessor.compact(matchedProfile(
                visit(2, 1, 1),
                visit(1, 1, 1)
        ));
    }

    @Test(expected = IllegalArgumentException.class)
    public void compactOutOfOrderVersions() {
        profilesProcessor.compact(matchedProfile(
                visit(1, 2, 1),
                visit(1, 1, 1)
        ));
    }

    @Test
    public void mergeBothEmpty() {
        assertEquals(
                profile(false),
                profilesProcessor.mergeAndCompact(
                        profile(false),
                        profile(false)
                )
        );
    }

    @Test
    public void mergeOneEmpty() {
        assertEquals(
                matchedProfile(
                        visit(1, 1, 1)
                ),
                profilesProcessor.mergeAndCompact(
                        matchedProfile(
                                visit(1, 1, 1)
                        ),
                        matchedProfile()
                )
        );
    }

    @Test
    public void mergeUsual() {
        assertEquals(
                matchedProfile(
                        visit(1, 1, 1),
                        visit(2, 1, 1)
                ),
                profilesProcessor.mergeAndCompact(
                        matchedProfile(
                                visit(1, 1, 1)
                        ),
                        matchedProfile(
                                visit(2, 1, 1)
                        )
                )
        );
    }

    @Test
    public void mergeUsualOutOfOrder() {
        assertEquals(
                matchedProfile(
                        visit(1, 1, 1),
                        visit(2, 1, 1)
                ),
                profilesProcessor.mergeAndCompact(
                        matchedProfile(
                                visit(2, 1, 1)
                        ),
                        matchedProfile(
                                visit(1, 1, 1)
                        )
                )
        );
    }

    @Test
    public void mergeMinusSignVersionOutOfOrder() {
        assertEquals(
                matchedProfile(
                        visit(1, 1, -1),
                        visit(2, 1, 1)
                ),
                profilesProcessor.mergeAndCompact(
                        matchedProfile(
                                visit(1, 1, -1)
                        ),
                        matchedProfile(
                                visit(1, 1, 1),
                                visit(2, 1, 1)
                        )
                )
        );
    }


    private Collector.VisitData visit(long visitID, int visitVersion, int sign) {
        return ProfilesTestUtil.visit(1, visitID, nowSeconds, visitVersion, sign);
    }

    private Collector.VisitData visit(int segmentVersion, long visitID, int visitVersion, int sign) {
        return ProfilesTestUtil.visit(segmentVersion, visitID, nowSeconds, visitVersion, sign);
    }

    private Collector.VisitData visit(int segmentVersion, long visitID, int utcStartTime, int visitVersion, int sign) {
        return ProfilesTestUtil.visit(segmentVersion, visitID, utcStartTime, visitVersion, sign);
    }
}
