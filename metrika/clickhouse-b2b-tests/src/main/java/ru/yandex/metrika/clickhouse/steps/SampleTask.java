package ru.yandex.metrika.clickhouse.steps;

import java.nio.file.Path;
import java.util.concurrent.Callable;

public class SampleTask implements Callable<SampleResult> {

    private final Sample sample;
    private final Path reportDestination;

    public SampleTask(Sample sample, Path reportDestination) {
        this.sample = sample;
        this.reportDestination = reportDestination;
    }

    @Override
    public SampleResult call() throws Exception {
        return sample.perform(reportDestination);
    }
}
