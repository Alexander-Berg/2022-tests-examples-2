package ru.yandex.metrika.schedulerd.helpers;

import com.google.common.collect.ImmutableMap;

public interface ConfigHelper {

    default void addConfigArgs(ImmutableMap.Builder<String, String> configBuilder) {
    }

    default void apply() {
    }

}
