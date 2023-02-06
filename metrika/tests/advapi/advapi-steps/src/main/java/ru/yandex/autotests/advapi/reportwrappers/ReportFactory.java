package ru.yandex.autotests.advapi.reportwrappers;

import com.google.common.collect.ImmutableMap;
import ru.yandex.advapi.V1StatDataBytimeGETSchema;
import ru.yandex.advapi.V1StatDataDrilldownGETSchema;
import ru.yandex.advapi.V1StatDataGETSchema;
import ru.yandex.autotests.advapi.exceptions.MetrikaApiException;

import java.lang.reflect.Constructor;
import java.util.Map;

/**
 * Created by konkov on 04.08.2016.
 */
public final class ReportFactory {

    private static final Map<Class<?>, Class<? extends Report>> responseReportMapping = ImmutableMap.<Class<?>, Class<? extends Report>>builder()
            .put(V1StatDataGETSchema.class, TableReport.class)
            .put(V1StatDataBytimeGETSchema.class, BytimeReport.class)
            .put(V1StatDataDrilldownGETSchema.class, DrilldownReport.class)
            .build();

    public static Report create(Class<?> responseClass, Object report) {
        Class<? extends Report> reportClass = responseReportMapping.get(responseClass);

        if (reportClass == null) {
            throw new MetrikaApiException("Не удалось создать обёртку для бина: неизвестный тип бина");
        }

        try {
            Constructor<? extends Report> reportClassConstructor = reportClass.getConstructor(responseClass);
            return reportClassConstructor.newInstance(report);
        } catch (Exception e) {
            throw new MetrikaApiException("Не удалось создать обёртку для бина", e);
        }
    }

}
