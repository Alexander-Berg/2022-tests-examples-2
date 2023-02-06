package ru.yandex.taxi.conversation.jackson.nestedtype.common;

import java.util.Objects;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class NestedId {

    private String id;
    private String description;
    private NestedId nestedId;

    @JsonCreator
    public NestedId(@JsonProperty("id") String id,
                    @JsonProperty("description") String description,
                    @JsonProperty("nestedId") NestedId nestedId) {
        this.id = id;
        this.description = description;
        this.nestedId = nestedId;
    }

    public NestedId(String id, String description) {
        this.id = id;
        this.description = description;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public NestedId getNestedId() {
        return nestedId;
    }

    public void setNestedId(NestedId nestedId) {
        this.nestedId = nestedId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        NestedId nestedId1 = (NestedId) o;
        return Objects.equals(id, nestedId1.id) && Objects.equals(description, nestedId1.description) && Objects.equals(nestedId, nestedId1.nestedId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, description, nestedId);
    }
}
