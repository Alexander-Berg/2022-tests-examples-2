package ru.yandex.quasar.app.webview;

import org.junit.Test;

import java.lang.reflect.Field;

import static org.junit.Assert.assertEquals;

public class LoadingStateTest {
    @Test
    public void shouldBeCorrespondingEnum() throws  IllegalAccessException {
        for (Field field : WebViewWrapper.LoadingState.class.getFields()) {
            WebViewWrapper.LoadingStateEnum state = WebViewWrapper.LoadingStateEnum.valueOf(field.getName());
            assertEquals(state.ordinal(), field.getInt(null));
        }
        assertEquals(WebViewWrapper.LoadingState.class.getFields().length, WebViewWrapper.LoadingStateEnum.values().length);
    }
}
