package ru.yandex.autotests.metrika.beans.schemes;

import org.apache.commons.beanutils.PropertyUtils;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiWrapperException;

import java.util.List;

/**
 * Created by konkov on 25.03.2015.
 */
public class ResponseWrapper<T> {

    private final T object;

    public static <V> ResponseWrapper<V> wrap(V wrappedObject) {
        return new ResponseWrapper<>(wrappedObject);
    }

    public ResponseWrapper(T wrappedObject) {
        object = wrappedObject;
    }

    private <U> U getCheckedProperty(String propertyName) {
        try {
            return (U) PropertyUtils.getProperty(object, propertyName);
        } catch (Throwable e) {
            throw new MetrikaApiWrapperException(String.format("Ошибка при доступе к свойству %s", propertyName), e);
        }
    }

    public Boolean getWithConfidence() {
        return getCheckedProperty("withConfidence");
    }

    public Boolean getExcludeInsignificant() {
        return getCheckedProperty("excludeInsignificant");
    }

    public List<Object> getData() {
        return getCheckedProperty("data");
    }

    public Long getSampleSpace() {
        return getCheckedProperty("sampleSpace");
    }

    public Long getSampleSize() {
        return getCheckedProperty("sampleSize");
    }

    public Double getSampleShare() {
        return getCheckedProperty("sampleShare");
    }

    public Double getMaxSampleShare() {
        return getCheckedProperty("maxSampleShare");
    }

    public Double getMaxSampleShareForInpageClick() {
        return getCheckedProperty("data.maxSampleShare");
    }

    public List<String> getQuerySort() {
        return getCheckedProperty("query.sort");
    }
}
