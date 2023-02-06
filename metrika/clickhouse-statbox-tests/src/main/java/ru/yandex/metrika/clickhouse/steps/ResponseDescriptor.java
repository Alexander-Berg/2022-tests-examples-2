package ru.yandex.metrika.clickhouse.steps;

import okhttp3.Response;

import java.io.IOException;

public class ResponseDescriptor {
    private Throwable exception;
    private int code;
    private String message;
    private String response;

    public Throwable getException() {
        return exception;
    }

    public boolean isHasException() {
        return exception != null;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public String getResponse() {
        return response;
    }


    private ResponseDescriptor(Builder builder) {
        exception = builder.exception;
        if (builder.response != null) {
            code = builder.response.code();
            message = builder.response.message();

            try {
                response = builder.response.body().string();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public static Builder builer() {
        return new Builder();
    }

    public static class Builder {
        private Throwable exception;
        private Response response;

        private Builder() {}

        public Builder withException(final Throwable exception) {
            this.exception = exception;
            return this;
        }

        public Builder withResponse(final Response response) {
            this.response = response;
            return this;
        }

        public ResponseDescriptor build() {
            return new ResponseDescriptor(this);
        }
    }
}
