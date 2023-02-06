package ru.yandex.metrika.clickhouse.steps;

import org.joda.time.DateTime;
import org.joda.time.Period;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.PeriodFormat;

import java.util.Map;

public class TestCaseBriefResult {
    private final String destination;
    private final String handle;
    private final long totalSamples;
    private final double percentile;
    private final DateTime startDateTime;
    private final DateTime finishDateTime;
    private final Map<DifferenceDescriptor.ResultKind, Long> aggregatedResults;

    private TestCaseBriefResult(Builder builder) {
        this.destination = builder.destination;
        this.handle = builder.handle;
        this.totalSamples = builder.totalSamples;
        this.percentile = builder.percentile;
        this.aggregatedResults = builder.aggregatedResults;
        this.startDateTime = builder.startDateTime;
        this.finishDateTime = builder.finishDateTime;
    }

    public String getDestination() {
        return destination;
    }

    public String getHandle() {
        return handle;
    }

    public long getTotalSamples() {
        return totalSamples;
    }

    public double getPercentile() {
        return percentile;
    }

    public Map<DifferenceDescriptor.ResultKind, Long> getAggregatedResults() {
        return aggregatedResults;
    }

    public long getTotalSamplesByResultKind(DifferenceDescriptor.ResultKind resultKind) {
        return getAggregatedResults().get(resultKind);
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

    public String getStartDateTime() {
        return JodaUtils.DTF.print(startDateTime);
    }

    public String getFinishDateTime() {
        return JodaUtils.DTF.print(finishDateTime);
    }

    public String getDuration() {
        return JodaUtils.PF.print(new Period(startDateTime, finishDateTime));
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private String destination;
        private String handle;
        private long totalSamples;
        private double percentile;
        private DateTime startDateTime;
        private DateTime finishDateTime;
        private Map<DifferenceDescriptor.ResultKind, Long> aggregatedResults;

        public TestCaseBriefResult build() {
            return new TestCaseBriefResult(this);
        }

        public Builder withDestination(final String destination) {
            this.destination = destination;
            return this;
        }

        public Builder withHandle(final String handle) {
            this.handle = handle;
            return this;
        }

        public Builder withTotalSamples(final long totalSamples) {
            this.totalSamples = totalSamples;
            return this;
        }

        public Builder withPercentile(final double percentile) {
            this.percentile = percentile;
            return this;
        }

        public Builder withAggregatedResults(final Map<DifferenceDescriptor.ResultKind, Long> aggregatedResults) {
            this.aggregatedResults = aggregatedResults;
            return this;
        }

        public Builder withStartDateTime(final DateTime startDateTime) {
            this.startDateTime = startDateTime;
            return this;
        }

        public Builder withFinishDateTime(final DateTime finishDateTime) {
            this.finishDateTime = finishDateTime;
            return this;
        }
    }
}

