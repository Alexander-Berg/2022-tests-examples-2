package ru.yandex.metrika.direct.dict.utils;

import java.util.function.BiConsumer;

import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;

public class ResultWithCallback<T> implements Answer<T> {
    private final BiConsumer<T, InvocationOnMock> callback;

    public ResultWithCallback(BiConsumer<T, InvocationOnMock> callback) {
        this.callback = callback;
    }

    @Override
    public T answer(InvocationOnMock invocationOnMock) throws Throwable {
        var result = (T) invocationOnMock.callRealMethod();
        callback.accept(result, invocationOnMock);
        return result;
    }
}
