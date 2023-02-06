package ru.yandex.autotests.topsites.data.parameters;

import javax.annotation.Nullable;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class ParamUtils {

    @Nullable
    public static String joinToString(@Nullable List<?> list) {
        return Optional.ofNullable(list)
                .map(l -> l.stream().map(Object::toString).collect(Collectors.joining(",")))
                .orElse(null);
    }
}
