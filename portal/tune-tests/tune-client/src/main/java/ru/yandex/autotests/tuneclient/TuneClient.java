package ru.yandex.autotests.tuneclient;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.introspect.Annotated;
import com.fasterxml.jackson.databind.introspect.JacksonAnnotationIntrospector;
import com.fasterxml.jackson.databind.type.TypeFactory;
import com.fasterxml.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationIntrospector;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLContexts;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.glassfish.jersey.apache.connector.ApacheClientProperties;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientConfig;
import org.glassfish.jersey.client.ClientProperties;
import org.glassfish.jersey.client.spi.CachingConnectorProvider;
import org.glassfish.jersey.filter.LoggingFilter;
import ru.yandex.autotests.tuneclient.actions.GeoSearchActions;
import ru.yandex.autotests.tuneclient.actions.LanguageActions;
import ru.yandex.autotests.tuneclient.actions.MyActions;
import ru.yandex.autotests.tuneclient.actions.RegionActions;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.core.MediaType;
import java.net.URI;
import java.util.logging.Logger;

import static com.fasterxml.jackson.databind.AnnotationIntrospector.pair;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/01/15
 */
public class TuneClient {

    public static final Properties CONFIG = new Properties();
    private final URI baseUri;
    private final String geoPath;
    private final String langPath;
    private final String myPath;
    private final String regionPath;

    public TuneClient() {
        this(CONFIG.getBaseURI());
    }

    public TuneClient(URI baseUri) {
        this(baseUri, CONFIG.getGeoPath(), CONFIG.getLangPath(), CONFIG.getMyPath(), CONFIG.getRegionPath());
    }

    public TuneClient(URI baseUri, String geoPath, String langPath, String myPath, String regionPath) {
        this.baseUri = baseUri;
        this.geoPath = geoPath;
        this.langPath = langPath;
        this.myPath = myPath;
        this.regionPath = regionPath;
    }

    public LanguageActions.Builder language() {
        return new LanguageActions.Builder(baseUri, langPath);
    }

    public RegionActions.Builder region() {
        return new RegionActions.Builder(baseUri, regionPath);
    }

    public MyActions.Builder my() {
        return new MyActions.Builder(baseUri, myPath);
    }

    public GeoSearchActions.Builder geoSearch() {
        return new GeoSearchActions.Builder(baseUri, geoPath);
    }

    private static final JacksonJaxbJsonProvider JSON_PROVIDER =
            new JacksonJaxbJsonProvider(new ObjectMapper(), JacksonJaxbJsonProvider.DEFAULT_ANNOTATIONS) {
                @Override
                protected boolean hasMatchingMediaType(MediaType mediaType) {
                    return mediaType.isCompatible(MediaType.TEXT_PLAIN_TYPE) || super.hasMatchingMediaType(mediaType);
                }
            };

    public static Client getClient() {
        ClientConfig cc = new ClientConfig();
        cc.property(ApacheClientProperties.CONNECTION_MANAGER, new PoolingHttpClientConnectionManager(
                RegistryBuilder.<ConnectionSocketFactory>create()
                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
                        .register("https", new SSLConnectionSocketFactory(SSLContexts.createDefault(),
                                SSLConnectionSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER)).build()));
        cc.connectorProvider(new CachingConnectorProvider(new ApacheConnectorProvider()));
        cc.register(JSON_PROVIDER);
        cc.register(new LoggingFilter(Logger.getAnonymousLogger(), false));
        return ClientBuilder.newClient(cc);
    }

}
