package ru.yandex.autotests.audience.internal.api.schema.custom;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import ru.yandex.metrika.api.error.ApiError;

import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
        "code",
        "errors",
        "message",
})
public class SegmentDataSchemaNegative {
    @JsonProperty("code")
    private Long code;
    @JsonProperty("errors")
    private List<ApiError> errors;
    @JsonProperty("message")
    private String message;

    @JsonProperty("code")
    public Long getCode() {
        return code;
    }

    @JsonProperty("code")
    public void setCode(Long code) {
        this.code = code;
    }

    @JsonProperty("errors")
    public List<ApiError> getErrors() {
        return errors;
    }

    @JsonProperty("errors")
    public void setErrors(List<ApiError> errors) {
        this.errors = errors;
    }

    @JsonProperty("message")
    public String getMessage() {
        return message;
    }

    @JsonProperty("message")
    public void setMessage(String message) {
        this.message = message;
    }
}
