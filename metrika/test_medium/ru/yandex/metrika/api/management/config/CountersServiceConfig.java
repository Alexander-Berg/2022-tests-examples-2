package ru.yandex.metrika.api.management.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.ImportResource;

import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.client.DelegatesService;
import ru.yandex.metrika.api.management.client.FiltersService;
import ru.yandex.metrika.api.management.client.GoalsService;
import ru.yandex.metrika.api.management.client.GrantsService;
import ru.yandex.metrika.api.management.client.OfflineOptionsService;
import ru.yandex.metrika.api.management.client.OperationsService;
import ru.yandex.metrika.api.management.client.WebvisorService;
import ru.yandex.metrika.api.management.client.check.CodeCheckService;
import ru.yandex.metrika.api.management.client.counter.CodeOptionsService;
import ru.yandex.metrika.api.management.client.counter.CounterChecker;
import ru.yandex.metrika.api.management.client.counter.CounterCreator;
import ru.yandex.metrika.api.management.client.counter.CounterFlagsService;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.client.counter.CounterUpdater;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.counter.CountersService;
import ru.yandex.metrika.api.management.client.geopoint.GeoPointService;
import ru.yandex.metrika.api.management.client.geopoint.SpravAltayService;
import ru.yandex.metrika.api.management.client.label.LabelsService;
import ru.yandex.metrika.api.management.client.pvl.PvlDictsService;
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLinkService;
import ru.yandex.metrika.api.management.spring.AdditionalBeansConfig;
import ru.yandex.metrika.api.management.tests.medium.client.GoalsServiceTest;
import ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags.CounterFlagsServiceTest;
import ru.yandex.metrika.auth.AuthUtils;
import ru.yandex.metrika.auth.MetrikaRoleUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.TimeZones;
import ru.yandex.metrika.rbac.metrika.CounterLabelsRbac;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.util.ApiInputValidator;

@Configuration
@Import({CountersDaoConfig.class, CurrencyServiceConfig.class,
        GoalsServiceTest.Config.class, OfflineOptionsServiceConfig.class,
        CounterOptionsServiceConfig.class, CodeOptionsServiceConfig.class,
        CounterStatDaoYDBConfig.class, CounterFlagsServiceTest.Config.class,
        WebMetrikaPickingClustersConfig.class, FeatureServiceConfig.class,
        AdditionalBeansConfig.class, JdbcTemplateConfig.class})
@ImportResource(locations = {"classpath:/ru/yandex/metrika/api/management/spring/test-counter-creator-config.xml",
        "classpath:/ru/yandex/metrika/common-security-test.xml",
        "classpath:/ru/yandex/metrika/util/common-jdbc.xml",
        "classpath:/ru/yandex/metrika/rbac/metrika/metrika-rbac.xml",
        "classpath:/ru/yandex/metrika/frontend-common-ch.xml",
        "classpath:/ru/yandex/metrika/mtgiga-router-config.xml",
        "classpath:/ru/yandex/metrika/mtnano-router-config.xml",
        "classpath:/ru/yandex/metrika/mtaggr-router-config.xml",
        "classpath:/ru/yandex/metrika/ch-router-factory.xml"})
public class CountersServiceConfig {

    @Bean
    public static BeanFactoryPostProcessor aliasRegistrationBFPP() {
        return beanFactory -> {
            beanFactory.registerAlias("metrikaRbac", "mainRbac");
            beanFactory.registerAlias("counterOptionsService", "counterLimitsService");
            beanFactory.registerAlias("counterOptionsService", "publisherOptionsService");
            beanFactory.registerAlias("counterOptionsService", "autogoalsService");
            beanFactory.registerAlias("counterOptionsService","webvisorOptionsService");
        };
    }

    @Bean
    CountersService countersService(CountersDao countersDao, CountersRbac countersRbac,
                                    CounterUpdater counterUpdater, CounterCreator counterCreator,
                                    CurrencyService currencyService, AuthUtils authUtils,
                                    CodeCheckService codeCheckService, FiltersService filtersService,
                                    GoalsService goalsService, GrantsService grantsService,
                                    GeoPointService geoPointService, PvlDictsService pvlDictsService,
                                    TimeZones timeZones, LabelsService labelsService,
                                    CounterLabelsRbac counterLabelsRbac, MetrikaRoleUtils metrikaRoleUtils,
                                    WebmasterLinkService webmasterLinkService, OfflineOptionsService offlineOptionsService,
                                    WebvisorService webvisorService, CounterOptionsService counterOptionsService,
                                    FeatureService featureService, CodeOptionsService codeOptionsService,
                                    CounterFlagsService counterFlagsService,
                                    DelegatesService delegatesService) {
        var result = new CountersService();
        result.setCountersDao(countersDao);
        result.setFeatureService(featureService);
        result.setRoleUtils(metrikaRoleUtils);
        result.setAuthUtils(authUtils);
        result.setCountersRbac(countersRbac);
        result.setLabelsRbac(counterLabelsRbac);
        result.setCodeChecker(codeCheckService);
        result.setCounterCreator(counterCreator);
        result.setCounterUpdater(counterUpdater);
        result.setFiltersService(filtersService);
        result.setGoalsService(goalsService);
        result.setGrantsService(grantsService);
        //Непроброшенные бины из xml конфига. Оставлю, на случай, если надо будет понять, чего не хватает:
        //        <property name="operationsService" ref="operationsService"/>
        result.setTimeZones(timeZones);
        result.setWebvisorService(webvisorService);
        result.setLabelsService(labelsService);
        //        <property name="listener" ref="beanContextStartupListener"/>
        result.setCounterLimitsService(counterOptionsService);
        //        <property name="linksService" ref="linksService"/>
        result.setDelegatesService(delegatesService);
        result.setWebmasterLinkService(webmasterLinkService);
        result.setOfflineOptionsService(offlineOptionsService);
        result.setGeoPointService(geoPointService);
        result.setPvlDictsService(pvlDictsService);
        result.setCurrencyService(currencyService);
        //        <property name="httpClientsWrapperWithTvm" ref="httpClientsWrapperWithTvm"/>
        result.setAutogoalsService(counterOptionsService);
        result.setCodeOptionsService(codeOptionsService);
        //        <property name="settings" ref="settings"/>
        result.setCounterFlagsService(counterFlagsService);
        return result;
    }

    @Bean
    public CounterUpdater counterUpdater(@Qualifier("convMainTemplate") MySqlJdbcTemplate convMain, WebvisorService webvisorService,
                                         CodeCheckService codeCheckService, CounterChecker counterChecker,
                                         FiltersService filtersService, GoalsService goalsService,
                                         GrantsService grantsService, OperationsService operationsService,
                                         TimeZones timeZones, ApiInputValidator apiInputValidator,
                                         WebmasterLinkService webmasterLinkService, OfflineOptionsService offlineOptionsService,
                                         SpravAltayService spravAltayService, CodeOptionsService codeOptionsService,
                                         CounterOptionsService counterOptionsService) {
        var counterUpdater = new CounterUpdater();
        counterUpdater.setJdbcTemplate(convMain);
        counterUpdater.setWebvisorService(webvisorService);
        counterUpdater.setCodeChecker(codeCheckService);
        counterUpdater.setCounterChecker(counterChecker);
        counterUpdater.setFiltersService(filtersService);
        counterUpdater.setGoalsService(goalsService);
        counterUpdater.setGrantsService(grantsService);
        counterUpdater.setOperationsService(operationsService);
        counterUpdater.setTimeZones(timeZones);
        counterUpdater.setValidator(apiInputValidator);
        counterUpdater.setWebmasterLinkService(webmasterLinkService);
        counterUpdater.setOfflineOptionsService(offlineOptionsService);
        counterUpdater.setSpravAltayService(spravAltayService);
        counterUpdater.setPublisherOptionsService(codeOptionsService);
        counterUpdater.setAutogoalsService(counterOptionsService);
        counterUpdater.setAlternativeCdnService(counterOptionsService);
        counterUpdater.setCodeOptionsService(codeOptionsService);
        counterUpdater.setCounterOptionsService(counterOptionsService);
        return counterUpdater;
    }
}
