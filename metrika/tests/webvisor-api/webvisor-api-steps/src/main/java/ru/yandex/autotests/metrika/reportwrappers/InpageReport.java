package ru.yandex.autotests.metrika.reportwrappers;

import java.util.List;

import ru.yandex.metrika.api.error.ApiError;

/**
 * Общий интерфейс для Inpage
 *
 * Created by sonick on 19.12.16.
 */
public interface InpageReport {

    /**
     * @return The code.
     */
    Long getCode();

    /**
     * @return The errors.
     */
    List<ApiError> getErrors();

    /**
     * @return Максимальная доля данных, по которой осуществляется расчет. Доступно значение в пределах от 0 до 1.
     */
    Double getMaxSampleShare();

    /**
     * @return Признак семплирования. Показывает, был ли применен семплинг. Возможные значения: true, false.
     */
    Boolean getSampleable();

    /**
     * @return Доля данных, по которым осуществлялся расчет. Доступно значение в пределах от 0 до 1.
     */
    Double getSampleShare();

    /**
     * @return The Message.
     */
    String getMessage();

}
