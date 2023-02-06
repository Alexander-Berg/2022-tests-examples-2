package ru.yandex.autotests.metrika.beans;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import ru.yandex.metrika.api.error.ApiError;
import ru.yandex.metrika.spring.profile.ProfileData;

import java.util.ArrayList;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
        "_profile",
        "code",
        "common_segments",
        "detailed_code",
        "errors",
        "message",
        "usercentric_segments"
})
public class StatV1MetadataUserAndCommonSegmentsGETSchemaCopy {

    @JsonProperty("_profile")
    private ProfileData profile;
    @JsonProperty("code")
    private Long code;
    @JsonProperty("common_segments")
    private List<CustomTree> commonSegments;
    @JsonProperty("detailed_code")
    private String detailedCode;
    @JsonProperty("errors")
    private List<ApiError> errors = new ArrayList<ApiError>();
    @JsonProperty("message")
    private String message;
    @JsonProperty("usercentric_segments")
    private List<CustomTree> usercentricSegments;

    @JsonProperty("_profile")
    public ProfileData getProfile() {
        return profile;
    }

    @JsonProperty("_profile")
    public void setProfile(ProfileData profile) {
        this.profile = profile;
    }

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withProfile(ProfileData profile) {
        this.profile = profile;
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

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withCode(Long code) {
        this.code = code;
        return this;
    }

    @JsonProperty("common_segments")
    public List<CustomTree> getCommonSegments() {
        return commonSegments;
    }

    @JsonProperty("common_segments")
    public void setCommonSegments(List<CustomTree> commonSegments) {
        this.commonSegments = commonSegments;
    }

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withCommonSegments(List<CustomTree> commonSegments) {
        this.commonSegments = commonSegments;
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

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withDetailedCode(String detailedCode) {
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

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withErrors(List<ApiError> errors) {
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

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withMessage(String message) {
        this.message = message;
        return this;
    }

    @JsonProperty("usercentric_segments")
    public List<CustomTree> getUsercentricSegments() {
        return usercentricSegments;
    }

    @JsonProperty("usercentric_segments")
    public void setUsercentricSegments(List<CustomTree> usercentricSegments) {
        this.usercentricSegments = usercentricSegments;
    }

    public StatV1MetadataUserAndCommonSegmentsGETSchemaCopy withUsercentricSegments(List<CustomTree> usercentricSegments) {
        this.usercentricSegments = usercentricSegments;
        return this;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder().append(profile).append(code).append(commonSegments).append(detailedCode).append(errors).append(message).append(usercentricSegments).toHashCode();
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof StatV1MetadataUserAndCommonSegmentsGETSchemaCopy) == false) {
            return false;
        }
        StatV1MetadataUserAndCommonSegmentsGETSchemaCopy rhs = ((StatV1MetadataUserAndCommonSegmentsGETSchemaCopy) other);
        return new EqualsBuilder().append(profile, rhs.profile).append(code, rhs.code).append(commonSegments, rhs.commonSegments).append(detailedCode, rhs.detailedCode).append(errors, rhs.errors).append(message, rhs.message).append(usercentricSegments, rhs.usercentricSegments).isEquals();
    }

}
