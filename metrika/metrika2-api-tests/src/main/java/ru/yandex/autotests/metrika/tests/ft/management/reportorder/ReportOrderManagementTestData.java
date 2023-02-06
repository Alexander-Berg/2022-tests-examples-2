package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import org.apache.commons.lang3.StringUtils;
import org.joda.time.LocalDate;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderFrequency;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderType;
import ru.yandex.metrika.segments.core.query.paramertization.GroupType;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.errors.CommonError.*;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;

/**
 * @author zgmnkv
 */
public class ReportOrderManagementTestData {

    public static final User REPORT_ORDER_USER = Users.SIMPLE_USER;

    public static ReportOrder getDefaultReportOrder() {
        return getSingleReportOrder();
    }

    public static ReportOrder getSingleReportOrder() {
        return new ReportOrder()
                .withType(ReportOrderType.SINGLE)
                .withName("Тестовый одноразовый отчет")
                .withDate1(new LocalDate(2017, 9, 4))
                .withDate2(new LocalDate(2017, 9, 17))
                .withMetrics("ym:s:visits");
    }

    public static ReportOrder getRegularReportOrder() {
        return new ReportOrder()
                .withType(ReportOrderType.REGULAR)
                .withName("Тестовый регулярный отчет")
                .withFrequency(ReportOrderFrequency.DAILY)
                .withMetrics("ym:s:visits");
    }

    public static ReportOrder getDailyReportOrder() {
        return getRegularReportOrder()
                .withFrequency(ReportOrderFrequency.DAILY);
    }

    public static ReportOrder getWeeklyReportOrder() {
        return getRegularReportOrder()
                .withFrequency(ReportOrderFrequency.WEEKLY);
    }

    public static ReportOrder getMonthlyReportOrder() {
        return getRegularReportOrder()
                .withFrequency(ReportOrderFrequency.MONTHLY);
    }

    public static ReportOrder getReportOrderWithSingleRecipientEmail() {
        return getDefaultReportOrder()
                .withRecipientEmails(ImmutableList.of("user@example.com"));
    }

    public static ReportOrder getReportOrderWithMultipleRecipientEmails() {
        return getDefaultReportOrder()
                .withRecipientEmails(ImmutableList.of("user1@example.com", "user2@example.org"));
    }

    public static ReportOrder getReportOrderWithAllReportParams() {
        return getDefaultReportOrder()
                .withPreset("sources_summary")
                .withMetrics("ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds")
                .withDimensions("ym:s:<attribution>TrafficSource,ym:s:<attribution>SourceEngine")
                .withFilters("ym:s:regionCountry IN('225')")
                .withSort("-ym:s:visits")
                .withDynamicMetric("ym:s:avgVisitDurationSeconds")
                .withIncludeUndefined(true)
                .withWithConfidence(true)
                .withExcludeInsignificant(true)
                .withConfidenceLevel(0.98d)
                .withMaxDeviation(0.03d)
                .withGroup(GroupType.DAY)
                .withOtherParams(ImmutableMap.of("attribution", "Last"));
    }

    public static ReportOrder getReportOrderWithNoName() {
        return getDefaultReportOrder()
                .withName(null);
    }

    public static ReportOrder getReportOrderWithEmptyName() {
        return getDefaultReportOrder()
                .withName("   ");
    }

    public static ReportOrder getReportOrderWithLongName() {
        return getDefaultReportOrder()
                .withName(StringUtils.repeat("1", 256));
    }

    public static ReportOrder getReportOrderWithIncorrectRecipientEmail() {
        return getDefaultReportOrder()
                .withRecipientEmails(of("@incorrect_email@"));
    }

    public static ReportOrder getSingleReportOrderWithoutDate1() {
        return getSingleReportOrder()
                .withDate1(null);
    }

    public static ReportOrder getSingleReportOrderWithoutDate2() {
        return getSingleReportOrder()
                .withDate2(null);
    }

    public static ReportOrder getRegularReportOrderWithoutFrequency() {
        return getRegularReportOrder()
                .withFrequency(null);
    }

    public static ReportOrder getReportOrderWithoutMetrics() {
        return getDefaultReportOrder()
                .withMetrics(null);
    }

    public static Collection<Object[]> getCommonReportOrderNegativeParams() {
        return of(
                toArray("Пустой объект", (ReportOrder) null, MAY_NOT_BE_NULL),
                toArray("Отчет без названия", getReportOrderWithNoName(), MAY_NOT_BE_EMPTY),
                toArray("Отчет с пустым нзванием", getReportOrderWithEmptyName(), MAY_NOT_BE_EMPTY),
                toArray("Отчет с длинным названием", getReportOrderWithLongName(), SIZE_MUST_BE_BETWEEN),
                toArray("Отчет с некорректным email получателя", getReportOrderWithIncorrectRecipientEmail(), INCORRECT_EMAIL),
                toArray("Регулярный отчет без частоты", getRegularReportOrderWithoutFrequency(), MAY_NOT_BE_NULL)
        );
    }

    public static Collection<Object[]> getCreateReportOrderNegativeParams() {
        return Lists.newArrayList(Iterables.concat(
                getCommonReportOrderNegativeParams(),
                of(
                        toArray("Одноразовый отчет без даты начала", getSingleReportOrderWithoutDate1(), MAY_NOT_BE_NULL),
                        toArray("Одноразовый отчет без даты окончания", getSingleReportOrderWithoutDate2(), MAY_NOT_BE_NULL),
                        toArray("Отчет без метрик", getReportOrderWithoutMetrics(), expect(400L, "Wrong parameter: 'metrics', value: ''"))
                )
        ));
    }

    public static Collection<Object[]> getEditReportOrderNegativeParams() {
        return getCommonReportOrderNegativeParams();
    }

    public static EditAction<ReportOrder> getChangeNameAction() {
        return new EditAction<ReportOrder>("изменить название") {
            @Override
            public ReportOrder edit(ReportOrder source) {
                return source.withName("Измененное название");
            }
        };
    }

    public static EditAction<ReportOrder> getChangeSingleRecipientEmailAction() {
        return new EditAction<ReportOrder>("изменить один email получателя") {
            @Override
            public ReportOrder edit(ReportOrder source) {
                return source.withRecipientEmails(ImmutableList.of("changed@example.com"));
            }
        };
    }

    public static EditAction<ReportOrder> getChangeMultipleRecipientEmailsAction() {
        return new EditAction<ReportOrder>("изменить несколько email получателей") {
            @Override
            public ReportOrder edit(ReportOrder source) {
                return source.withRecipientEmails(ImmutableList.of(
                        "changed1@example.com", "changed2@example.com", "changed3@example.com"
                ));
            }
        };
    }

    public static EditAction<ReportOrder> getChangeSingleReportOrderDatesAction() {
        return new EditAction<ReportOrder>("изменить даты одноразового отчета") {
            @Override
            public ReportOrder edit(ReportOrder source) {
                return source
                        .withDate1(new LocalDate(2015, 11, 12))
                        .withDate2(new LocalDate(2016, 5, 12));
            }
        };
    }

    public static EditAction<ReportOrder> getChangeRegularReportOrderFrequencyToMonthlyAction() {
        return new EditAction<ReportOrder>("изменить частоту регулярного отчета на ежемесячную") {
            @Override
            public ReportOrder edit(ReportOrder source) {
                return source.withFrequency(ReportOrderFrequency.MONTHLY);
            }
        };
    }
}
