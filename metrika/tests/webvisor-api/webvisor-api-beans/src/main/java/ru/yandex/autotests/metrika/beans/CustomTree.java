package ru.yandex.autotests.metrika.beans;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import ru.yandex.metrika.segments.core.meta.segment.ApiSegmentMetadata;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
        "chld",
        "empty"
})
public class CustomTree extends ApiSegmentMetadata{

    @JsonProperty("chld")
    private List<CustomTree> chld = new ArrayList<CustomTree>();
    @JsonProperty("empty")
    private Boolean empty;

    @JsonProperty("chld")
    public List<CustomTree> getChld() {
        return chld;
    }

    @JsonProperty("chld")
    public void setChld(List<CustomTree> chld) {
        this.chld = chld;
    }

    public CustomTree withChld(List<CustomTree> chld) {
        this.chld = chld;
        return this;
    }

    @JsonProperty("empty")
    public Boolean getEmpty() {
        return empty;
    }

    @JsonProperty("empty")
    public void setEmpty(Boolean empty) {
        this.empty = empty;
    }

    public CustomTree withEmpty(Boolean empty) {
        this.empty = empty;
        return this;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder().append(chld).append(empty).toHashCode();
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof CustomTree) == false) {
            return false;
        }
        CustomTree rhs = ((CustomTree) other);
        return new EqualsBuilder().append(chld, rhs.chld).append(empty, rhs.empty).isEquals();
    }

    public List<CustomTree> flattened() {
        return stream().collect(toList());
    }

    public Stream<CustomTree> stream() {
        return Stream.concat(
                Stream.of(this),
                chld.stream().flatMap(CustomTree::stream));
    }

}