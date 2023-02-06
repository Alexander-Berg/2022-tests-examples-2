package ru.yandex.autotests.metrika.appmetrica.parameters;

import org.apache.http.NameValuePair;
import org.apache.http.message.BasicNameValuePair;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;

import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.Collections.emptyList;
import static org.apache.commons.lang3.StringUtils.isNotEmpty;

/**
 * Параметры запроса, в свободном виде. Наименования - произвольные строки.
 */
public class FreeFormParameters extends HashMap<String, String> implements IFormParameters {

    /**
     * Константа пустого списка - не следует ее модифицировать.
     * Вместо этого используем new FreeFormParameters().append...
     * или makeParameters().append...
     */
    public static final IFormParameters EMPTY = () -> emptyList();

    @Override
    public List<NameValuePair> getParameters() {
        return entrySet().stream()
                .filter(entry -> isNotEmpty(entry.getValue()))
                .map(entry -> new BasicNameValuePair(entry.getKey(), entry.getValue()))
                .collect(Collectors.toList());
    }

    public <T> FreeFormParameters append(String key, T value) {
        put(key, Objects.toString(value, null));
        return this;
    }

    public FreeFormParameters append(IFormParameters parameters) {
        if (parameters != null) {
            parameters.getParameters().forEach(p -> append(p));
        }
        return this;
    }

    public FreeFormParameters append(IFormParameters... parameters) {
        if (parameters != null) {
            Stream.of(parameters).flatMap(p -> p.getParameters().stream()).forEach(p -> append(p));
        }
        return this;
    }

    public FreeFormParameters append(NameValuePair nameValuePair) {
        if (nameValuePair != null) {
            put(nameValuePair.getName(), nameValuePair.getValue());
        }
        return this;
    }

    public static <T> FreeFormParameters makeParameters(String key, T value) {
        return makeParameters().append(key, Objects.toString(value, null));
    }

    public static FreeFormParameters makeParameters() {
        return new FreeFormParameters();
    }
}
