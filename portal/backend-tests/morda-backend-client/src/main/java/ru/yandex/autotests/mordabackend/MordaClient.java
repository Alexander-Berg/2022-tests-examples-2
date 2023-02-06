package ru.yandex.autotests.mordabackend;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.introspect.Annotated;
import com.fasterxml.jackson.databind.introspect.JacksonAnnotationIntrospector;
import com.fasterxml.jackson.databind.type.TypeFactory;
import com.fasterxml.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationIntrospector;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.DnsResolver;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLContexts;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.glassfish.jersey.apache.connector.ApacheClientProperties;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientConfig;
import org.glassfish.jersey.client.ClientProperties;
import org.glassfish.jersey.filter.LoggingFilter;
import ru.yandex.autotests.mordabackend.actions.CleanvarsActions;
import ru.yandex.autotests.mordabackend.actions.GeohelperActions;
import ru.yandex.autotests.mordabackend.actions.GpsaveActions;
import ru.yandex.autotests.mordabackend.actions.LogsActions;
import ru.yandex.autotests.mordabackend.actions.OperaDataActions;
import ru.yandex.autotests.mordabackend.actions.RapidoActions;
import ru.yandex.autotests.mordabackend.actions.ThemeActions;
import ru.yandex.autotests.mordabackend.actions.TuneActions;
import ru.yandex.autotests.mordacommonsteps.Properties;
import ru.yandex.autotests.utils.morda.url.Domain;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.core.MediaType;
import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;
import java.util.Map;
import java.util.logging.Logger;
import java.util.regex.Pattern;

import static com.fasterxml.jackson.databind.AnnotationIntrospector.pair;
import static ru.yandex.autotests.utils.morda.BaseProperties.MordaEnv;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;

/**
 * User: lanqu
 * Date: 24.04.13
 */
public class MordaClient {
    private static final String MORDA_URL_PATTERN = "%s://%s.yandex%s";

    private static final ru.yandex.autotests.mordacommonsteps.Properties COMMON_CONFIG = new Properties();

    private final String protocol;
    private final MordaEnv mordaEnv;
    private final Domain domain;
    private final URI mordaHost;
    private static ObjectMapper objectMapper;

    public MordaClient(MordaEnv mordaEnv) {
        this("http", mordaEnv, RU);
    }

    public MordaClient(MordaEnv mordaEnv, Domain domain) {
        this("http", mordaEnv, domain);
    }
    public MordaClient(String protocol, MordaEnv mordaEnv) {
        this(protocol, mordaEnv, RU);
    }

    public MordaClient(String protocol, MordaEnv mordaEnv, Domain domain) {
        this.protocol = protocol;
        this.mordaEnv = mordaEnv;
        this.domain = domain;
        this.mordaHost = URI.create(String.format(MORDA_URL_PATTERN, protocol, mordaEnv, domain));
    }

    public MordaClient(URI mordaHost) {
        this.mordaHost = mordaHost;

        // Для совместимости, но, кажется, нигде не надо
        this.protocol = mordaHost.getScheme();
        String h = mordaHost.getHost();
        this.mordaEnv = new MordaEnv(h.substring(0, h.indexOf('.')));
        this.domain = Domain.getDomain(mordaHost.toString());
    }

    public ThemeActions themeActions() {
        return themeActions(getJsonEnabledClient());
    }

    public ThemeActions themeActions(Client client) {
        return new ThemeActions(this, client);
    }

    public CleanvarsActions cleanvarsActions() {
        return cleanvarsActions(getJsonEnabledClient());
    }

    public CleanvarsActions cleanvarsActions(Client client) {
        return new CleanvarsActions(this, client);
    }

    public RapidoActions rapidoActions() {
        return rapidoActions(getJsonEnabledClient());
    }

    public RapidoActions rapidoActions(Client client) {
        return new RapidoActions(this, client);
    }

    public TuneActions tuneActions() {
        return tuneActions(getJsonEnabledClient());
    }

    public TuneActions tuneActions(Client client) {
        return new TuneActions(this, client);
    }

    public LogsActions logsActions(Client client) {
        return new LogsActions(this, client);
    }

    public GeohelperActions geohelperActions() {
        return geohelperActions(getJsonEnabledClient());
    }

    public GeohelperActions geohelperActions(Client client) {
        return new GeohelperActions(this, client);
    }

    public OperaDataActions operaDataActions() {
        return operaDataActions(getJsonEnabledClient());
    }

    public OperaDataActions operaDataActions(Client client) {
        return new OperaDataActions(this, client);
    }

    public GpsaveActions gpsaveActions() {
        return gpsaveActions(getJsonEnabledClient());
    }

    public GpsaveActions gpsaveActions(Client client) {
        return new GpsaveActions(this, client);
    }

    public String getProtocol() {
        return protocol;
    }

    public MordaEnv getMordaEnv() {
        return mordaEnv;
    }

    public Domain getDomain() {
        return domain;
    }

    public URI getMordaHost() {
        return mordaHost;
    }

    private static final ApacheConnectorProvider CONNECTOR_PROVIDER = new ApacheConnectorProvider();
    private static final JacksonJaxbJsonProvider JSON_PROVIDER;
    private static final LoggingFilter LOGGING_FILTER = new LoggingFilter(Logger.getAnonymousLogger(), false);

    static {
        objectMapper = new ObjectMapper();
        objectMapper.setAnnotationIntrospector(pair(new JaxbAnnotationIntrospector(TypeFactory.defaultInstance()) {
            @Override
            public Class<?> _doFindDeserializationType(Annotated a, JavaType baseContentType) {
                return null;
            }
        }, new JacksonAnnotationIntrospector()))
                .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                .enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
        JSON_PROVIDER = new JacksonJaxbJsonProvider(objectMapper, JacksonJaxbJsonProvider.DEFAULT_ANNOTATIONS) {
            @Override
            protected boolean hasMatchingMediaType(MediaType mediaType) {
                return mediaType.isCompatible(MediaType.TEXT_PLAIN_TYPE) || super.hasMatchingMediaType(mediaType);
            }
        };
    }

    public static Client getJsonEnabledClient() {
        return getJsonEnabledClient(getRemapHostDnsResolver());
    }

    public static Client getJsonEnabledClient(DnsResolver dnsResolver) {
        ClientConfig cc = new ClientConfig();
        cc.connectorProvider(CONNECTOR_PROVIDER);
        cc.register(JSON_PROVIDER);
        cc.register(LOGGING_FILTER);
        cc.property(ApacheClientProperties.CONNECTION_MANAGER, new PoolingHttpClientConnectionManager(
                RegistryBuilder.<ConnectionSocketFactory>create()
                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
                        .register("https", new SSLConnectionSocketFactory(SSLContexts.createDefault(),
                                SSLConnectionSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER)).build(),
                dnsResolver));
        Client client = ClientBuilder.newBuilder().withConfig(cc).build();
        client.property(ClientProperties.CONNECT_TIMEOUT, 30000);
        client.property(ClientProperties.READ_TIMEOUT,    30000);
        return client;
    }

//    public static Client getJsonEnabledClient(DnsResolver dnsResolver) {
//        ClientConfig cc = new ClientConfig();
//        cc.connectorProvider(CONNECTOR_PROVIDER);
//        cc.register(JSON_PROVIDER);
//        cc.register(LOGGING_FILTER);
//        cc.property(ApacheClientProperties.CONNECTION_MANAGER, new PoolingHttpClientConnectionManager(
//                RegistryBuilder.<ConnectionSocketFactory>create()
//                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
//                        .register("https", new SSLConnectionSocketFactory(SSLContexts.createDefault(),
//                                SSLConnectionSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER)).build(),
//                dnsResolver));
//
//        TrustManager[] trustAllCerts = new TrustManager[]{new X509TrustManager(){
//            public X509Certificate[] getAcceptedIssuers() {
//                return null;
//            }
//            public void checkClientTrusted(X509Certificate[] certs, String authType){}
//            public void checkServerTrusted(X509Certificate[] certs, String authType){}
//        }};
//
//        try {
//
//            SSLContext sc = SSLContext.getInstance("SSL");
//            sc.init(null, trustAllCerts, new java.security.SecureRandom());
//
//            Client client = new JerseyClientBuilder().sslContext(sc).withConfig(cc).build();
//            client.property(ClientProperties.CONNECT_TIMEOUT, 30000);
//            client.property(ClientProperties.READ_TIMEOUT,    30000);
//            return client;
//        } catch (Throwable e) {
//            throw new RuntimeException(e);
//        }
//    }

    public static DnsResolver getRemapHostDnsResolver() {
        return new DnsResolver() {
            @Override
            public InetAddress[] resolve(String host) throws UnknownHostException {
                for (Map.Entry<Pattern, String> entry : COMMON_CONFIG.getRemap().entrySet()) {
                    if (entry.getKey().matcher(host).matches()) {
                        return InetAddress.getAllByName(entry.getValue());
                    }
                }
                return InetAddress.getAllByName(host);
            }
        };
    }

    public static ObjectMapper getObjectMapper() {
        return objectMapper;
    }
}
