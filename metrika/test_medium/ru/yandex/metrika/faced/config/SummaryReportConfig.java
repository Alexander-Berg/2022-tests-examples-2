package ru.yandex.metrika.faced.config;

import java.util.List;

import javax.servlet.Filter;
import javax.servlet.http.HttpServletRequest;

import org.apache.commons.lang3.RandomStringUtils;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.security.web.FilterChainProxy;
import org.springframework.security.web.SecurityFilterChain;

import ru.yandex.metrika.api.error.MetrikaExceptionHandler;
import ru.yandex.metrika.api.management.client.SummaryReportTelegramLinkController;
import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSubscriptionCountersProvider;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportTelegramLinkService;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportTelegramSubscription;
import ru.yandex.metrika.api.management.client.external.summaryreport.TelegramUserLink;
import ru.yandex.metrika.api.management.config.CountersRbacConfig;
import ru.yandex.metrika.api.management.config.CountersServiceConfig;
import ru.yandex.metrika.api.management.config.JdbcTemplateConfig;
import ru.yandex.metrika.api.management.config.WebMockMvcConfig;
import ru.yandex.metrika.rbac.metrika.CountersRbac;
import ru.yandex.metrika.util.dao.GenericJdbcDao;
import ru.yandex.metrika.util.dao.JdbcMetadataGenerator;
import ru.yandex.metrika.util.dao.PostgresDialectSettings;

@Configuration
@Import(value = {
        JdbcTemplateConfig.class,
        WebMockMvcConfig.class,
        CountersRbacConfig.class,
        CountersServiceConfig.class
})
@EnableAsync
public class SummaryReportConfig {

    public static final String botToken = RandomStringUtils.random(20, true, true);

    @Bean(name = "summaryReportSubscriptionDao")
    public GenericJdbcDao<SummaryReportTelegramSubscription> summaryReportSubscriptionDao(
            @Qualifier("pgSubscriptionsTemplate") JdbcTemplate pgSubscriptionsTemplate
    ) {
        var bean = new GenericJdbcDao<>(SummaryReportTelegramSubscription.class, new JdbcMetadataGenerator(), new NamedParameterJdbcTemplate(pgSubscriptionsTemplate));

        bean.setDialectSettings(new PostgresDialectSettings());

        return bean;
    }

    @Bean(name = "telegramUserLinkDao")
    public GenericJdbcDao<TelegramUserLink> telegramUserLinkDao(
            @Qualifier("pgSubscriptionsTemplate") JdbcTemplate pgSubscriptionsTemplate
    ) {
        var bean = new GenericJdbcDao<>(TelegramUserLink.class, new JdbcMetadataGenerator(), new NamedParameterJdbcTemplate(pgSubscriptionsTemplate));

        bean.setDialectSettings(new PostgresDialectSettings());

        return bean;
    }

    @Bean
    public SummaryReportSubscriptionCountersProvider summaryReportCountersProvider(
            @Qualifier("countersDao") CountersDao countersDao,
            @Qualifier("countersRbac") CountersRbac countersRbac,
            @Qualifier("pgSubscriptionsTemplate") JdbcTemplate pgSubscriptionsTemplate
    ) {
        return new SummaryReportSubscriptionCountersProvider(pgSubscriptionsTemplate, countersDao, countersRbac);
    }

    @Bean
    public SummaryReportTelegramLinkService summaryReportTelegramLinkService(
            @Qualifier("pgSubscriptionsTemplate") JdbcTemplate pgSubscriptionsTemplate,
            @Qualifier("summaryReportSubscriptionDao") GenericJdbcDao<SummaryReportTelegramSubscription> subscriptionDao,
            @Qualifier("telegramUserLinkDao") GenericJdbcDao<TelegramUserLink> telegramUserLinkDao,
            @Qualifier("summaryReportCountersProvider") SummaryReportSubscriptionCountersProvider countersProvider
    ) {
        var bean = new SummaryReportTelegramLinkService(subscriptionDao, telegramUserLinkDao, pgSubscriptionsTemplate, countersProvider);
        bean.setBotToken(botToken);
        return bean;
    }

    @Bean
    public SummaryReportTelegramLinkController summaryReportTelegramLinkController() {
        return new SummaryReportTelegramLinkController();
    }

    @Bean(name = "exceptionHandler")
    public MetrikaExceptionHandler metrikaExceptionHandler() {
        return new MetrikaExceptionHandler();
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
