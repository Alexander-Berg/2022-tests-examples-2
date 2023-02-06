package ru.yandex.autotests.metrika.matchers.chartannotation;

import org.hamcrest.Matcher;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationGroup;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationUserGroup;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaReportChartAnnotation;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

public class ChartAnnotationMatchers {

    public static Matcher<MetrikaReportChartAnnotation> matchesChartAnnotation(MetrikaChartAnnotation chartAnnotation) {
        return beanEquivalent(convertToReportAnnotation(chartAnnotation));
    }

    private static MetrikaReportChartAnnotation convertToReportAnnotation(MetrikaChartAnnotation annotation) {
        return new MetrikaReportChartAnnotation()
                .withId(annotation.getId())
                .withDate(annotation.getDate())
                .withTime(annotation.getTime())
                .withTitle(annotation.getTitle())
                .withMessage(annotation.getMessage())
                .withGroup(convertToAnnotationGroup(annotation.getGroup()));
    }

    private static ChartAnnotationGroup convertToAnnotationGroup(ChartAnnotationUserGroup userGroup) {
        if (userGroup == null) {
            return null;
        }
        switch (userGroup) {
            case A:
                return ChartAnnotationGroup.A;
            case B:
                return ChartAnnotationGroup.B;
            case C:
                return ChartAnnotationGroup.C;
            case D:
                return ChartAnnotationGroup.D;
            case E:
                return ChartAnnotationGroup.E;
            default:
                return null;
        }
    }
}
