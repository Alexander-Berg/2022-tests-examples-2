package ru.yandex.metrika.api.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.auth.MetrikaRoleUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.rbac.metrika.MetrikaObjTypeResolver;
import ru.yandex.metrika.rbac.metrika.MetrikaPermissionResolver;

@Configuration
@Import(JdbcTemplateConfig.class)
public class CountersRbacConfig {

    @Bean
    public CountersRbac countersRbac(
            MySqlJdbcTemplate rbacTemplate,
            MySqlJdbcTemplate countersTemplate
    ) {
        CountersRbac countersRbac = new CountersRbac();
        countersRbac.setRbacDb(rbacTemplate);
        countersRbac.setConvMain(countersTemplate);
        countersRbac.setPermissionResolver(new MetrikaPermissionResolver());
        countersRbac.setObjTypeResolver(new MetrikaObjTypeResolver());
        countersRbac.setRoleUtils(new MetrikaRoleUtils());
        /*countersRbac.setGrantsLog(metrikaGrantsLog);
        countersRbac.setRbac(metrikaRbac);>*/
        return countersRbac;
    }
}
