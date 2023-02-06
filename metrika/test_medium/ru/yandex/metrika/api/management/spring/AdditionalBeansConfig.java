package ru.yandex.metrika.api.management.spring;

import java.util.Map;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.mail.PassportSmsService2;
import ru.yandex.metrika.mail.SmsUtils;
import ru.yandex.metrika.managers.GeoPointDao;
import ru.yandex.metrika.tvm2.TvmHolder;
import ru.yandex.metrika.tvm2.TvmServices;
import ru.yandex.metrika.util.PropertyUtilsMysql;

@Configuration
public class AdditionalBeansConfig {

    @Bean
    public Map<String, String> metrikaOauthScopes() {
        return Map.of();
    }

    @Bean
    PassportSmsService2 smsService(TvmHolder tvmHolder, TvmServices tvmServices) {
        var smsService = new PassportSmsService2();
        smsService.setSmsPassportUrlHost("sms.passport.yandex.ru");
        smsService.setTvmHolder(tvmHolder);
        smsService.setTvmServices(tvmServices);
        return smsService;
    }

    @Bean
    SmsUtils smsUtils(PassportSmsService2 smsService, AuthUtils authUtils) {
        var smsUtils = new SmsUtils();
        smsUtils.setAuthUtils(authUtils);
        smsUtils.setSmsService(smsService);
        return smsUtils;
    }

    @Bean(name = {"propertyUtilsMysql", "propertyUtils"})
    PropertyUtilsMysql propertyUtilsMysql(MySqlJdbcTemplate convMainTemplate) {
        var propertyUtilsMysql = new PropertyUtilsMysql();
        propertyUtilsMysql.setPropertiesDb(convMainTemplate);
        return propertyUtilsMysql;
    }

    @Bean(name = {"geoPointsDao", "geoPointDao"})
    GeoPointDao geoPointDao(MySqlJdbcTemplate convMainTemplate) {
        var geoPointDao = new GeoPointDao();
        geoPointDao.setConvMain(convMainTemplate);
        return geoPointDao;
    }
}
