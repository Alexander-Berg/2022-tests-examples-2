package ru.yandex.taxi.conversation.jackson.nestedtype.level1;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedType;

@JsonTypeInfo(
        use = JsonTypeInfo.Id.NAME,
        include = JsonTypeInfo.As.WRAPPER_OBJECT,
        property = "nestedId.id",
        visible = true)
@JsonSubTypes({
        @JsonSubTypes.Type(value = TypeL1Mk1.class, name = "mk1_l1"),
        @JsonSubTypes.Type(value = TypeL1Mk2.class, name = "mk2_l1")})
public interface NestedTypeLevel1 extends NestedType {
}
