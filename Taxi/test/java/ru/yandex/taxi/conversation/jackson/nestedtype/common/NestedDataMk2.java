package ru.yandex.taxi.conversation.jackson.nestedtype.common;

import java.util.Objects;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class NestedDataMk2 {

    private final String payload;
    private final Long length;

    @JsonCreator
    public NestedDataMk2(@JsonProperty("payload") String payload, @JsonProperty("length") Long length) {
        this.payload = payload;
        this.length = length;
    }

    public String getPayload() {
        return payload;
    }

    public Long getLength() {
        return length;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        NestedDataMk2 that = (NestedDataMk2) o;
        return Objects.equals(payload, that.payload) && Objects.equals(length, that.length);
    }

    @Override
    public int hashCode() {
        return Objects.hash(payload, length);
    }
}
