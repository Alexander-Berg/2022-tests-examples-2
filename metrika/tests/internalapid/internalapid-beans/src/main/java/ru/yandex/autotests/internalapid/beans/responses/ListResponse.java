package ru.yandex.autotests.internalapid.beans.responses;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

public class ListResponse<T> extends InternalApidResponse {
    private List<T> result = new ArrayList<>();

    public List<T> getResult() {
        return result;
    }

    public void setResult(List<T> result) {
        this.result = result;
    }

    public ListResponse<T> withResult(List<T> result) {
        this.result = result;
        return this;
    }

    public void parseFromList(List<?> list, Function<Object, T> valueParser) {
        result = list.stream().map(valueParser).collect(Collectors.toList());
    }
}
