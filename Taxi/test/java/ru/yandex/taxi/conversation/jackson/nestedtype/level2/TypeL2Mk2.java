package ru.yandex.taxi.conversation.jackson.nestedtype.level2;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedDataMk2;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedId;
import ru.yandex.taxi.conversation.jackson.nestedtype.common.WithNestedTypeMk2;

public class TypeL2Mk2 extends WithNestedTypeMk2 implements NestedTypeLevel2 {

    @JsonCreator
    public TypeL2Mk2(@JsonProperty("id") String id,
                     @JsonProperty("nestedId") NestedId nestedId,
                     @JsonProperty("number") Long number,
                     @JsonProperty("nestedData") NestedDataMk2 nestedData) {
        super(id, nestedId, number, nestedData);
    }
}
