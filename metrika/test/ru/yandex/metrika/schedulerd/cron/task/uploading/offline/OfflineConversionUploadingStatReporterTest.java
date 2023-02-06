package ru.yandex.metrika.schedulerd.cron.task.uploading.offline;

import java.util.stream.DoubleStream;

import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.junit.BeforeClass;
import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;

public class OfflineConversionUploadingStatReporterTest {

    private static OfflineConversionUploadingStatReporter statReporter;

    private static final int VALUES_SIZE = 100;
    private static final double[] VALUES = DoubleStream.iterate(0, i -> i + 1).limit(VALUES_SIZE).toArray();

    @BeforeClass
    public static void setUp() {
        statReporter = new OfflineConversionUploadingStatReporter();
        statReporter.report(VALUES_SIZE, new DescriptiveStatistics(VALUES));
    }

    @Test
    public void getPerc999() {
        assertThat(statReporter.getPerc999()).isEqualTo(99.0);
    }

    @Test
    public void getPerc98() {
        assertThat(statReporter.getPerc98()).isBetween(97.0, 98.0);
    }

    @Test
    public void getPerc95() {
        assertThat(statReporter.getPerc95()).isBetween(94.0, 95.0);
    }

    @Test
    public void getPerc75() {
        assertThat(statReporter.getPerc75()).isBetween(74.0, 75.0);
    }

    @Test
    public void getQueueSize() {
        assertThat(statReporter.getQueueSize()).isEqualTo(VALUES_SIZE);
    }
}
