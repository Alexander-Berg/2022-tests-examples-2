package ru.yandex.autotests.metrika.reportwrappers;

import com.google.common.collect.ImmutableMap;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;

import java.lang.reflect.Constructor;
import java.util.Map;

/**
 * Created by konkov on 04.08.2016.
 */
public final class ReportFactory {

    private static final Map<Class<?>, Class<? extends Report>> responseReportMapping = ImmutableMap.<Class<?>, Class<? extends Report>>builder()
            .put(StatV1DataGETSchema.class, TableReport.class)
            .put(StatV1DataBytimeGETSchema.class, BytimeReport.class)
            .put(StatV1DataComparisonGETSchema.class, ComparisonReport.class)
            .put(StatV1DataDrilldownGETSchema.class, DrilldownReport.class)
            .put(StatV1DataComparisonDrilldownGETSchema.class, ComparisonDrilldownReport.class)
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
