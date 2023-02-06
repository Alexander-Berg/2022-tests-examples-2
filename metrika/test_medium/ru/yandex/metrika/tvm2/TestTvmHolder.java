package ru.yandex.metrika.tvm2;

import org.apache.commons.lang3.StringUtils;

import ru.yandex.passport.tvmauth.CheckedUserTicket;
import ru.yandex.passport.tvmauth.TicketStatus;
import ru.yandex.passport.tvmauth.Unittest;

/**
 * Альтернативы созданию данного класса
 * 1) Использовать в тестах предопределённый набор uid-ов чтобы можно было
 * сгенерировать тикеты с помощью tvmknife заранее
 * 2) Поставить тестам зависимость на passport/infra/tools/tvmknife/bin и генерировать тикеты прямо в тестах
 * <p>
 * Данный способ предполагает, что мы кодируем всю нужную информацию в строчке "токена" где-то в тестах,
 * а потом не вызываем настоящий код проверки tvm тикета, а просто отдаём объект болванку.
 * Преимуществами такого подхода является
 * 1) не нужно тянуть неочевидные зависимости
 * 2) не нужно ограничивать логику тестов определённым набором uid-ов
 * 3) логика похожа на {@link ru.yandex.metrika.auth.BlackboxRequestExecutorStub}
 */
public class TestTvmHolder extends TvmHolder {

    private static final String FAKE_USER_TICKET_PREFIX = "fake_user_ticket:";

    public static String makeFakeUserTicket(long uid) {
        return FAKE_USER_TICKET_PREFIX + uid;
    }

    @Override
    public CheckedUserTicket checkUserTicket(String tvmToken) {
        if (tvmSettings.isEnabled()) {
            return parseTicketFromFakeUserTicket(tvmToken);
        } else {
            throw new IllegalStateException("checkUserTicket: tvm is disabled");
        }
    }

    private CheckedUserTicket parseTicketFromFakeUserTicket(String token) {
        if (!token.startsWith(FAKE_USER_TICKET_PREFIX)) {
            throw new IllegalArgumentException("In medium tests we use special format to stub " +
                    "user ticket checking logic. Like 'fake_user_ticket:12312312'. Actual input: " + token);
        }
        String suffix = StringUtils.substringAfter(token, FAKE_USER_TICKET_PREFIX);
        long uid;
        try {
            uid = Long.parseLong(suffix);
        } catch (Exception ex) {
            throw new IllegalArgumentException("Test user token stub's suffix is not a number: " + suffix);
        }
        return Unittest.createUserTicket(TicketStatus.OK, uid,
                new String[]{"appmetrica:read", "appmetrica:write"}, new long[]{uid});
    }
}
