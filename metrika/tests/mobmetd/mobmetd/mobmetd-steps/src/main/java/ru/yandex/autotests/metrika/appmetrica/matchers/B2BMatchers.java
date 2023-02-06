package ru.yandex.autotests.metrika.appmetrica.matchers;

import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;

import static ru.yandex.autotests.metrika.appmetrica.matchers.DoubleValueDiffer.DEFAULT_EPSILON;

/**
 * Матчеры для B2B тестов отчётов
 */
public class B2BMatchers {

    public static <T> Matcher<T> similarTo(T referenceBean) {
        BeanFieldPath[] ignoredFields = AppMetricaApiProperties.apiProperties().getB2bIgnoredFields();
        return similarTo(referenceBean, new BeanFieldPath[]{}, ignoredFields, DEFAULT_EPSILON);
    }

    public static <T> Matcher<T> similarTo(T referenceBean,
                                           BeanFieldPath[] volatileFields,
                                           BeanFieldPath[] ignoredFields) {
        return similarTo(referenceBean, volatileFields, ignoredFields, DEFAULT_EPSILON);
    }

    /**
     * Проверяем совпадение полей.
     * Для указанных путей и для Double полей проверяем неточное совпадение.
     */
    public static <T> Matcher<T> similarTo(T referenceBean,
                                           BeanFieldPath[] additionalVolatileFields,
                                           BeanFieldPath[] additionalIgnoredFields,
                                           double epsilon) {
        return BeanDifferMatcher.beanDiffer(referenceBean).
                useCompareStrategy(
                        DefaultCompareStrategies.allFieldsExcept(additionalIgnoredFields)
                                .forClasses(Double.class)
                                .useDiffer(new DoubleValueDiffer(epsilon))
                                .forFields(additionalVolatileFields)
                                .useDiffer(new DoubleValueDiffer(epsilon))
                );
    }
}
