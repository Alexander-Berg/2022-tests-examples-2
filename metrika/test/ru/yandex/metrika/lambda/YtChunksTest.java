package ru.yandex.metrika.lambda;

import java.util.Arrays;
import java.util.List;
import java.util.TimeZone;

import org.apache.commons.lang3.tuple.Pair;
import org.joda.time.DateTimeZone;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;

public class YtChunksTest {

    @BeforeClass
    public static void init() {
        TimeZone tz = TimeZone.getTimeZone("Europe/Moscow");
        TimeZone.setDefault(tz);
        DateTimeZone.setDefault(DateTimeZone.forTimeZone(tz));
    }

    @Test
    public void testMergeIntervals30mOneInterval() {
        Assert.assertEquals(
                List.of(
                        Pair.of("2019-11-14T00:00:00", "2019-11-14T03:30:00")
                ),
                YtChunks.mergeIntervals30m(Arrays.asList(
                        "2019-11-14T00:00:00",
                        "2019-11-14T00:30:00",
                        "2019-11-14T01:00:00",
                        "2019-11-14T01:30:00",
                        "2019-11-14T02:00:00",
                        "2019-11-14T02:30:00",
                        "2019-11-14T03:00:00",
                        "2019-11-14T03:30:00"
                ))
        );
    }

    @Test
    public void testMergeIntervals30mTwoIntervals() {
        Assert.assertEquals(
                List.of(
                        Pair.of("2019-11-14T00:00:00", "2019-11-14T01:00:00"),
                        Pair.of("2019-11-14T02:00:00", "2019-11-14T03:30:00")

                ),
                YtChunks.mergeIntervals30m(Arrays.asList(
                        "2019-11-14T00:00:00",
                        "2019-11-14T00:30:00",
                        "2019-11-14T01:00:00",
                        "2019-11-14T02:00:00",
                        "2019-11-14T02:30:00",
                        "2019-11-14T03:00:00",
                        "2019-11-14T03:30:00"
                ))
        );
    }

    @Test
    public void testMergeIntervals1hOneInterval() {
        Assert.assertEquals(
                List.of(
                        Pair.of("2019-11-14T00:00:00", "2019-11-14T04:00:00")
                ),
                YtChunks.mergeIntervals1h(Arrays.asList(
                        "2019-11-14T00:00:00",
                        "2019-11-14T01:00:00",
                        "2019-11-14T02:00:00",
                        "2019-11-14T03:00:00",
                        "2019-11-14T04:00:00"
                ))
        );
    }

    @Test
    public void testMergeIntervals1hTwoIntervals() {
        Assert.assertEquals(
                List.of(
                        Pair.of("2019-11-14T00:00:00", "2019-11-14T01:00:00"),
                        Pair.of("2019-11-14T03:00:00", "2019-11-14T04:00:00")

                ),
                YtChunks.mergeIntervals1h(Arrays.asList(
                        "2019-11-14T00:00:00",
                        "2019-11-14T01:00:00",
                        "2019-11-14T03:00:00",
                        "2019-11-14T04:00:00"
                ))
        );
    }

    @Test
    public void testMergeIntervals1dOneInterval() {
        Assert.assertEquals(
                List.of(
                        Pair.of("2019-11-12", "2019-11-14")
                ),
                YtChunks.mergeIntervals1d(Arrays.asList(
                        "2019-11-12",
                        "2019-11-13",
                        "2019-11-14"
                ))
        );
    }

    @Test
    public void testMergeIntervals1dTwoIntervals() {
        Assert.assertEquals(
                List.of(
                        Pair.of("2019-11-10", "2019-11-11"),
                        Pair.of("2019-11-13", "2019-11-14")

                ),
                YtChunks.mergeIntervals1d(Arrays.asList(
                        "2019-11-10",
                        "2019-11-11",
                        "2019-11-13",
                        "2019-11-14"
                ))
        );
    }

    @Test
    public void testTableNameTimeWithoutSuffix() {
        Assert.assertEquals(
                1573434000000L,
                YtChunks.getTableNameTime("2019-11-11T04:00:00")
        );
    }

    @Test
    public void testTableNameTimeWithSuffix() {
        Assert.assertEquals(
                1573434000000L,
                YtChunks.getTableNameTime("2019-11-11T04:00:00_oc_m")
        );
    }

    @Test
    public void testTableNameTimeOnlyDateWithoutSuffix() {
        Assert.assertEquals(
                1573506000000L,
                YtChunks.getTableNameTime("2019-11-12")
        );
    }

    @Test
    public void testTableNameTimeOnlyDateWithSuffix() {
        Assert.assertEquals(
                1573506000000L,
                YtChunks.getTableNameTime("2019-11-12_xxx")
        );
    }

    @Test
    public void testTableNameSuffixWithoutSuffix() {
        Assert.assertEquals(
                "",
                YtChunks.getTableNameSuffix("2019-11-11T04:00:00")
        );
    }

    @Test
    public void testTableNameSuffixWithSuffix() {
        Assert.assertEquals(
                "oc_m",
                YtChunks.getTableNameSuffix("2019-11-11T04:00:00_oc_m")
        );
    }

    @Test
    public void testTableNameSuffixOnlyDateWithoutSuffix() {
        Assert.assertEquals(
                "",
                YtChunks.getTableNameSuffix("2019-11-12")
        );
    }

    @Test
    public void testTableNameSuffixOnlyDateWithSuffix() {
        Assert.assertEquals(
                "xxx",
                YtChunks.getTableNameSuffix("2019-11-12_xxx")
        );
    }
}
