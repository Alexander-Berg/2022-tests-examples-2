package ru.yandex.autotests.internalapid.util;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.Arrays;
import java.util.stream.Collectors;

public class RestUtils {
    public static String buildBody(IFormParameters... parameters) {
        return Arrays.stream(parameters).flatMap(it -> it.getParameters().stream()).map(it -> it.getName() + "=" + it.getValue())
                .collect(Collectors.joining("&"));
    }
}
