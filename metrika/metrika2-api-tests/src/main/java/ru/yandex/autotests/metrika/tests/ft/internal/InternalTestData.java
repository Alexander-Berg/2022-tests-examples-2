package ru.yandex.autotests.metrika.tests.ft.internal;

import com.google.common.collect.ImmutableMap;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerContent;
import ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerLocation;
import ru.yandex.metrika.api.management.client.notification.ExternalNotificationInnerType;
import ru.yandex.metrika.api.management.client.notification.Notification;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import static java.lang.String.format;
import static java.util.Arrays.asList;
import static java.util.Collections.EMPTY_MAP;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.RandomUtils.getString;

/**
 * Created by sourx on 21.07.16.
 */
public class InternalTestData {
    private static final String NOTIFICATION_BASE_TITLE = "Тестовое уведомление ";

    private static final int NOTIFICATION_TITTLE_LIMIT = 256;
    private static final int NOTIFICATION_BODY_LIMIT = 4096;

    private static final int RANDOM_STRING_LENGTH = 10;

    public static String getNotificationTitle() {
        return NOTIFICATION_BASE_TITLE + getString(RANDOM_STRING_LENGTH);
    }

    public static String getNotificationTitle(String baseName) {
        return baseName + getString(RANDOM_STRING_LENGTH);
    }

    public static String getNotificationVisitParam() {
        return "visit_param_" + getString(RANDOM_STRING_LENGTH);
    }

    private static String getNotificationStartDate() {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd 00:00:00");
        return dateFormat.format(new Date());
    }

    private static String getNotificationEndDate() {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd 23:59:59");
        return dateFormat.format(new Date());
    }

    public static Object createNotificationParam(Notification notification) {
        return createNotificationParam(Users.SUPPORT, notification);
    }

    public static Object createNotificationParam(User user, Notification notification) {
        return toArray(user, new NotificationObjectWrapper(notification));
    }

    public static Object createNotificationNegativeParam(Notification notification, IExpectedError error) {
        return createNotificationNegativeParam(Users.SUPPORT, notification, error);
    }

    public static Object createNotificationNegativeParam(User user, Notification notification, IExpectedError error) {
        return toArray(user, new NotificationObjectWrapper(notification), error);
    }

    public static Notification getNotificationWithoutDate() {
        return new Notification()
                .withType(ExternalNotificationInnerType.INFO)
                .withLocation(ExternalNotificationInnerLocation.ROW)
                .withCloseAfterFollow(false)
                .withPending(true)
                .withVisitParam("AnyVisitParam")
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle()
                        ))
                        .withBody(EMPTY_MAP));
    }

    public static Notification getDefaultNotification() {
        return getNotificationWithoutDate()
                .withStartTime(getNotificationStartDate())
                .withEndTime(getNotificationEndDate());
    }

    public static Notification getUpdateNotification() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", "Уведомление с типом update "
                        ))
                        .withBody(EMPTY_MAP))
                .withType(ExternalNotificationInnerType.UPDATE);
    }

    public static Notification getCriticalNotification() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", "Уведомление с типом critical "
                        ))
                        .withBody(EMPTY_MAP))
                .withType(ExternalNotificationInnerType.CRITICAL);
    }

    public static Notification getNotificationWithLocation(ExternalNotificationInnerLocation location) {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", format("Уведомление с location %s ", location.name())
                        ))
                        .withBody(EMPTY_MAP))
                .withLocation(location);
    }

    public static Notification getNotificationWithVisitParam(String visitParam) {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", format("Уведомление с visit_param %s ", visitParam)
                        ))
                        .withBody(EMPTY_MAP))
                .withVisitParam(visitParam);
    }

    public static Notification getNotificationWithCloseAfterFollow(Boolean closeAfterFollow) {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", format("Уведомление с closeAfterFollow %s ", closeAfterFollow)
                        ))
                        .withBody(EMPTY_MAP))
                .withCloseAfterFollow(closeAfterFollow);
    }

    public static Notification getNotificationWithPending(Boolean pending) {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", format("Уведомление с pending %s ", pending)
                        ))
                        .withBody(EMPTY_MAP))
                .withPending(pending);
    }

    public static Notification getNotificationWithMaxTitle() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getString(NOTIFICATION_TITTLE_LIMIT)
                        ))
                        .withBody(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с заголовком максимальной длины ")
                        )));
    }

    public static Notification getNotificationWithMaxBody() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с телом максимальной длины ")
                        ))
                        .withBody(ImmutableMap.of(
                                "ru", getString(NOTIFICATION_BODY_LIMIT)
                        )));
    }

    public static Notification getNotificationWithMoreThanMaxTitle() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getString(NOTIFICATION_TITTLE_LIMIT + 1)
                        ))
                        .withBody(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с заголовком больше максимального")
                        )));
    }

    public static Notification getNotificationWithMoreThanMaxBody() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с телом больше максимального")
                        ))
                        .withBody(ImmutableMap.of(
                                "ru", getString(NOTIFICATION_BODY_LIMIT + 1)
                        )));
    }

    public static Notification getNotificationWithOnlyEnTitle() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "en", getNotificationTitle("Уведомление только с английским заголовком ")
                        ))
                        .withBody(EMPTY_MAP));
    }

    public static Notification getNotificationWithOnlyUaTitle() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ua", getNotificationTitle("Уведомление только с украинским заголовком ")
                        ))
                        .withBody(EMPTY_MAP));
    }

    public static Notification getNotificationWithOnlyTrTitle() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "tr", getNotificationTitle("Уведомление только с турецким заголовком ")
                        ))
                        .withBody(EMPTY_MAP));
    }

    public static Notification getNotificationWithFullContent() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle(),
                                "en", getNotificationTitle(),
                                "ua", getNotificationTitle(),
                                "tr", getNotificationTitle()
                        ))
                        .withBody(ImmutableMap.of(
                                "ru", getString(RANDOM_STRING_LENGTH),
                                "en", getString(RANDOM_STRING_LENGTH),
                                "ua", getString(RANDOM_STRING_LENGTH),
                                "tr", getString(RANDOM_STRING_LENGTH)
                        )));
    }

    public static Notification getNotificationWithIcon() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с иконкой ")
                        ))
                        .withBody(EMPTY_MAP)
                        .withIcon("base64, optional"));
    }

    public static Notification getNotificationWithScope() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с заданным scope ")
                        ))
                        .withBody(EMPTY_MAP))
                .withScope(asList("report:traffic"));
    }

    public static Notification getNotificationWithUIDs(List<Long> uids) {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с заданными uids ")
                        ))
                        .withBody(EMPTY_MAP))
                .withUids(uids);
    }

    public static Notification getNotificationWithObjIds(List<Long> objIds) {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", getNotificationTitle("Уведомление с заданными obj_ids ")
                        ))
                        .withBody(EMPTY_MAP))
                .withObjIds(objIds);
    }

    public static Notification getNotificationWithoutContent() {
        return getDefaultNotification()
                .withContent(new ExternalNotificationInnerContent()
                        .withTitle(EMPTY_MAP)
                        .withBody(EMPTY_MAP));
    }

    public static Notification getNotificationWithEmptyStringInDate() {
        return getDefaultNotification()
                .withStartTime("")
                .withEndTime("");
    }

    public static Object createNotificationEditParam(Notification notification, EditAction<Notification> editAction) {
        return createNotificationEditParam(Users.SUPPORT, notification, editAction);
    }

    public static Object createNotificationEditParam(User user,
                                                     Notification notification,
                                                     EditAction<Notification> editAction) {
        return toArray(user, new NotificationObjectWrapper(notification), editAction);
    }

    public static EditAction<Notification> getChangeContent() {
        final String newTitle = getNotificationTitle();

        return new EditAction<Notification>(format("Сменить заголовок уведомления на %s", newTitle)) {
            @Override
            public Notification edit(Notification source) {
                return source.withContent(new ExternalNotificationInnerContent()
                        .withTitle(ImmutableMap.of(
                                "ru", newTitle,
                                "en", newTitle
                        ))
                        .withBody(EMPTY_MAP));
            }
        };
    }

    public static EditAction<Notification> getChangeType(ExternalNotificationInnerType type) {
        final ExternalNotificationInnerType newType = type;

        return new EditAction<Notification>(format("Сменить тип на %s", newType)) {
            @Override
            public Notification edit(Notification source) {
                return source.withType(newType);
            }
        };
    }

    public static EditAction<Notification> getChangeVisitParam(String visitParam) {
        return new EditAction<Notification>(format("Сменить visit_param на %s", visitParam)) {
            @Override
            public Notification edit(Notification source) {
                return source.withVisitParam(visitParam);
            }
        };
    }

    public static EditAction<Notification> getChangeLocation(ExternalNotificationInnerLocation location) {
        final ExternalNotificationInnerLocation newLocation = location;

        return new EditAction<Notification>(format("Сменить расположение на %s", newLocation)) {
            @Override
            public Notification edit(Notification source) {
                return source.withLocation(newLocation);
            }
        };
    }

    public static EditAction<Notification> getChangeStartDate() {
        final String newStartTime = "2016-01-01 00:00:00";

        return new EditAction<Notification>(format("Сменить время начала на %s", newStartTime)) {
            @Override
            public Notification edit(Notification source) {
                return source.withStartTime(newStartTime);
            }
        };
    }

    public static EditAction<Notification> getChangeEndDate() {
        final String newEndTime = getNotificationStartDate();
        return new EditAction<Notification>(format("Сменить время окончания на %s", newEndTime)) {
            @Override
            public Notification edit(Notification source) {
                return source.withEndTime(newEndTime);
            }
        };
    }

    public static EditAction<Notification> getChangeCloseAfterFollow(Boolean closeAfterFollow) {
        return new EditAction<Notification>(format("Сменить closeAfterFollow на %s", closeAfterFollow)) {
            @Override
            public Notification edit(Notification source) {
                return source.withCloseAfterFollow(closeAfterFollow);
            }
        };
    }

    public static EditAction<Notification> getChangePending(Boolean pending) {
        return new EditAction<Notification>(format("Сменить pending на %s", pending)) {
            @Override
            public Notification edit(Notification source) {
                return source.withPending(pending);
            }
        };
    }

    public static EditAction<Notification> getChangeScope() {
        final List<String> newScope = asList("report:sources");

        return new EditAction<Notification>(format("Сменить scope на %s", newScope)) {
            @Override
            public Notification edit(Notification source) {
                return source.withScope(newScope);
            }
        };
    }

    public static EditAction<Notification> getChangeUIDs(List<Long> uids) {
        return new EditAction<Notification>(format("Сменить UIDs на %s ", uids)) {
            @Override
            public Notification edit(Notification source) {
                return source.withUids(uids);
            }
        };
    }

    public static EditAction<Notification> getChangeObjIds(List<Long> objIds) {
        return new EditAction<Notification>(format("Сменить obj_ids на %s ", objIds)) {
            @Override
            public Notification edit(Notification source) {
                return source.withObjIds(objIds);
            }
        };
    }

    public static EditAction<Notification> getChangeContentWithMaxTitle() {
        return new EditAction<Notification>("Сменить заголовок на заголовок максимальной длины") {
            @Override
            public Notification edit(Notification source) {
                return source.withContent(
                        new ExternalNotificationInnerContent()
                                .withTitle(ImmutableMap.of(
                                        "ru", getString(NOTIFICATION_TITTLE_LIMIT)
                                ))
                                .withBody(EMPTY_MAP));
            }
        };
    }

    public static EditAction<Notification> getChangeContentWithMaxBody() {
        return new EditAction<Notification>("Сменить тело уведомления на максимальное") {
            @Override
            public Notification edit(Notification source) {
                return source.withContent(
                        new ExternalNotificationInnerContent()
                                .withTitle(ImmutableMap.of(
                                        "ru", getNotificationTitle()
                                ))
                                .withBody(ImmutableMap.of(
                                        "ru", getString(NOTIFICATION_BODY_LIMIT)
                                ))
                );
            }
        };
    }

    public static Object createNotificationNegativeEditParam(Notification notification,
                                                             EditAction<Notification> editAction,
                                                             IExpectedError error) {
        return createNotificationNegativeEditParam(Users.SUPPORT, notification, editAction, error);
    }

    public static Object createNotificationNegativeEditParam(User user,
                                                             Notification notification,
                                                             EditAction<Notification> editAction,
                                                             IExpectedError error) {
        return toArray(user, new NotificationObjectWrapper(notification), editAction, error);
    }

    public static EditAction<Notification> getChangeEmptyTitle() {
        return new EditAction<Notification>("Сменить заголовки уведомления на пустые") {
            @Override
            public Notification edit(Notification source) {
                return source.withContent(
                        new ExternalNotificationInnerContent()
                                .withTitle(EMPTY_MAP)
                                .withBody(EMPTY_MAP)
                );
            }
        };
    }

    public static EditAction<Notification> getChangeContentWithMoreThanMaxTitle() {
        return new EditAction<Notification>("Сменить заголовок на заголовок больше максимальной длины") {
            @Override
            public Notification edit(Notification source) {
                return source.withContent(
                        new ExternalNotificationInnerContent()
                                .withTitle(ImmutableMap.of(
                                        "ru", getString(NOTIFICATION_TITTLE_LIMIT + 1)
                                ))
                                .withBody(EMPTY_MAP));
            }
        };
    }

    public static EditAction<Notification> getChangeContentWithMoreThanMaxBody() {
        return new EditAction<Notification>("Сменить тело уведомления на тело больше максимального") {
            @Override
            public Notification edit(Notification source) {
                return source.withContent(
                        new ExternalNotificationInnerContent()
                                .withTitle(ImmutableMap.of(
                                        "ru", getNotificationTitle()
                                ))
                                .withBody(ImmutableMap.of(
                                        "ru", getString(NOTIFICATION_BODY_LIMIT + 1)
                                ))
                );
            }
        };
    }

    public static EditAction<Notification> getChangeDateToEmptyString() {
        return new EditAction<Notification>("Сменить дату на пустую строку") {
            @Override
            public Notification edit(Notification source) {
                return source
                        .withStartTime("")
                        .withEndTime("");
            }
        };
    }

    public static EditAction<Notification> getChangeDateToNull() {
        return new EditAction<Notification>("Сменить дату на null") {
            @Override
            public Notification edit(Notification source) {
                return source
                        .withStartTime(null)
                        .withEndTime(null);
            }
        };
    }
}
