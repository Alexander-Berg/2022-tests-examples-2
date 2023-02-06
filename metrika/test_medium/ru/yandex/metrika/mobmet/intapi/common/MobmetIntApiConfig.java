package ru.yandex.metrika.mobmet.intapi.common;

import java.util.Collections;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ImportResource;

import ru.yandex.metrika.clusters.clickhouse.MtMobGigaCluster;
import ru.yandex.metrika.config.ArcadiaSourceAwareBeanDefinitionReader;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.mobmet.dao.ActiveAppsDao;
import ru.yandex.metrika.mobmet.dao.AppLabelDao;
import ru.yandex.metrika.mobmet.dao.MonotoneSequenceDao;
import ru.yandex.metrika.mobmet.dao.TrackingPartnersDao;
import ru.yandex.metrika.mobmet.dao.cluster.MobmetApiPickingClusters;
import ru.yandex.metrika.mobmet.dao.redirect.CampaignsDao;
import ru.yandex.metrika.mobmet.dao.redirect.CommonProcessor;
import ru.yandex.metrika.mobmet.dao.redirect.DeepLinkDao;
import ru.yandex.metrika.mobmet.dao.redirect.MultiplatformDao;
import ru.yandex.metrika.mobmet.dao.redirect.OmniPostbackDao;
import ru.yandex.metrika.mobmet.dao.redirect.PostbackDao;
import ru.yandex.metrika.mobmet.dao.redirect.PostbackTemplateDao;
import ru.yandex.metrika.mobmet.dao.redirect.RedirectServiceDao;
import ru.yandex.metrika.mobmet.dao.redirect.TargetUrlDao;
import ru.yandex.metrika.mobmet.dao.redirect.TrackerLogger;
import ru.yandex.metrika.mobmet.dao.redirect.TrackerPreprocessor;
import ru.yandex.metrika.mobmet.dao.redirect.TrackingDao;
import ru.yandex.metrika.mobmet.dao.redirect.TrackingErrorsMessageGenerator;
import ru.yandex.metrika.mobmet.dao.redirect.TrackingMacrosDao;
import ru.yandex.metrika.mobmet.management.AppLabelService;
import ru.yandex.metrika.mobmet.management.ApplicationsLoadService;
import ru.yandex.metrika.mobmet.management.conversion.MobmetConversionDao;
import ru.yandex.metrika.mobmet.management.conversion.MobmetConversionService;
import ru.yandex.metrika.mobmet.scheduler.tasks.bundleid.dao.BundleIdCachingDao;
import ru.yandex.metrika.mobmet.scheduler.tasks.clientevents.EventNamesCacheDao;
import ru.yandex.metrika.mobmet.service.TrackingPartnerService;
import ru.yandex.metrika.mobmet.service.TrackingService;
import ru.yandex.metrika.mobmet.service.TrackingUrlsService;
import ru.yandex.metrika.mobmet.service.grants.MobmetGrantsService;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;
import ru.yandex.metrika.spring.TranslationHelper;


@SuppressWarnings({"SpringImportResource", "ParameterNumber"})
@Configuration
@ImportResource(
        locations = {
                // чтобы контроллеры загрузились прописываем *-servlet.xml явно, не полагаясь на web.xml
                "arcadia_source_file:webapp/WEB-INF/mobmet-intapi-servlet.xml",
                "arcadia_source_file:webapp/WEB-INF/mobmet-intapi.xml",
                "arcadia_source_file:webapp/WEB-INF/mobmet-intapi-security.xml",
                "arcadia_source_file:webapp/WEB-INF/mobmet-intapi-jdbc.xml",
                "classpath:ru/yandex/metrika/util/common-jmx-support.xml",
                "classpath:ru/yandex/metrika/util/common-metrics-support.xml",
                "classpath:ru/yandex/metrika/util/common-monitoring-support.xml",
                "classpath:ru/yandex/metrika/util/common-jdbc.xml",
                "classpath:ru/yandex/metrika/util/common-console.xml",
                "classpath:ru/yandex/metrika/ch-router-factory.xml",
                "classpath:ru/yandex/metrika/mtmobgiga-router-config.xml",
                "classpath:ru/yandex/metrika/util/common-tx.xml",
                "classpath:ru/yandex/metrika/util/juggler-reporter.xml",
                "classpath:ru/yandex/metrika/rbac/metrika/mobmet-rbac.xml",
                "classpath:ru/yandex/metrika/frontend-common-cache-redis.xml",
                "classpath:ru/yandex/metrika/mobmet/mobmet-common-management.xml",
                "classpath:ru/yandex/metrika/util/common-jdbc-pg-mobile-crashes.xml",
                "classpath:ru/yandex/metrika/mobmet/mobmet-common-crash.xml",
                "classpath:ru/yandex/metrika/dbclients/clickhouse/clickhouse-log.xml",
                // с common-security.xml, но у меня не получилось переопределить authUtils
                "classpath:ru/yandex/metrika/common-security-test.xml",
        },
        reader = ArcadiaSourceAwareBeanDefinitionReader.class
)
public class MobmetIntApiConfig {

    @Bean
    public EventNamesCacheDao eventNamesCacheDao(MySqlJdbcTemplate mobileMiscTemplate,
                                                 MtMobGigaCluster mtMobGiga) {
        return new EventNamesCacheDao(mobileMiscTemplate, mtMobGiga);
    }

    @Bean
    public BundleIdCachingDao bundleIdCachingDao(MySqlJdbcTemplate mobileMiscTemplate,
                                                 MtMobGigaCluster mtMobGiga) {
        return new BundleIdCachingDao(mobileMiscTemplate, mtMobGiga);
    }

    @Bean
    public TrackingPartnerService trackingPartnerService(MySqlJdbcTemplate mobileTemplate,
                                                         ApplicationsLoadService applicationsLoadService,
                                                         PartnerTypes partnerTypes,
                                                         TranslationHelper translationHelper) {
        return new TrackingPartnerService(
                new PostbackTemplateDao(mobileTemplate),
                new TrackingPartnersDao(mobileTemplate),
                new TrackingMacrosDao(mobileTemplate),
                applicationsLoadService,
                partnerTypes,
                translationHelper);
    }

    @Bean
    public PartnerTypes partnerTypes(MySqlJdbcTemplate mobileTemplate) {
        PartnerTypes partnerTypes = new PartnerTypes();
        partnerTypes.setMobile(mobileTemplate);
        return partnerTypes;
    }

    @Bean
    public AppLabelService appLabelService(MySqlJdbcTemplate mobileTemplate,
                                           ApplicationsLoadService applicationsLoadService) {
        return new AppLabelService(applicationsLoadService, new AppLabelDao(mobileTemplate));
    }

    @Bean
    public DeepLinkDao deepLinkDao(MySqlJdbcTemplate mobileTemplate) {
        DeepLinkDao deepLinkDao = new DeepLinkDao();
        deepLinkDao.setJdbc(mobileTemplate);
        return deepLinkDao;
    }

    @Bean
    TargetUrlDao targetUrlDao(MySqlJdbcTemplate mobileTemplate) {
        TargetUrlDao targetUrlDao = new TargetUrlDao();
        targetUrlDao.setJdbc(mobileTemplate);
        return targetUrlDao;
    }

    @Bean
    public TrackingUrlsService trackingUrlsService(DeepLinkDao deepLinkDao, TargetUrlDao targetUrlDao) {
        return new TrackingUrlsService(deepLinkDao, targetUrlDao, Collections.emptyMap());
    }

    @Bean
    public RedirectServiceDao redirectServiceDao(MySqlJdbcTemplate mobileTemplate,
                                                 PartnerTypes partnerTypes,
                                                 DeepLinkDao deepLinkDao,
                                                 TargetUrlDao targetUrlDao,
                                                 TranslationHelper translationHelper) {
        CampaignsDao campaignsDao = new CampaignsDao(mobileTemplate);
        TrackerPreprocessor trackerPreprocessor = new TrackerPreprocessor(
                campaignsDao,
                deepLinkDao,
                targetUrlDao,
                partnerTypes,
                new TrackingErrorsMessageGenerator(translationHelper),
                Collections.emptyMap());
        CommonProcessor commonProcessor = new CommonProcessor(partnerTypes, Collections.emptyMap());
        PostbackDao postbackDao = new PostbackDao(mobileTemplate);
        return new RedirectServiceDao(
                new MonotoneSequenceDao(mobileTemplate),
                postbackDao,
                new OmniPostbackDao(mobileTemplate),
                campaignsDao,
                new MultiplatformDao(mobileTemplate),
                partnerTypes,
                trackerPreprocessor,
                commonProcessor,
                translationHelper,
                new MobmetConversionService(new MobmetConversionDao(mobileTemplate), postbackDao));
    }

    @Bean
    public MobmetApiPickingClusters mobmetApiPickingClusters(MtMobGigaCluster mtMobGiga) {
        return new MobmetApiPickingClusters(mtMobGiga.mtmobgiga());
    }

    @Bean
    public TrackingService trackingService(MySqlJdbcTemplate mobileTemplate,
                                           MySqlJdbcTemplate mobileMiscTemplate,
                                           MtMobGigaCluster mtMobGiga,
                                           ApplicationsLoadService applicationsLoadService,
                                           TrackingPartnerService trackingPartnerService,
                                           RedirectServiceDao redirectServiceDao,
                                           MobmetGrantsService grantsService,
                                           PartnerTypes partnerTypes) {
        MobmetApiPickingClusters mobmetApiPickingClusters = new MobmetApiPickingClusters(mtMobGiga.mtmobgiga());
        return new TrackingService(
                redirectServiceDao,
                applicationsLoadService,
                new ActiveAppsDao(mobileMiscTemplate, mobmetApiPickingClusters),
                new TrackingDao(mobileTemplate, mobileMiscTemplate, mtMobGiga),
                new TrackingPartnersDao(mobileTemplate),
                trackingPartnerService,
                partnerTypes,
                grantsService,
                new TrackerLogger(mobileMiscTemplate));
    }
}
