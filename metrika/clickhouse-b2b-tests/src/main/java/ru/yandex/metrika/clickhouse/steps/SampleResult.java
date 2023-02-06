package ru.yandex.metrika.clickhouse.steps;

import org.joda.time.DateTime;
import org.joda.time.Period;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;

import java.net.URL;

public class SampleResult {
    private final String handle;
    private final String params;
    private final int counter;
    private final int seq;
    private final String id;
    private final FreeFormParameters dynamicParams;
    private final URL refHost;
    private final URL testHost;
    private final DateTime startDateTime;
    private final DateTime finishDateTime;
    private final DifferenceDescriptor diff;

    private SampleResult(Builder builder) {
        this.handle = builder.handle;
        this.params = builder.params;
        this.counter = builder.counter;
        this.seq = builder.seq;
        this.id = builder.id;
        this.dynamicParams = builder.dynamicParams;
        this.refHost = builder.refHost;
        this.testHost = builder.testHost;
        this.startDateTime = builder.startDateTime;
        this.finishDateTime = builder.finishDateTime;
        this.diff = builder.diff;
    }

    public String getHandle() {
        return handle;
    }

    public String getParams() {
        return params;
    }

    public int getCounter() {
        return counter;
    }

    public int getSeq() {
        return seq;
    }

    public String getId() {
        return id;
    }

    public FreeFormParameters getDynamicParams() {
        return dynamicParams;
    }

    public URL getRefHost() {
        return refHost;
    }

    public URL getTestHost() {
        return testHost;
    }

    public DifferenceDescriptor getDiff() {
        return diff;
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
        private String handle;
        private String params;
        private int counter;
        private int seq;
        private String id;
        private FreeFormParameters dynamicParams;
        private URL refHost;
        private URL testHost;
        private DateTime startDateTime;
        private DateTime finishDateTime;
        private DifferenceDescriptor diff;

        private Builder() {}

        public SampleResult build() {
            return new SampleResult(this);
        }

        public Builder withHandle(final String handle) {
            this.handle = handle;
            return this;
        }

        public Builder withParams(final String params) {
            this.params = params;
            return this;
        }

        public Builder withCounter(final int counter) {
            this.counter = counter;
            return this;
        }

        public Builder withSeq(final int seq) {
            this.seq = seq;
            return this;
        }

        public Builder withId(final String id) {
            this.id = id;
            return this;
        }

        public Builder withDynamicParams(final FreeFormParameters dynamicParams) {
            this.dynamicParams = dynamicParams;
            return this;
        }

        public Builder withRefHost(final URL refHost) {
            this.refHost = refHost;
            return this;
        }

        public Builder withTestHost(final URL testHost) {
            this.testHost = testHost;
            return this;
        }

        public Builder withDiff(final DifferenceDescriptor diff) {
            this.diff = diff;
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
}
