package ru.yandex.taxi.conversation.jackson.nestedtype.common;

import java.util.Objects;

public abstract class WithNestedTypeMk1 {

    private final String id;
    private final NestedId nestedId;

    private final String title;
    private final NestedDataMk1 nestedData;

    protected WithNestedTypeMk1(String id, NestedId nestedId, String title, NestedDataMk1 nestedData) {
        this.id = id;
        this.nestedId = nestedId;
        this.title = title;
        this.nestedData = nestedData;
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public NestedId getNestedId() {
        return nestedId;
    }

    public NestedDataMk1 getNestedData() {
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
        WithNestedTypeMk1 that = (WithNestedTypeMk1) o;
        return Objects.equals(id, that.id) && Objects.equals(nestedId, that.nestedId) && Objects.equals(title,
                that.title) && Objects.equals(nestedData, that.nestedData);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, nestedId, title, nestedData);
    }
}
