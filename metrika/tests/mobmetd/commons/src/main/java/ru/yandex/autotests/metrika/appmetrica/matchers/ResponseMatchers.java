package ru.yandex.autotests.metrika.appmetrica.matchers;

import com.google.common.collect.ImmutableMap;
import org.hamcrest.Matcher;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.autotests.irt.testutils.beandiffer2.differ.Differ;

import java.util.Collections;
import java.util.Map;

import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;

/**
 * Created by konkov on 05.05.2016.
 */
public class ResponseMatchers {

    public static <T> Matcher<T> equivalentTo(T bean) {
        return equivalentTo(bean, Collections.emptyMap());
    }

    public static <T> Matcher<T> approximatelyEquivalentTo(T bean, double epsilon) {
        return equivalentTo(bean, ImmutableMap.of(Double.class, new DoubleValueDiffer(epsilon)));
    }

    public static <T> Matcher<T> equivalentTo(T referenceBean, Map<Class, Differ> differs) {
        DefaultCompareStrategy compareStrategy = DefaultCompareStrategies.onlyExpectedFields();
        differs.forEach((cl, differ) -> compareStrategy.forClasses(cl).useDiffer(differ));

        return beanDiffer(referenceBean).useCompareStrategy(compareStrategy);
    }

    public static <T> Matcher<T> equivalentTo(T referenceBean,
                                              Map<Class, Differ> customClassesDiffers,
                                              Map<String, Differ> customFieldsDiffers) {
        DefaultCompareStrategy compareStrategy = DefaultCompareStrategies.onlyExpectedFields();
        customClassesDiffers.forEach((cl, differ) -> compareStrategy.forClasses(cl).useDiffer(differ));
        customFieldsDiffers.forEach(
                (fieldPath, differ) -> compareStrategy.forFields(newPath(fieldPath)).useDiffer(differ)
        );

        return beanDiffer(referenceBean).useCompareStrategy(compareStrategy);
    }
}
