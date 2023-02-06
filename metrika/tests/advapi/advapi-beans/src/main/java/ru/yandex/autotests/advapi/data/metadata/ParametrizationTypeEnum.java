package ru.yandex.autotests.advapi.data.metadata;

import java.util.stream.Stream;

/**
 * Created by konkov on 15.08.2014.
 * Перечисление всех возможных типов параметризации
 */
public enum ParametrizationTypeEnum {

    GOAL_ID("goal_id"),
    GROUP("group"),
    ATTRIBUTION("attribution"),
    QUANTILE("quantile"),
    CURRENCY("currency"),
    OFFLINE_REGION("offline_region"),
    OFFLINE_POINT("offline_point"),
    OFFLINE_WINDOW("offline_window"),
    EXPERIMENT("experiment_ab");

    private final String parameterName;

    ParametrizationTypeEnum(String parameterName){

        this.parameterName = parameterName;
    }

    /**
     * @return строка для замены на значение параметра в наименовании
     */
    public String getPlaceholder(){
        return String.format("<%s>", parameterName);
    }

    /**
     * @return строка с наименованием параметра для использования в строке запроса
     */
    public String getParameterName() {
        return parameterName;
    }

    public static Stream<ParametrizationTypeEnum> stream() {
        return Stream.of(values());
    }
}
