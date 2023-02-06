package ru.yandex.metrika.cdp.api.users;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxCorrectResponse;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.rbac.metrika.MetrikaRole;
import ru.yandex.metrika.util.collections.F;

import static ru.yandex.metrika.api.management.users.MockSecurityUtils.blackboxResponse;
import static ru.yandex.metrika.api.management.users.MockSecurityUtils.metrikaUserDetails;

public class TestUsers {

    public static final String SIMPLE_USER_NAME = "test user";
    public static final String READ_ONLY_USER_NAME = "read only user";
    public static final String YA_MANAGER_NAME = "ya manager";

    private static final List<MetrikaUserDetails> muds = new ArrayList<>();
    private static final String METRIKA_OAUTH_SCOPE_READ = "metrika:read";
    private static final String METRIKA_OAUTH_SCOPE_WRITE = "metrika:write";

    private static void addUser(BlackboxCorrectResponse blackboxResponse, MetrikaRole... roles) {
        muds.add(metrikaUserDetails(blackboxResponse, roles));
    }

    static {
        addUser(
                blackboxResponse(42, SIMPLE_USER_NAME, METRIKA_OAUTH_SCOPE_READ, METRIKA_OAUTH_SCOPE_WRITE),
                MetrikaRole.api_read, MetrikaRole.api_write, MetrikaRole.user
        );
        addUser(
                blackboxResponse(43, YA_MANAGER_NAME, METRIKA_OAUTH_SCOPE_READ, METRIKA_OAUTH_SCOPE_WRITE),
                MetrikaRole.api_read, MetrikaRole.api_write, MetrikaRole.user, MetrikaRole.yamanager
        );
        addUser(
                blackboxResponse(44, READ_ONLY_USER_NAME, METRIKA_OAUTH_SCOPE_READ),
                MetrikaRole.api_read, MetrikaRole.user
        );
    }


    public static final Map<String, MetrikaUserDetails> usersByUsername = F.asMap(muds, MetrikaUserDetails::getUsername);
    public static final Map<Long, MetrikaUserDetails> usersByUid = F.asMap(muds, MetrikaUserDetails::getUid);
}
