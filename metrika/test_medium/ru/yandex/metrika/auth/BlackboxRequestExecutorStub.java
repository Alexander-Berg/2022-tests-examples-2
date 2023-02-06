package ru.yandex.metrika.auth;

import java.util.List;
import java.util.stream.Collectors;

import ru.yandex.bolts.collection.Either;
import ru.yandex.bolts.collection.Option;
import ru.yandex.bolts.collection.Tuple2;
import ru.yandex.bolts.collection.impl.ArrayListF;
import ru.yandex.bolts.collection.impl.EmptyMap;
import ru.yandex.inside.passport.PassportDomain;
import ru.yandex.inside.passport.PassportUid;
import ru.yandex.inside.passport.blackbox2.BlackboxRequestExecutor;
import ru.yandex.inside.passport.blackbox2.protocol.request.BlackboxMethodParameter;
import ru.yandex.inside.passport.blackbox2.protocol.request.BlackboxRequest;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxAbstractResponse;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxBulkResponse;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxCorrectResponse;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxOAuthInfo;
import ru.yandex.inside.passport.blackbox2.protocol.response.Karma;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.misc.email.Email;

/**
 * Можно было бы инжектить в этот бин пользователей или какую-то логику, но пока это не нужно
 */
public class BlackboxRequestExecutorStub extends BlackboxRequestExecutor {

    @Override
    public Either<BlackboxAbstractResponse, BlackboxBulkResponse> execute(BlackboxRequest request) {
        return Either.left(blackboxResponse(request));
    }

    private static BlackboxCorrectResponse blackboxResponse(BlackboxRequest request) {
        return switch (request.getMethod()) {
            case USER_INFO -> handleUserInfo(request);
            case OAUTH -> handleOauth(request);
            default -> throw new IllegalArgumentException("Unsupported method: " + request.getMethod());
        };
    }

    private static BlackboxCorrectResponse handleUserInfo(BlackboxRequest request) {
        long responseUid;
        String responseLogin;

        List<Long> uids = F.map(getParams(request, BlackboxMethodParameter.UID), Long::valueOf);
        List<String> logins = getParams(request, BlackboxMethodParameter.LOGIN);
        if (!uids.isEmpty()) {
            responseUid = F.getOnlyElement(uids);
            responseLogin = "login_of_" + responseUid;
        } else if (!logins.isEmpty()) {
            responseLogin = F.getOnlyElement(logins);
            responseUid = Math.abs(responseLogin.hashCode());
        } else {
            throw new IllegalArgumentException("Unsupported params: " + request.asUrlEncodedString());
        }

        return getResponse(responseUid, responseLogin, request);
    }

    private static BlackboxCorrectResponse handleOauth(BlackboxRequest request) {
        return getResponse(1L, "aa", request);
    }

    private static BlackboxCorrectResponse getResponse(long responseUid, String responseLogin, BlackboxRequest request) {
        String responseEmail = responseLogin + "@yandex.ru";
        List<String> responseOauthScopes = List.of("appmetrica:read", "appmetrica:write");

        return new BlackboxCorrectResponse(
                request.getMethod(),
                Option.empty(),
                Option.empty(),
                200,
                Option.of(20),
                Option.of(Tuple2.tuple(new PassportUid(responseUid), PassportDomain.YANDEX_RU)),
                Option.of(responseLogin),
                new EmptyMap<>(),
                new ArrayListF<>(),
                new ArrayListF<>(),
                Option.of(new Email(responseEmail)),
                new EmptyMap<>(),
                Option.of(new Karma(42, 42)),
                Option.empty(),
                Option.empty(),
                Option.of(new BlackboxOAuthInfo("clientId", "clientName", new ArrayListF<>(responseOauthScopes))),
                Option.of("regionName"),
                Option.empty()
        );
    }

    private static List<String> getParams(BlackboxRequest request, BlackboxMethodParameter parameter) {
        return request.getRequestParameters()
                .stream()
                .filter(t -> parameter.toRequestParameterName().equals(t.get1()))
                .map(Tuple2::get2)
                .collect(Collectors.toList());
    }
}
