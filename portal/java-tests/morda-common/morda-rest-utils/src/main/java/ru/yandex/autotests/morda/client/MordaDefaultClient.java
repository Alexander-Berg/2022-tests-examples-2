package ru.yandex.autotests.morda.client;

import com.fasterxml.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import com.fasterxml.jackson.jaxrs.xml.JacksonJaxbXMLProvider;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientConfig;
import org.glassfish.jersey.client.ClientProperties;
import org.glassfish.jersey.client.JerseyClientBuilder;
import org.glassfish.jersey.filter.LoggingFilter;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import javax.ws.rs.client.Client;
import java.security.cert.X509Certificate;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/04/15
 */
public class MordaDefaultClient {

    public static ClientConfig getDefaultClientConfig() {
        ClientConfig clientConfig = new ClientConfig();

        clientConfig.connectorProvider(new ApacheConnectorProvider());
        clientConfig.register(LoggingFilter.class);
        clientConfig.register(JacksonJaxbXMLProvider.class);
        clientConfig.register(JacksonJaxbJsonProvider.class);

        return clientConfig;
    }

    public static Client getDefaultClient() {
        TrustManager[] trustAllCerts = new TrustManager[]{new X509TrustManager(){
            public X509Certificate[] getAcceptedIssuers() {
                return null;
            }
            public void checkClientTrusted(X509Certificate[] certs, String authType){}
            public void checkServerTrusted(X509Certificate[] certs, String authType){}
        }};

        try {

            SSLContext sc = SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());

            Client client = new JerseyClientBuilder().withConfig(getDefaultClientConfig()).build();

            client.property(ClientProperties.CONNECT_TIMEOUT, 10000);
            client.property(ClientProperties.READ_TIMEOUT,    10000);

            return client;
        } catch (Throwable e) {
            throw new RuntimeException(e);
        }
    }
}
