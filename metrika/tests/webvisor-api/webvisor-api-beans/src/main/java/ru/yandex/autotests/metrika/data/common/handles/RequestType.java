package ru.yandex.autotests.metrika.data.common.handles;

import java.util.Objects;

/**
 * Описание вида отчета, совмещает в себе адрес ручки и класс, который используется для парсинга ответа.
 *
 * Created by konkov on 13.07.2016.
 */
public class RequestType<ResponseClass> {

    private final String title;
    private final Class<ResponseClass> responseClass;
    private final String path;

    public RequestType(String title, Class<ResponseClass> responseClass, String path) {

        this.title = title;
        this.responseClass = responseClass;
        this.path = path;
    }

    public Class<ResponseClass> getResponseClass() {
        return responseClass;
    }

    public String getPath() {
        return path;
    }

    public String getTitle() {
        return title;
    }

    @Override
    public String toString() {
        return getTitle();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RequestType<?> that = (RequestType<?>) o;
        return Objects.equals(title, that.title) &&
                Objects.equals(responseClass, that.responseClass) &&
                Objects.equals(path, that.path);
    }

    @Override
    public int hashCode() {
        return Objects.hash(title, responseClass, path);
    }

    static <T> RequestType<T> report(String title, Class<T> responseClass, String path) {
        return new RequestType<>(title, responseClass, path);
    }

}
