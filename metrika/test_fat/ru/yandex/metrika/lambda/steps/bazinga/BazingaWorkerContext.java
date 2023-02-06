package ru.yandex.metrika.lambda.steps.bazinga;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.commune.bazinga.impl.storage.BazingaStorage;
import ru.yandex.commune.bazinga.impl.storage.memory.InMemoryBazingaStorage;
import ru.yandex.commune.zk2.ZkConfiguration;
import ru.yandex.commune.zk2.ZkPath;
import ru.yandex.commune.zk2.client.ZkManagerContextConfiguration;
import ru.yandex.metrika.util.app.ZooSettingsImpl;

@Configuration
@Import(ZkManagerContextConfiguration.class)
public class BazingaWorkerContext {

    @Autowired
    private ZooSettingsImpl zooSettings;

    @Bean
    public WorkerTaskManagerSelfServiceImpl bazingaTaskManager() {
        return new WorkerTaskManagerSelfServiceImpl();
    }

    @Bean
    public BazingaStorage bazingaStorage() {
        return new InMemoryBazingaStorage();
    }

    @Bean
    public ZkPath zkRoot() {
        return new ZkPath("/bazinga-lambda-test");
    }

    @Bean
    public ZkConfiguration zkConfiguration() {
        return new ZkConfiguration(zooSettings.getZookeeperConnectString());
    }
}
