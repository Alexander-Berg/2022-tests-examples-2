package ru.yandex.autotests.metrika.steps.internal;

import java.util.Map;

import com.google.gson.reflect.TypeToken;

import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.qatools.allure.annotations.Step;

/**
 * Created by sourx on 04.02.2016.
 */
public class InternalSteps extends MetrikaBaseSteps {

    @Step("Получить JSON-схемы для сравнения")
    public Map<String, Object> getSchemas() {
        return executeAsJson(getRequestBuilder("/internal/schema").get())
                .readResponse((Class<Map<String, Object>>)
                        new TypeToken<Map<String, Object>>() {
                        }.getRawType());
    }

}
