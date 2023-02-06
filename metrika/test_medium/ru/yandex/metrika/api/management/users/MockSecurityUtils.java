package ru.yandex.metrika.api.management.users;

import java.util.Arrays;
import java.util.stream.Stream;

import ru.yandex.bolts.collection.Option;
import ru.yandex.bolts.collection.Tuple2;
import ru.yandex.bolts.collection.impl.ArrayListF;
import ru.yandex.bolts.collection.impl.EmptyMap;
import ru.yandex.inside.passport.PassportDomain;
import ru.yandex.inside.passport.PassportUid;
import ru.yandex.inside.passport.blackbox2.protocol.BlackboxMethod;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxCorrectResponse;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxOAuthInfo;
import ru.yandex.inside.passport.blackbox2.protocol.response.Karma;
import ru.yandex.metrika.auth.AuthenticationType;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.rbac.metrika.MetrikaRole;
import ru.yandex.misc.email.Email;

import static java.util.stream.Collectors.toSet;

public class MockSecurityUtils {

    public static BlackboxCorrectResponse blackboxResponse(long uid, String login, String... oauthScopes) {
        return new BlackboxCorrectResponse(
                BlackboxMethod.LOGIN,
                Option.empty(),
                Option.empty(),
                200,
                Option.of(20),
                Option.of(Tuple2.tuple(new PassportUid(uid), PassportDomain.YANDEX_RU)),
                Option.of(login),
                new EmptyMap<>(),
                new ArrayListF<>(),
                new ArrayListF<>(),
                Option.of(new Email("aa@bb.ru")),
                new EmptyMap<>(),
                Option.of(new Karma(42, 42)),
                Option.empty(),
                Option.empty(),
                Option.of(new BlackboxOAuthInfo("1", "name", new ArrayListF<>(Arrays.asList(oauthScopes)))),
                Option.of("aaaa"),
                Option.empty()
        );
    }

    public static MetrikaUserDetails metrikaUserDetails(BlackboxCorrectResponse blackboxResponse, MetrikaRole... roles) {
        var userDetails = new MetrikaUserDetails(blackboxResponse, "localhost", AuthenticationType.oauth_token);
        userDetails.setRoleNames(Stream.of(roles).map(MetrikaRole::getName).collect(toSet()), 0);
        return userDetails;
    }
}
