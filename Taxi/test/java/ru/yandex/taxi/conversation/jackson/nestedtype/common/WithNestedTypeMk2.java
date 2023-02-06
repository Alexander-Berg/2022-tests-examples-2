package ru.yandex.taxi.conversation.jackson.nestedtype.common;

import java.util.Objects;

public abstract class WithNestedTypeMk2 {

    private final String id;
    private final NestedId nestedId;

    private final Long number;
    private final NestedDataMk2 nestedData;

    protected WithNestedTypeMk2(String id, NestedId nestedId, Long number, NestedDataMk2 nestedData) {
        this.id = id;
        this.nestedId = nestedId;
        this.number = number;
        this.nestedData = nestedData;
    }

    public String getId() {
        return id;
    }

    public NestedId getNestedId() {
        return nestedId;
    }

    public Long getNumber() {
        return number;
    }

    public NestedDataMk2 getNestedData() {
        return nestedData;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        WithNestedTypeMk2 that = (WithNestedTypeMk2) o;
        return Objects.equals(id, that.id) && Objects.equals(nestedId, that.nestedId) && Objects.equals(number,
                that.number) && Objects.equals(nestedData, that.nestedData);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, nestedId, number, nestedData);
    }
}
