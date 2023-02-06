package ru.yandex.taxi.conversation.jackson.nestedtype.negative;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedType;

@JsonTypeInfo(
        use = JsonTypeInfo.Id.NAME,
        include = JsonTypeInfo.As.EXISTING_PROPERTY,
        property = "nestedId.not_found.id",
        visible = true)
@JsonSubTypes({
        @JsonSubTypes.Type(value = TypeErrMk1.class, name = "mk1_l2"),
        @JsonSubTypes.Type(value = TypeErrMk2.class, name = "mk2_l2")})
public interface NestedTypeMissed extends NestedType {
}
