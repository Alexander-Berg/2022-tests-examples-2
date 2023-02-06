package com.yandex.tv.services.testapp;

import androidx.annotation.NonNull;

import com.yandex.tv.services.common.annotations.AndroidService;

@AndroidService
public interface TestServiceApi {

    @NonNull
    String getConstantString();

    void crash();

    void nonExistentMethod();

    void dummyInBinder(QuasarBinder iBinder);
}
