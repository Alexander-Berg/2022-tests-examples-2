package ru.yandex.taxi.conversation.jackson.nestedtype.level0;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;

import ru.yandex.taxi.conversation.jackson.nestedtype.common.NestedType;

@JsonTypeInfo(
        use = JsonTypeInfo.Id.NAME,
        include = JsonTypeInfo.As.EXISTING_PROPERTY,
        property = "id",
        visible = true)
@JsonSubTypes({
        @JsonSubTypes.Type(value = TypeL0Mk1.class, name = "mk1"),
        @JsonSubTypes.Type(value = TypeL0Mk2.class, name = "mk2")})
public interface NestedTypeLevel0 extends NestedType {

}
