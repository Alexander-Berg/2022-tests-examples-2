package ru.yandex.metrika.internalapid.api.config;

import java.util.List;

import javax.servlet.Filter;
import javax.servlet.http.HttpServletRequest;
import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.security.web.FilterChainProxy;
import org.springframework.security.web.SecurityFilterChain;

import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.constructor.contr.FeatureServiceStub;
import ru.yandex.metrika.api.deleted.DeletedCountersService;
import ru.yandex.metrika.api.management.client.EmptyPrefixProvider;
import ru.yandex.metrika.api.management.client.GoalIdGenerationService;
import ru.yandex.metrika.api.management.client.GoalsService;
import ru.yandex.metrika.api.management.client.PrefixNameByTvmProvider;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.counter.CountersDeletionsLog;
import ru.yandex.metrika.api.management.client.counter.CountersService;
import ru.yandex.metrika.api.management.client.label.CounterLinksService;
import ru.yandex.metrika.api.management.config.ApiValidatorConfig;
import ru.yandex.metrika.api.management.config.CounterOptionsDaoConfig;
import ru.yandex.metrika.api.management.config.CounterOptionsServiceConfig;
import ru.yandex.metrika.api.management.config.CurrencyServiceConfig;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.api.management.config.LocaleDictionariesConfig;
import ru.yandex.metrika.api.management.config.MessengerValidatorConfig;
import ru.yandex.metrika.api.management.config.SocialNetworkValidatorConfig;
import ru.yandex.metrika.api.management.config.TimeZonesConfig;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.mysql.DataSourceFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.TransactionalMetrikaDataSource;
import ru.yandex.metrika.internalapid.common.IntapiCountersService;
import ru.yandex.metrika.internalapid.common.IntapiGoalsService;
import ru.yandex.metrika.internalapid.common.validators.SubscribedCounterGoalValidator;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.managers.TimeZones;
import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

@Configuration
@Import({JdbcTemplateConfig.class, ApiValidatorConfig.class,
        LocaleDictionariesConfig.class, MessengerValidatorConfig.class, SocialNetworkValidatorConfig.class,
        CounterOptionsServiceConfig.class, CurrencyServiceConfig.class, CounterOptionsDaoConfig.class,
        TimeZonesConfig.class, TakeoutServiceConfig.class
})
public class InternalapiConfiguration {

    @Autowired
    @Qualifier("convMainTemplate")
    private MySqlJdbcTemplate convMain;

    @Autowired
    @Qualifier("dictsTemplate")
    private MySqlJdbcTemplate dicts;

    @Autowired
    private ApiInputValidator validator;

    @Autowired
    private LocaleDictionaries dictionaries;

    @Autowired
    private CounterOptionsService counterOptionsService;

    @Autowired
    private TimeZones timeZones;

    @Autowired
    private CurrencyService currencyService;

    @Bean
    public DataSource dictsDataSource() {
        TransactionalMetrikaDataSource dataSource = new DataSourceFactory().getDataSource();

        dataSource.setHost(EnvironmentHelper.mysqlHost);
        dataSource.setPort(EnvironmentHelper.mysqlPort);
        dataSource.setUser(EnvironmentHelper.mysqlUser);
        dataSource.setPassword(EnvironmentHelper.mysqlPassword);
        dataSource.setDb("dicts");

        return dataSource;
    }

    @Bean
    MySqlJdbcTemplate dictsTemplate() {
        return new MySqlJdbcTemplate(dictsDataSource());
    }

    @Bean
    public DataSource rbacDataSource() {
        TransactionalMetrikaDataSource dataSource = new DataSourceFactory().getDataSource();

        dataSource.setHost(EnvironmentHelper.mysqlHost);
        dataSource.setPort(EnvironmentHelper.mysqlPort);
        dataSource.setUser(EnvironmentHelper.mysqlUser);
        dataSource.setPassword(EnvironmentHelper.mysqlPassword);
        dataSource.setDb("rbac");

        return dataSource;
    }

    @Bean
    MySqlJdbcTemplate rbacTemplate() {
        return new MySqlJdbcTemplate(rbacDataSource());
    }

    @Bean
    public FeatureService featureService() {
        return new FeatureServiceStub();
    }

    @Bean
    SubscribedCounterGoalValidator subscribedCounterGoalValidator() {
        return new SubscribedCounterGoalValidator(convMain, dicts);
    }

    @Bean
    GoalsService goalsService() {
        GoalsService goalsService = new GoalsService();
        goalsService.setJdbcTemplate(convMain);
        goalsService.setValidator(validator);
        goalsService.setCounterLimitsService(counterOptionsService);
        goalsService.setFormGoalsService(counterOptionsService);
        goalsService.setButtonGoalsService(counterOptionsService);
        goalsService.setDictionaries(dictionaries);
        goalsService.setGoalIdGenerationService(goalIdGenerationService());
        return goalsService;
    }

    @Bean
    GoalIdGenerationService goalIdGenerationService() {
        GoalIdGenerationService service = new GoalIdGenerationService();
        service.setConvMain(convMain);
        return service;
    }

    @Bean
    public PrefixNameByTvmProvider prefixNameByTvmProvider() {
        return new EmptyPrefixProvider();
    }

    @Bean
    public IntapiGoalsService intapiGoalsService() {
        return new IntapiGoalsService(convMain, goalsService(), featureService(), subscribedCounterGoalValidator(), prefixNameByTvmProvider());
    }

    @Bean
    public DeletedCountersService deletedCountersService() {
        DeletedCountersService deletedCountersService = new DeletedCountersService();
        deletedCountersService.setCountersDao(countersDao());
        return deletedCountersService;
    }

    @Bean
    public CountersDao countersDao() {
        return new CountersDao(convMain, timeZones, currencyService);
    }

    @Bean
    public IntapiCountersService intapiCountersService() {
        var deletionsLog = new CountersDeletionsLog(convMain);
        var countersService = new CountersService();
        countersService.setCountersDeleteLog(deletionsLog);
        var countersLinkService = new CounterLinksService();
        countersLinkService.setConvMain(convMain);
        countersService.setCountersDao(countersDao());
        countersService.setLinksService(countersLinkService);
        return new IntapiCountersService(null, countersDao(), convMain, null, null, null, countersService, deletionsLog);
    }

    @Bean
    public FilterChainProxy getFilterChainProxy() {
        SecurityFilterChain securityFilterChain = new SecurityFilterChain() {
            @Override
            public boolean matches(HttpServletRequest request) {
                return false;
            }

            @Override
            public List<Filter> getFilters() {
                return null;
            }
        };
        return new FilterChainProxy(securityFilterChain);
    }
}
