package ru.yandex.metrika.schedulerd.cron.task.uploading;

import java.time.ZoneId;
import java.time.ZonedDateTime;

import org.jetbrains.annotations.NotNull;
import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;

public class UploadingChunkPeriodUtilsTest {

    public static final int YEAR = 2018;
    public static final int MONTH = 11;
    public static final int DAY = 1;

    @Test
    public void getChunkPeriodFor_9_00_00() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(9, 0, 0)))
                .isEqualTo(getDateTime(9, 0));
    }

    @Test
    public void getChunkPeriodFor_9_00_01() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(9, 0, 1)))
                .isEqualTo(getDateTime(9, 30));
    }

    @Test
    public void getChunkPeriodFor_9_29_59() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(9, 29, 59)))
                .isEqualTo(getDateTime(9, 30));
    }

    @Test
    public void getChunkPeriodFor_9_30_00() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(9, 30, 0)))
                .isEqualTo(getDateTime(9, 30));
    }

    @Test
    public void getChunkPeriodFor_9_30_01() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(9, 30, 1)))
                .isEqualTo(getDateTime(10, 0));
    }

    @Test
    public void getChunkPeriodFor_9_59_59() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(9, 59, 59)))
                .isEqualTo(getDateTime(10, 0));
    }

    @Test
    public void getChunkPeriodFor_10_00_00() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriod(createDateTime(10, 0, 0)))
                .isEqualTo(getDateTime(10, 0));
    }

    @Test
    public void getChunkPeriodBeforeFor_9_00_00() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(9, 0, 0)))
                .isEqualTo(getDateTime(8, 30));
    }

    @Test
    public void getChunkPeriodBeforeFor_9_00_01() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(9, 0, 1)))
                .isEqualTo(getDateTime(9, 0));
    }

    @Test
    public void getChunkPeriodBeforeFor_9_29_59() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(9, 29, 59)))
                .isEqualTo(getDateTime(9, 0));
    }

    @Test
    public void getChunkPeriodBeforeFor_9_30_00() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(9, 30, 0)))
                .isEqualTo(getDateTime(9, 0));
    }

    @Test
    public void getChunkPeriodBeforeFor_9_30_01() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(9, 30, 1)))
                .isEqualTo(getDateTime(9, 30));
    }

    @Test
    public void getChunkPeriodBeforeFor_9_59_59() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(9, 59, 59)))
                .isEqualTo(getDateTime(9, 30));
    }

    @Test
    public void getChunkPeriodBeforeFor_10_00_00() {
        assertThat(UploadingChunkPeriodUtils.getChunkPeriodBefore(createDateTime(10, 0, 0)))
                .isEqualTo(getDateTime(9, 30));
    }

    private ZonedDateTime createDateTime(int hour, int min, int sec) {
        return ZonedDateTime.of(YEAR, MONTH, DAY, hour, min, sec, 0, ZoneId.systemDefault());
    }

    @NotNull
    private ZonedDateTime getDateTime(int h, int m) {
        return ZonedDateTime.of(YEAR, MONTH, DAY, h, m, 0, 0, ZoneId.systemDefault());
    }
}
