package ru.yandex.autotests.metrika.appmetrica.matchers;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;

import java.util.stream.Stream;

import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;

public class ProfileB2BMatchers {

    public static final String ANY_NUMBER = "\\d+";

    /**
     * Слегка больше значения по умолчанию, потому что данные в профили будут постоянно доезжать
     */
    public static final double PROFILES_EPSILON = 0.05;

    /**
     * Значение метрик может меняться, так как это профили. Чтобы постоянно не падать мы помечаем нужные поля
     * как волатильные. Но пути в бинах не поддерживают регулярные выражения, поэтому приходится руками прописывать
     * все пути.
     */
    private static final BeanFieldPath[] PROFILES_REPORT_VOLATILE_FIELDS = Stream.of(
                    newPath("totalRows"),
                    newPath("min", ANY_NUMBER),
                    newPath("max", ANY_NUMBER),
                    newPath("data", "metrics", ANY_NUMBER),
                    newPath("data", "metrics", ANY_NUMBER, ANY_NUMBER)
            )
            .toArray(BeanFieldPath[]::new);

    private static final BeanFieldPath[] PROFILES_VOLATILE_FIELDS = Stream.of(
                    newPath("totalRows"),
                    newPath("min", ANY_NUMBER),
                    newPath("max", ANY_NUMBER),
                    newPath("totals", ANY_NUMBER),
                    newPath("data", "metrics", ANY_NUMBER)
            )
            .toArray(BeanFieldPath[]::new);

    public static <T> Matcher<T> similarProfiles(T referenceBean) {
        BeanFieldPath[] ignoredFields = AppMetricaApiProperties.apiProperties().getB2bIgnoredFields();
        return B2BMatchers.similarTo(referenceBean, PROFILES_VOLATILE_FIELDS, ignoredFields, PROFILES_EPSILON);
    }

    public static <T> Matcher<T> similarProfilesReport(T referenceBean) {
        BeanFieldPath[] ignoredFields = AppMetricaApiProperties.apiProperties().getB2bIgnoredFields();
        return B2BMatchers.similarTo(referenceBean, PROFILES_REPORT_VOLATILE_FIELDS, ignoredFields, PROFILES_EPSILON);
    }
}
