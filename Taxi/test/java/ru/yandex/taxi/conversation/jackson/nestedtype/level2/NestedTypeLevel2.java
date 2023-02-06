package ru.yandex.taxi.conversation.jackson.nestedtype.level2;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedType;

@JsonTypeInfo(
        use = JsonTypeInfo.Id.NAME,
        include = JsonTypeInfo.As.EXISTING_PROPERTY,
        property = "nestedId.nestedId.id",
        visible = true)
@JsonSubTypes({
        @JsonSubTypes.Type(value = TypeL2Mk1.class, name = "mk1_l2"),
        @JsonSubTypes.Type(value = TypeL2Mk2.class, name = "mk2_l2")})
public interface NestedTypeLevel2 extends NestedType {
}
