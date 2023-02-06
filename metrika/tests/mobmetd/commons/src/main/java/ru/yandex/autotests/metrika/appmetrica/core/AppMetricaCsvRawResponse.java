package ru.yandex.autotests.metrika.appmetrica.core;

import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

/**
 * Минимально обработанные данные ответа csv rest метода
 *
 * @author dancingelf
 */
public class AppMetricaCsvRawResponse {

    private final List<String> headers;
    private final List<List<String>> content;

    public AppMetricaCsvRawResponse(List<String> headers, List<List<String>> content) {
        this.headers = headers;
        this.content = content;
    }

    public List<String> getHeaders() {
        return headers;
    }

    public List<List<String>> getContent() {
        return content;
    }

    public <T> AppMetricaCsvResponse<T> withMapper(Function<List<String>, T> mapper) {
        final List<T> typedContent = new ArrayList<>();
        for (int i = 0; i < content.size(); ++i) {
            final List<String> row = content.get(i);
            try {
                typedContent.add(mapper.apply(row));
            } catch (Exception ex) {
                throw new AppMetricaException(
                        "Не удалось преобразовать в объект строку csv файла: " +
                        "номер строки=" + (i + 1) + ", строка=" + row, ex);
            }
        }
        return new AppMetricaCsvResponse<T>(headers, typedContent);
    }
}
