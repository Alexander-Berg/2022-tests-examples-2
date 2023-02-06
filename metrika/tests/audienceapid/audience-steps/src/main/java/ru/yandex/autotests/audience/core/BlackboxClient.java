package ru.yandex.autotests.audience.core;

import org.apache.http.HttpRequestInterceptor;
import org.apache.http.client.HttpClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import ru.yandex.bolts.collection.Option;
import ru.yandex.inside.passport.blackbox2.BlackboxRawRequestExecutor;
import ru.yandex.inside.passport.blackbox2.BlackboxRequestExecutorWithRetries;
import ru.yandex.inside.passport.blackbox2.protocol.BlackboxException;
import ru.yandex.inside.passport.blackbox2.protocol.response.BlackboxCorrectResponse;
import ru.yandex.misc.io.http.Timeout;
import ru.yandex.misc.io.http.apache.v4.ApacheHttpClientUtils;
import ru.yandex.misc.ip.IpAddress;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

@Resource.Classpath("blackbox.properties")
public class BlackboxClient {
    private static final Logger log = LoggerFactory.getLogger(BlackboxClient.class);

    public static final int BLACKBOX_SERVICE_ID = 222;
    public static final int BLACKBOX_MIMINO_SERVICE_ID = 239;

    private final BlackboxRequestExecutorWithRetries requestExecutor;

    @Property("api.url")
    private String apiUrl;

    private static BlackboxClient instance;

    public static BlackboxClient getInstance() {
        if (instance == null) {
            instance = new BlackboxClient();
        }
        return instance;
    }

    public BlackboxClient() {
        PropertyLoader.populate(this);
        final BlackboxRawRequestExecutor rawExecutor =
                new BlackboxRawRequestExecutor(apiUrl, buildBlackboxHttpClient(100));
        requestExecutor = new BlackboxRequestExecutorWithRetries(rawExecutor, 5);
    }

    private HttpClient buildBlackboxHttpClient(int timeout) {
        ApacheHttpClientUtils.Builder builder = ApacheHttpClientUtils.Builder.create()
                .multiThreaded()
                .withHttpsSupport(ApacheHttpClientUtils.HttpsSupport.ENABLED)
                .withMaxConnections(100)
                .withTimeout(Timeout.milliseconds(timeout));

        TvmClient tvm = TvmClient.getInstance();
        final HttpRequestInterceptor interceptor = tvm.serviceTicketInterceptorChecked(() -> BLACKBOX_MIMINO_SERVICE_ID);
        builder = builder.withInterceptorFirst(interceptor);

        return builder.build();
    }

    public static List<InetAddress> getLocalAddresses() {
        Enumeration<NetworkInterface> networkInterfaces = Collections.enumeration(Collections.emptyList());
        try {
            networkInterfaces = NetworkInterface.getNetworkInterfaces();
        } catch (SocketException e) {
            log.warn("no network interfaces? ", e);
        }
        List<InetAddress> locals = new ArrayList<>();
        while (networkInterfaces.hasMoreElements()) {
            NetworkInterface networkInterface = networkInterfaces.nextElement();
            Enumeration<InetAddress> inetAddresses = networkInterface.getInetAddresses();
            while(inetAddresses.hasMoreElements()) {
                InetAddress inetAddress = inetAddresses.nextElement();
                locals.add(inetAddress);
            }
        }
        return locals;
    }

    public BlackboxCorrectResponse oAuth(String token) {

        List<InetAddress> localAddresses = getLocalAddresses();
        InetAddress inetAddress = localAddresses.get(0);

        try {
            return requestExecutor.asQueryable().oAuth(
                    IpAddress.valueOf(inetAddress),
                    token,
                    null, // DB_FIELDS,
                    null, // attributes
                    Option.empty(), // EMAILS_PARAMETER_VALUES,
                    Option.empty(), // aliases oO
                    true
                    );
        } catch (BlackboxException e) {
            throw new RuntimeException("fail at "+ inetAddress+" // " +getLocalAddresses(), e);
        }
    }

    public void setApiUrl(String apiUrl) {
        this.apiUrl = apiUrl;
    }
}
