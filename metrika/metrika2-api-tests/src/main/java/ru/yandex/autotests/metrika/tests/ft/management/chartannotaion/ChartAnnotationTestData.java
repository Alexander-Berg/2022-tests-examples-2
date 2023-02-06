package ru.yandex.autotests.metrika.tests.ft.management.chartannotaion;

import org.apache.commons.lang3.StringUtils;
import org.joda.time.LocalDate;
import org.joda.time.LocalTime;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.metrika.api.management.client.external.chartannotation.ChartAnnotationUserGroup;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.errors.CommonError.*;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_ALLOWED_SYMBOLS_IN_ANNOTATION_MESSAGE;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_ALLOWED_SYMBOLS_IN_ANNOTATION_TITLE;

/**
 * @author zgmnkv
 */
public class ChartAnnotationTestData {

    public static final User OWNER = USER_DELEGATOR;
    public static final User DELEGATE = USER_DELEGATE_PERMANENT;
    public static final User GRANTEE_WRITE_ACCESS = USER_GRANTEE;
    public static final User GRANTEE_READ_ACCESS = SIMPLE_USER2;
    public static final User FOREIGN_USER = SIMPLE_USER;

    public static MetrikaChartAnnotation getDefaultAnnotation() {
        return new MetrikaChartAnnotation()
                .withTitle("Тестовое примечание")
                .withDate(new LocalDate(2017, 9, 3))
                .withGroup(ChartAnnotationUserGroup.A);
    }

    public static MetrikaChartAnnotation getAlternativeAnnotation() {
        return new MetrikaChartAnnotation()
                .withTitle("Тестовое примечание 2")
                .withDate(new LocalDate(2017, 8, 22))
                .withGroup(ChartAnnotationUserGroup.C)
                .withTime(new LocalTime(21, 53))
                .withMessage("Тестовое описание 2");
    }

    public static MetrikaChartAnnotation getAnnotationWithTime() {
        return getDefaultAnnotation()
                .withTime(new LocalTime(15, 42));
    }

    public static MetrikaChartAnnotation getAnnotationWithMessage() {
        return getDefaultAnnotation()
                .withMessage("Тестовое описание");
    }

    public static MetrikaChartAnnotation getAnnotationWithNoTitle() {
        return getDefaultAnnotation()
                .withTitle(null);
    }

    public static MetrikaChartAnnotation getAnnotationWithEmptyTitle() {
        return getDefaultAnnotation()
                .withTitle("  ");
    }

    public static MetrikaChartAnnotation getAnnotationWithLongTitle() {
        return getDefaultAnnotation()
                .withTitle(StringUtils.repeat("1", 256));
    }

    public static MetrikaChartAnnotation getAnnotationWithNoDate() {
        return getDefaultAnnotation()
                .withDate(null);
    }

    public static MetrikaChartAnnotation getAnnotationWithNoGroup() {
        return getDefaultAnnotation()
                .withGroup(null);
    }

    public static MetrikaChartAnnotation getAnnotationWithLongMessage() {
        return getDefaultAnnotation()
                .withTitle(StringUtils.repeat("1", 1024));
    }

    public static Collection<Object[]> getNegativeAnnotationParams() {
        return of(
                toArray("Пустой объект", (MetrikaChartAnnotation) null, MAY_NOT_BE_NULL),
                toArray("Примечание без заголовка", getAnnotationWithNoTitle(), MAY_NOT_BE_EMPTY),
                toArray("Примечание с пустым заголовком", getAnnotationWithEmptyTitle(), MAY_NOT_BE_EMPTY),
                toArray("Примечание с длинным заголовком", getAnnotationWithLongTitle(), SIZE_MUST_BE_BETWEEN),
                toArray("Примечание без даты", getAnnotationWithNoDate(), MAY_NOT_BE_NULL),
                toArray("Примечание без группы", getAnnotationWithNoGroup(), MAY_NOT_BE_NULL),
                toArray("Примечание с длинным описанием", getAnnotationWithLongMessage(), SIZE_MUST_BE_BETWEEN),
                toArray("Базовое примечание с недопустимыми символами в заголовке", getDefaultAnnotation().withTitle("\uD83D\uDCC5"), NOT_ALLOWED_SYMBOLS_IN_ANNOTATION_TITLE),
                toArray("Базовое примечание с недопустимыми символами в описании", getDefaultAnnotation().withMessage("\uD83D\uDCC5"), NOT_ALLOWED_SYMBOLS_IN_ANNOTATION_MESSAGE)
        );
    }

    public static EditAction<MetrikaChartAnnotation> getChangeTitleAction() {
        return new EditAction<MetrikaChartAnnotation>("изменить заголовок") {
            @Override
            public MetrikaChartAnnotation edit(MetrikaChartAnnotation source) {
                return source.withTitle("Измененное тестовое описание");
            }
        };
    }

    public static EditAction<MetrikaChartAnnotation> getChangeDateAction() {
        return new EditAction<MetrikaChartAnnotation>("изменить дату") {
            @Override
            public MetrikaChartAnnotation edit(MetrikaChartAnnotation source) {
                return source.withDate(new LocalDate(2016, 11, 14));
            }
        };
    }

    public static EditAction<MetrikaChartAnnotation> getChangeGroupAction() {
        return new EditAction<MetrikaChartAnnotation>("изменить группу") {
            @Override
            public MetrikaChartAnnotation edit(MetrikaChartAnnotation source) {
                return source.withGroup(ChartAnnotationUserGroup.D);
            }
        };
    }

    public static EditAction<MetrikaChartAnnotation> getChangeTimeAction() {
        return new EditAction<MetrikaChartAnnotation>("изменить время") {
            @Override
            public MetrikaChartAnnotation edit(MetrikaChartAnnotation source) {
                return source.withTime(new LocalTime(9, 27));
            }
        };
    }

    public static EditAction<MetrikaChartAnnotation> getChangeMessageAction() {
        return new EditAction<MetrikaChartAnnotation>("изменить описание") {
            @Override
            public MetrikaChartAnnotation edit(MetrikaChartAnnotation source) {
                return source.withMessage("Измененное тестовое описание");
            }
        };
    }
}
