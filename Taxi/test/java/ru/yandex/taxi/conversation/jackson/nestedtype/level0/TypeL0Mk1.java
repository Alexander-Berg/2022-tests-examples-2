package ru.yandex.taxi.conversation.jackson.nestedtype.level0;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedDataMk1;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedId;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.WithNestedTypeMk1;

public class TypeL0Mk1 extends WithNestedTypeMk1 implements NestedTypeLevel0 {

    @JsonCreator
    public TypeL0Mk1(@JsonProperty("id") String id,
                     @JsonProperty("nestedId") NestedId nestedId,
                     @JsonProperty("title") String title,
                     @JsonProperty("nestedData") NestedDataMk1 nestedData) {
        super(id, nestedId, title, nestedData);
    }



}
