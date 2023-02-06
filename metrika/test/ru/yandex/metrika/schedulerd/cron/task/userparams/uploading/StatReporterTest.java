package ru.yandex.metrika.schedulerd.cron.task.userparams.uploading;

import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.junit.Before;
import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;

public class StatReporterTest {

    private StatReporter statReporter;

    @Before
    public void setUp() {
        statReporter = new StatReporter();
        statReporter.report(createStats());
    }

    private DescriptiveStatistics createStats() {
        double[] values = new double[] {1, 3, 3, 9};
        return new DescriptiveStatistics(values);
    }

    @Test
    public void minCalculation() {
        assertThat(statReporter.getMin()).isEqualTo(1);
    }

    @Test
    public void maxCalculation() {
        assertThat(statReporter.getMax()).isEqualTo(9);
    }

    @Test
    public void medianCalculation() {
        assertThat(statReporter.getMedian()).isEqualTo(3);
    }

    @Test
    public void perc99Calculation() {
        assertThat(statReporter.getPerc99()).isEqualTo(9);
    }

    @Test
    public void perc90Calculation() {
        assertThat(statReporter.getPerc90()).isEqualTo(9);
    }

    @Test
    public void perc80Calculation() {
        assertThat(statReporter.getPerc80()).isEqualTo(9);
    }
}
