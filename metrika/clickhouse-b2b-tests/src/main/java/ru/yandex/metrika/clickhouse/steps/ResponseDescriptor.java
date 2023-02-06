package ru.yandex.metrika.clickhouse.steps;

import okhttp3.HttpUrl;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;
import java.util.stream.Collectors;

public class ResponseDescriptor {
    private Throwable exception;
    private String headers;
    private int code;
    private String message;
    private long contentLenght;
    private String contentType;
    private String response;
    private String requestUrl;
    private String requestParams;

    public Throwable getException() {
        return exception;
    }

    public boolean isHasException() {
        return exception != null;
    }

    public String getHeaders() {
        return headers;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public long getContentLenght() {
        return contentLenght;
    }

    public String getContentType() {
        return contentType;
    }

    public String getResponse() {
        return response;
    }

    public String getRequestUrl() {
        return requestUrl;
    }

    public String getRequestParams() {
        return requestParams;
    }

    private static String extractParams(HttpUrl url) {
        return url.queryParameterNames().stream()
                .map(n -> String.format("%s=%s", n, url.queryParameterValues(n)))
                .collect(Collectors.joining("\n"));
    }

    private ResponseDescriptor(Builder builder) {
        exception = builder.exception;
        if (builder.response != null) {
            try {
                headers = builder.response.headers().toString();
                code = builder.response.code();
                message = builder.response.message();
                contentLenght = builder.response.body().contentLength();
                contentType = builder.response.body().contentType().toString();

                requestUrl = builder.response.request().url().toString();
                requestParams = extractParams(builder.response.request().url());

                try {
                    response = builder.response.body().string();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            } finally {
                builder.response.close();
            }
        } else {
            requestUrl = builder.request.url().toString();
            requestParams = extractParams(builder.request.url());
        }
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private Throwable exception;
        private Response response;
        private Request request;

        private Builder() {}

        public Builder withException(final Throwable exception) {
            this.exception = exception;
            return this;
        }

        public Builder withRequest(final Request request) {
            this.request = request;
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
