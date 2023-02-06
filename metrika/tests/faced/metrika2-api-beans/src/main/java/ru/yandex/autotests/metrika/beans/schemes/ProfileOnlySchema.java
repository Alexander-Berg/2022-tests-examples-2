package ru.yandex.autotests.metrika.beans.schemes;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import ru.yandex.metrika.api.error.ga.GAConstructorError;
import ru.yandex.metrika.spring.profile.ProfileData;

/**
 * Created by konkov on 09.06.2017.
 */
public class ProfileOnlySchema {

    @JsonProperty("code")
    private Long code;

    /**
     *
     * @return
     *     The code
     */
    @JsonProperty("code")
    public Long getCode() {
        return code;
    }

    /**
     *
     * @param code
     *     The code
     */
    @JsonProperty("code")
    public void setCode(Long code) {
        this.code = code;
    }

    @JsonProperty("error")
    private GAConstructorError error;

    /**
     *
     * @return
     *     The error
     */
    @JsonProperty("error")
    public GAConstructorError getError() {
        return error;
    }

    /**
     *
     * @param error
     *     The error
     */
    @JsonProperty("error")
    public void setError(GAConstructorError error) {
        this.error = error;
    }

    @JsonProperty("_profile")
    private ProfileData profile;

    /**
     *
     * @return
     *     The profile
     */
    @JsonProperty("_profile")
    public ProfileData getProfile() {
        return profile;
    }

    /**
     *
     * @param profile
     *     The _profile
     */
    @JsonProperty("_profile")
    public void setProfile(ProfileData profile) {
        this.profile = profile;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder()
                .append(code)
                .append(profile)
                .toHashCode();
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if (!(other instanceof ProfileOnlySchema)) {
            return false;
        }
        ProfileOnlySchema rhs = ((ProfileOnlySchema) other);
        return new EqualsBuilder()
                .append(profile, rhs.profile)
                .append(code, rhs.code)
                .isEquals();
    }

}
