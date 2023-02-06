package ru.yandex.autotests.morda.monitorings.clusters;

import org.apache.log4j.Logger;
import org.glassfish.jersey.client.ClientConfig;
import org.glassfish.jersey.client.ClientProperties;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.mordabackend.utils.CleanvarsUtils;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.terra.junit.rules.BottleMessageRule;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import java.net.HttpURLConnection;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.util.Arrays;
import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;

@Aqua.Test(title = "Проверка кластеров Морды")
@Feature("Кластеры")
@RunWith(Parameterized.class)
public class ClustersTest {
    private static final Logger LOGGER = Logger.getLogger(ClustersTest.class);
    private static final String HOSTS_URL = "http://c.yandex-team.ru/api/groups2hosts/portal_wfront";

    @Rule
    public BottleMessageRule bottleMessageRule = new BottleMessageRule();
    private String url;
    private Client client;

    public ClustersTest(String host) throws KeyManagementException, NoSuchAlgorithmException {
        this.url = "https://" + host;

        TrustManager[] trustAllCerts = new TrustManager[]{new X509TrustManager() {
            public void checkClientTrusted(X509Certificate[] arg0, String arg1)
                    throws CertificateException {
            }

            public void checkServerTrusted(X509Certificate[] arg0, String arg1)
                    throws CertificateException {
            }

            public X509Certificate[] getAcceptedIssuers() {
                return new X509Certificate[0];
            }

        }};
        final SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, trustAllCerts, new java.security.SecureRandom());

        final HostnameVerifier allHostsValid = new HostnameVerifier() {
            public boolean verify(String hostname, SSLSession session) {
                return true;
            }
        };
        ClientBuilder clientBuilder = ClientBuilder.newBuilder();
        ClientConfig config = new ClientConfig();
        client = clientBuilder.sslContext(sslContext)
                .hostnameVerifier(allHostsValid)
                .withConfig(config)
                .property(ClientProperties.CONNECT_TIMEOUT, 5000)
                .property(ClientProperties.READ_TIMEOUT, 5000)
                .build();
    }

    @Parameterized.Parameters(name = "Cluster {0}")
    public static Collection<Object[]> data() {
        Client client = ClientBuilder
                .newClient()
                .property(ClientProperties.CONNECT_TIMEOUT, 5000)
                .property(ClientProperties.READ_TIMEOUT, 5000);

        String text = client.target(HOSTS_URL).request().buildGet().invoke().readEntity(String.class);

        return ParametrizationConverter.convert(Arrays.asList(text.split("\n")));
    }

    @Test
    public void clusterResponse() throws Exception {
        CleanvarsUtils.shouldHaveResponseCode(client, url, equalTo(HttpURLConnection.HTTP_OK));
        CleanvarsUtils.shouldHaveResponseCode(client, url + "/?edit=1", equalTo(HttpURLConnection.HTTP_OK));
    }

}
