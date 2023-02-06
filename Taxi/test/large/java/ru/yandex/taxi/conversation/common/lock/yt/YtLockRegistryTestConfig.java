package ru.yandex.taxi.conversation.common.lock.yt;

import java.time.Duration;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ru.yandex.yt.ytclient.bus.DefaultBusConnector;
import ru.yandex.yt.ytclient.proxy.YtClient;
import ru.yandex.yt.ytclient.proxy.YtCluster;
import ru.yandex.yt.ytclient.rpc.RpcCompression;
import ru.yandex.yt.ytclient.rpc.RpcCredentials;
import ru.yandex.yt.ytclient.rpc.RpcOptions;
import ru.yandex.yt.ytclient.rpc.internal.Compression;

@Configuration
public class YtLockRegistryTestConfig {

    @Value("${yt.lock.path}")
    private String lockPath;

    @Value("${yt.timeout.failover}")
    private Long failoverTimeout;

    @Value("${yt.timeout.global}")
    private Long globalTimeout;

    @Value("${yt.client.proxy}")
    private String proxy;

    @Value("${yt.user}")
    private String user;

    @Value("${YT_TOKEN}")
    private String token;

    @Bean
    public YtLockRegistryFactory lockRegistryFactory() {
        return new YtLockRegistryFactory();
    }

    public class YtLockRegistryFactory {

        public YtLockRegistry create() {
            return new YtLockRegistry(ytClient(), lockPath);
        }

        private YtClient ytClient() {
            RpcOptions rpcOptions = new RpcOptions()
                    .setFailoverTimeout(Duration.ofMillis(failoverTimeout))
                    .setGlobalTimeout(Duration.ofMillis(globalTimeout));

            YtClient ytClient = new YtClient(new DefaultBusConnector(), List.of(new YtCluster(proxy)),
                    "",
                    null,
                    new RpcCredentials(user, token),
                    new RpcCompression(Compression.Lz4),
                    rpcOptions);

            try {
                ytClient.waitProxies().get(1, TimeUnit.MINUTES);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                e.printStackTrace();
            }

            return ytClient;
        }
    }
}
