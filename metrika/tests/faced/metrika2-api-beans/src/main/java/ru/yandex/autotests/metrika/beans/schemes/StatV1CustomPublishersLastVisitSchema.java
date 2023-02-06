package ru.yandex.autotests.metrika.beans.schemes;

import java.util.ArrayList;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import ru.yandex.metrika.api.error.ApiError;
import ru.yandex.metrika.spring.profile.ProfileData;


@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
        "last",
        "_profile",
        "code",
        "detailed_code",
        "errors",
        "message"
})

public class StatV1CustomPublishersLastVisitSchema {

    @JsonProperty("last")
    private String last;
    @JsonProperty("_profile")
    private ProfileData profile;
    @JsonProperty("code")
    private Long code;
    @JsonProperty("detailed_code")
    private String detailedCode;
    @JsonProperty("errors")
    private List<ApiError> errors = new ArrayList<ApiError>();
    @JsonProperty("message")
    private String message;



    @JsonProperty("_profile")
    public ProfileData getProfile() {
        return profile;
    }

    @JsonProperty("_profile")
    public void setProfile(ProfileData profile) {
        this.profile = profile;
    }

    @JsonProperty("last")
    public String getLast() {
        return last;
    }

    public StatV1CustomPublishersLastVisitSchema withProfile(ProfileData profile) {
        this.profile = profile;
        return this;
    }


    @JsonProperty("last")
    public void setLast(String last) {
        this.last = last;
    }

    public StatV1CustomPublishersLastVisitSchema withLast(String last) {
        this.last = last;
        return this;
    }

    @JsonProperty("code")
    public Long getCode() {
        return code;
    }

    @JsonProperty("code")
    public void setCode(Long code) {
        this.code = code;
    }

    public StatV1CustomPublishersLastVisitSchema withCode(Long code) {
        this.code = code;
        return this;
    }

    @JsonProperty("detailed_code")
    public String getDetailedCode() {
        return detailedCode;
    }

    @JsonProperty("detailed_code")
    public void setDetailedCode(String detailedCode) {
        this.detailedCode = detailedCode;
    }

    public StatV1CustomPublishersLastVisitSchema withDetailedCode(String detailedCode) {
        this.detailedCode = detailedCode;
        return this;
    }

    @JsonProperty("errors")
    public List<ApiError> getErrors() {
        return errors;
    }

    @JsonProperty("errors")
    public void setErrors(List<ApiError> errors) {
        this.errors = errors;
    }

    public StatV1CustomPublishersLastVisitSchema withErrors(List<ApiError> errors) {
        this.errors = errors;
        return this;
    }

    @JsonProperty("message")
    public String getMessage() {
        return message;
    }

    @JsonProperty("message")
    public void setMessage(String message) {
        this.message = message;
    }



    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder().append(last).append(profile).append(code).append(detailedCode).append(errors).append(message).toHashCode();
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if (!(other instanceof StatV1CustomPublishersLastVisitSchema)) {
            return false;
        }
        StatV1CustomPublishersLastVisitSchema rhs = ((StatV1CustomPublishersLastVisitSchema) other);
        return new EqualsBuilder().append(last, rhs.last).append(profile, rhs.profile).append(code, rhs.code).append(detailedCode, rhs.detailedCode).append(errors, rhs.errors).append(message, rhs.message).isEquals();
    }
}
