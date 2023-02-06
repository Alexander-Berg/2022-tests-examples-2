package ru.yandex.metrika.lambda.steps;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
public class InvariantResult {

    private final String version;
    private final String name;
    private final String script;
    private final boolean hasError;
    private final Exception error;
    private final boolean hasResult;
    private final boolean result;
    private final boolean hasDetails;
    private final List<? extends Map<String, String>> details;

    private InvariantResult(Builder builder) {
        this.version = builder.version;
        this.name = builder.name;
        this.script = builder.script;
        this.hasError = builder.hasError;
        this.error = builder.error;
        this.hasResult = builder.hasResult;
        this.result = builder.result;
        this.hasDetails = builder.hasDetails;
        this.details = builder.details;
    }

    public static Builder builder() {
        return new Builder();
    }

    public String getVersion() {
        return version;
    }

    public String getName() {
        return name;
    }

    public String getScript() {
        return script;
    }

    public boolean getHasError() {
        return hasError;
    }

    public Exception getError() {
        return error;
    }

    public boolean getHasResult() {
        return hasResult;
    }

    public boolean getResult() {
        return result;
    }

    public boolean getHasDetails() {
        return hasDetails;
    }

    public Status getStatus() {
        if (hasResult) {
            if (result) {
                return Status.SUCCESS;
            } else {
                return Status.FAILED;
            }
        } else {
            return Status.BROKEN;
        }
    }

    public List<? extends Map<String, String>> getDetails() {
        return details;
    }

    public List<String> getDetailsKeys() {
        if (hasDetails && details != null && !details.isEmpty()) {
            return new ArrayList<>(details.get(0).keySet());
        } else {
            return Collections.emptyList();
        }
    }

    @Override
    public String toString() {
        return getStatus().toString();
    }

    public enum Status {
        SUCCESS("Инвариант выполнен"),
        FAILED("Инвариант не выполнен"),
        BROKEN("Инвариант сломан");

        private final String label;

        Status(String label) {
            this.label = label;
        }

        @Override
        public String toString() {
            return this.label;
        }
    }

    public static class Builder {
        private String version;
        private String name;
        private String script;
        private boolean hasError = false;
        private Exception error;
        private boolean hasResult = false;
        private boolean result;
        private boolean hasDetails = false;
        private List<? extends Map<String, String>> details;

        private Builder() {
        }

        public InvariantResult build() {
            return new InvariantResult(this);
        }

        public Builder withVersion(final String version) {
            this.version = version;
            return this;
        }

        public Builder withName(final String name) {
            this.name = name;
            return this;
        }

        public Builder withScript(final String script) {
            this.script = script;
            return this;
        }

        public Builder withError(final Exception error) {
            this.error = error;
            this.hasError = true;
            return this;
        }

        public Builder withResult(final boolean result) {
            this.result = result;
            this.hasResult = true;
            return this;
        }

        public Builder withDetails(final List<? extends Map<String, String>> details) {
            this.details = details;
            this.hasDetails = true;
            return this;
        }
    }
}
