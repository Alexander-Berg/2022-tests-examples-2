package ru.yandex.taxi.conversation.jackson.nestedtype.common;

import java.util.Objects;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class NestedDataMk1 {

    private final String data;
    private final String encoding;

    @JsonCreator
    public NestedDataMk1(@JsonProperty("data") String data, @JsonProperty("encoding") String encoding) {
        this.data = data;
        this.encoding = encoding;
    }

    public String getData() {
        return data;
    }

    public String getEncoding() {
        return encoding;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        NestedDataMk1 that = (NestedDataMk1) o;
        return Objects.equals(data, that.data) && Objects.equals(encoding, that.encoding);
    }

    @Override
    public int hashCode() {
        return Objects.hash(data, encoding);
    }
}
