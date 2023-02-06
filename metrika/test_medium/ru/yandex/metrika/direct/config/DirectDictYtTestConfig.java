package ru.yandex.metrika.direct.config;

import java.util.concurrent.TimeUnit;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.common.test.medium.YtClient;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.ytrpc.YtDao;
import ru.yandex.metrika.dbclients.ytrpc.YtPath;
import ru.yandex.metrika.dbclients.ytrpc.YtReplicatedTableReadClient;
import ru.yandex.metrika.dbclients.ytrpc.YtTransactionalClient;
import ru.yandex.metrika.direct.dict.banners.YtBannersDao;
import ru.yandex.metrika.direct.dict.banners.YtBannersIdMapDao;
import ru.yandex.metrika.direct.dict.banners.YtBannersPersistenceService;
import ru.yandex.metrika.direct.dict.bgroups.YtBannerGroupsDao;
import ru.yandex.metrika.direct.dict.order.phrases.YtPhrasesDao;

@Configuration
@Import({YtClient.class})
public class DirectDictYtTestConfig {

    private final String bannerGroupTableName = "banner_group";
    private final String bannerTableName = "banner";
    private final String bannerIdMapTableName = "banner_id_map";
    private final String orderPhraseTableName = "phrase";

    @Autowired
    private YtClient setupYtClient;

    @Bean
    public YtTransactionalClient dictYtClient() {
        var client = new YtTransactionalClient();
        client.setClusterName(EnvironmentHelper.ytProxy);
        return client;
    }

    @Bean
    public YtPath dictYtRootPath() {
        return new YtPath("//tmp");
    }

    @Bean
    public YtPath directDictYtRootPath(YtPath dictYtRootPath) {
        var path = dictYtRootPath.append("direct");
        YtPath bgPath = path.append(bannerGroupTableName);
        YtPath bannerPath = path.append(bannerTableName);
        YtPath bannerIdMapPath = path.append(bannerIdMapTableName);
        YtPath phrasePath = path.append(orderPhraseTableName);
        if (!setupYtClient.existsPath(bgPath.getPath())) {
            setupYtClient.createDynamicTable(bgPath.getPath(), YtBannerGroupsDao.TABLE_SCHEMA);
        }
        if (!setupYtClient.existsPath(bannerPath.getPath())) {
            setupYtClient.createDynamicTable(bannerPath.getPath(), YtBannersDao.TABLE_SCHEMA);
        }
        if (!setupYtClient.existsPath(bannerIdMapPath.getPath())) {
            setupYtClient.createDynamicTable(bannerIdMapPath.getPath(), YtBannersIdMapDao.TABLE_SCHEMA);
        }
        if (!setupYtClient.existsPath(phrasePath.getPath())) {
            setupYtClient.createDynamicTable(phrasePath.getPath(), YtPhrasesDao.TABLE_SCHEMA);
        }
        return path;
    }

    @Bean
    public YtReplicatedTableReadClient bannerGroupReplicatedReadClient(YtPath directDictYtRootPath) {
        return defaultReplicatedClientParams()
                .withRootPath(directDictYtRootPath)
                .withTableName(bannerGroupTableName)
                .build();
    }

    @Bean
    public YtDao bannerGroupMainDao(YtTransactionalClient ytTransactionalClient) {
        return new YtDao(ytTransactionalClient);
    }

    @Bean
    public YtBannerGroupsDao ytBannerGroupsDao(
            YtDao bannerGroupMainDao,
            YtPath directDictYtRootPath,
            YtReplicatedTableReadClient bannerGroupReplicatedReadClient) {
        return new YtBannerGroupsDao(
                bannerGroupMainDao, bannerGroupReplicatedReadClient, directDictYtRootPath, bannerGroupTableName
        );
    }

    private YtReplicatedTableReadClient.Builder defaultReplicatedClientParams() {
        return new YtReplicatedTableReadClient.Builder()
                .withClusterName(EnvironmentHelper.ytProxy)
                .withResolveInterval(TimeUnit.MINUTES.toMillis(1))
                .withMaximumLag(TimeUnit.MINUTES.toMillis(1))
                .withInactiveTtl(TimeUnit.MINUTES.toMillis(1));
    }

    @Bean
    public YtReplicatedTableReadClient bannerReplicatedReadClient(YtPath directDictYtRootPath) {
        return defaultReplicatedClientParams()
                .withRootPath(directDictYtRootPath)
                .withTableName(bannerTableName)
                .build();
    }

    @Bean
    public YtBannersDao ytBannersDao(
            YtDao directDictsMainDao,
            YtPath directDictYtRootPath,
            YtReplicatedTableReadClient bannerReplicatedReadClient) {
        return new YtBannersDao(directDictsMainDao, bannerReplicatedReadClient, directDictYtRootPath, bannerTableName);
    }

    @Bean
    public YtReplicatedTableReadClient bannerIdMapReplicatedReadClient(YtPath directDictYtRootPath) {
        return defaultReplicatedClientParams()
                .withRootPath(directDictYtRootPath)
                .withTableName(bannerIdMapTableName)
                .build();
    }

    @Bean
    public YtBannersIdMapDao ytBannersIdMapDao(
            YtDao directDictsMainDao,
            YtPath directDictYtRootPath,
            YtReplicatedTableReadClient bannerIdMapReplicatedReadClient) {
        return new YtBannersIdMapDao(
                directDictsMainDao, bannerIdMapReplicatedReadClient, directDictYtRootPath, bannerIdMapTableName
        );
    }

    @Bean
    public YtBannersPersistenceService ytBannersPersistenceService(
            YtBannersDao bannersDao,
            YtBannersIdMapDao bannersIdMapDao
    ) {
        return new YtBannersPersistenceService(bannersDao, bannersIdMapDao);
    }

    @Bean
    public YtReplicatedTableReadClient phraseReplicatedReadClient(YtPath directDictYtRootPath) {
        return defaultReplicatedClientParams()
                .withRootPath(directDictYtRootPath)
                .withTableName(orderPhraseTableName)
                .build();
    }

    @Bean
    public YtPhrasesDao ytPhrasesDao(
            YtDao directDictsMainDao,
            YtReplicatedTableReadClient phraseReplicatedReadClient,
            YtPath directDictYtRootPath
    ) {
        return new YtPhrasesDao(
                directDictsMainDao, phraseReplicatedReadClient,
                directDictYtRootPath, orderPhraseTableName
        );
    }
}
