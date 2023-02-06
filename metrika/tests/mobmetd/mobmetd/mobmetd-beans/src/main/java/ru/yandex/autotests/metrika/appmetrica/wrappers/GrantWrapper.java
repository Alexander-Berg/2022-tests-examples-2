package ru.yandex.autotests.metrika.appmetrica.wrappers;

import com.google.common.base.Joiner;
import com.google.common.collect.ImmutableMap;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;

import java.util.Map;

/**
 * Created by graev on 13/12/2016.
 */
public final class GrantWrapper {
    private MobmetGrantE grant;

    public static GrantWrapper wrap(MobmetGrantE grant) {
        return new GrantWrapper(grant);
    }

    public GrantWrapper(MobmetGrantE grant) {
        this.grant = grant;
    }

    public MobmetGrantE getGrant() {
        return grant;
    }

    public boolean isNotEmpty() {
        return grant != null;
    }

    @Override
    public String toString() {
        if (grant == null) {
            return "Отсутствие доступа";
        }

        return String.format("%s для пользователя %s с партнерами [%s] и событиями [%s]",
                grantTypeDescription(),
                grant.getUserLogin(),
                Joiner.on(", ").join(grant.getPartners()),
                Joiner.on(", ").join(grant.getEventLabels()));
    }

    private String grantTypeDescription() {
        final Map<GrantType, String> descriptionByPerm = ImmutableMap.<GrantType, String>builder()
                .put(GrantType.VIEW, "Доступ на чтение")
                .put(GrantType.EDIT, "Доступ на запись")
                .put(GrantType.AGENCY_VIEW, "Агентский доступ на чтение")
                .put(GrantType.AGENCY_EDIT, "Агентский доступ на запись")
                .build();
        return descriptionByPerm.get(grant.getPerm());
    }
}
