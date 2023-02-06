package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;

import javax.annotation.Nullable;

public class SKAdConversionValueConfigWrapper {

    @Nullable
    private final SKAdCVConfig config;

    public static SKAdConversionValueConfigWrapper wrap(@Nullable SKAdCVConfig config) {
        return new SKAdConversionValueConfigWrapper(config);
    }

    public SKAdConversionValueConfigWrapper(@Nullable SKAdCVConfig config) {
        this.config = config;
    }

    @Nullable
    public SKAdCVConfig getConfig() {
        return config;
    }

    @Override
    public String toString() {
        return config == null ? "no config" : config.getModelType().toString();
    }
}
