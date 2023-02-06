package ru.yandex.metrika.clickhouse.steps;

import org.joda.time.DateTime;
import org.joda.time.Period;

import java.util.List;

import static java.util.stream.Collectors.toList;

public class TestCaseResults {
    private final List<SampleResult> samples;
    private final String destination;
    private final String handle;
    private final double percentile;
    private final DateTime startDateTime;
    private final DateTime finishDateTime;

    private TestCaseResults(Builder builder) {
        this.samples = builder.samples;
        this.destination = builder.destination;
        this.handle = builder.handle;
        this.percentile = builder.percentile;
        this.startDateTime = builder.startDateTime;
        this.finishDateTime = builder.finishDateTime;
    }

    public List<SampleResult> getSamples() {
        return samples;
    }

    public String getDestination() {
        return destination;
    }

    public String getHandle() {
        return handle;
    }

    public double getPercentile() {
        return percentile;
    }

    public DateTime getStartDateTime() {
        return startDateTime;
    }

    public DateTime getFinishDateTime() {
        return finishDateTime;
    }

    public String getStartDateTimeAsString() {
        return JodaUtils.DTF.print(startDateTime);
    }

    public String getFinishDateTimeAsString() {
        return JodaUtils.DTF.print(finishDateTime);
    }

    public String getDurationAsString() {
        return JodaUtils.PF.print(new Period(startDateTime, finishDateTime));
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private List<SampleResult> samples;
        private String destination;
        private String handle;
        private double percentile;
        private DateTime startDateTime;
        private DateTime finishDateTime;

        private Builder() {}

        public TestCaseResults build() {
            return new TestCaseResults(this);
        }

        public Builder withSamples(final List<SampleResult> samples) {
            this.samples = samples;
            return this;
        }

        public Builder withDestination(final String destination) {
            this.destination = destination;
            return this;
        }

        public Builder withHandle(final String handle) {
            this.handle = handle;
            return this;
        }

        public Builder withPercentile(final double percentile) {
            this.percentile = percentile;
            return this;
        }

        public Builder start() {
            this.startDateTime = DateTime.now();
            return this;
        }

        public Builder finish() {
            this.finishDateTime = DateTime.now();
            return this;
        }
    }

    public int getTotalSamples() {
        return samples.size();
    }

    public long getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind resultKind) {
        return samples.stream()
                .filter(s -> s.getDiff().getResultKind() == resultKind)
                .count();
    }

    public List<SampleResult> getSamplesByResultKind(DifferenceDescriptor.ResultKind resultKind) {
        return samples.stream()
                .filter(s -> s.getDiff().getResultKind() == resultKind)
                .collect(toList());
    }

    public long getTotalSamplesNegative() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.NEGATIVE);
    }

    public long getTotalSamplesNotSimilar() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.NOT_SIMILAR);
    }

    public long getTotalSamplesBroken() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.BROKEN);
    }

    public long getTotalSamplesUnexpected() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.UNEXPECTED);
    }

    public long getTotalSamplesInternalError() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.INTERNAL_TEST_ERROR);
    }

    public long getTotalSamplesExternalError() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.EXTERNAL_TEST_ERROR);
    }

    public long getTotalSamplesBadRequest() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.BAD_REQUEST);
    }

    public long getTotalSamplesAlmostBadRequest() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.ALMOST_BAD_REQUEST);
    }

    public long getTotalSamplesNoData() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.NO_DATA);
    }

    public long getTotalSamplesPositive() {
        return getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind.POSITIVE);
    }

    public List<SampleResult> getSamplesNegative() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.NEGATIVE);
    }

    public List<SampleResult> getSamplesNotSimilar() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.NOT_SIMILAR);
    }

    public List<SampleResult> getSamplesBroken() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.BROKEN);
    }

    public List<SampleResult> getSamplesUnexpected() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.UNEXPECTED);
    }

    public List<SampleResult> getSamplesInternalError() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.INTERNAL_TEST_ERROR);
    }

    public List<SampleResult> getSamplesExternalError() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.EXTERNAL_TEST_ERROR);
    }

    public List<SampleResult> getSamplesBadRequest() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.BAD_REQUEST);
    }

    public List<SampleResult> getSamplesAlmostBadRequest() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.ALMOST_BAD_REQUEST);
    }

    public List<SampleResult> getSamplesNoData() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.NO_DATA);
    }

    public List<SampleResult> getSamplesPositive() {
        return getSamplesByResultKind(DifferenceDescriptor.ResultKind.POSITIVE);
    }
}
