package ru.yandex.taxi.conversation.jackson.nestedtype.common;

import com.fasterxml.jackson.databind.annotation.JsonTypeResolver;

import ru.yandex.taxi.conversation.utils.jackson.NestedTypeResolver;

@JsonTypeResolver(NestedTypeResolver.class)
public interface NestedType {

    String getId();

    NestedId getNestedId();

}
