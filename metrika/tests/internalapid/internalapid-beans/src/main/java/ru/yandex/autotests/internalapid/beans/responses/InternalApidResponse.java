package ru.yandex.autotests.internalapid.beans.responses;

import com.google.common.collect.ImmutableMap;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;

public class InternalApidResponse<K, V> {

    private Integer code;
    private String message;
    private Object errors;

    private Map<K, V> remaining = new HashMap<>();

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public boolean hasErrors() {
        return errors != null;
    }

    public void setErrors(Object errors) {
        this.errors = errors;
    }

    public Object getErrors() {
        return errors;
    }

    public V getValue(K key) {
        return remaining.get(key);
    }

    public Map<K, V> getRemaining() {
        return ImmutableMap.copyOf(remaining);
    }

    public void parseFromMap(Map<?, ?> data, Function<Object, K> keyParser, Function<Object, V> valueParser) {
        if (data.containsKey("errors")) {
            this.errors = data.get("errors");
            data.remove(errors);
        }
        if (data.containsKey("message")) {
            this.message = data.get("message").toString();
            data.remove("message");
        }
        if (data.containsKey("code")) {
            this.code = Integer.valueOf((data.get("code").toString()));
            data.remove("code");
        }

        for (Iterator iterator = data.entrySet().iterator(); iterator.hasNext(); ) {
            Map.Entry entry = (Map.Entry) iterator.next();
            try {
                remaining.put(keyParser.apply(entry.getKey()), valueParser.apply(entry.getValue()));
                iterator.remove();
            } catch (Exception e) {
                //ignore errors in parsing
            }

        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        InternalApidResponse<?, ?> that = (InternalApidResponse<?, ?>) o;
        return Objects.equals(code, that.code) &&
                Objects.equals(message, that.message) &&
                Objects.equals(errors, that.errors) &&
                Objects.equals(remaining, that.remaining);
    }

    @Override
    public int hashCode() {
        return Objects.hash(code, message, errors, remaining);
    }
}
