package ru.yandex.autotests.morda.exports;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.annotations.exports.MordaExportDescription;
import ru.yandex.autotests.morda.client.MordaClientBuilder;
import ru.yandex.autotests.morda.exports.interfaces.Entry;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.UriBuilder;
import java.io.Serializable;
import java.net.URI;
import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
public abstract class AbstractMordaExport<T extends AbstractMordaExport<T, E>, E extends Entry> implements Serializable {
    private static final Logger LOGGER = Logger.getLogger(AbstractMordaExport.class);
    private final String name;
    private final Class<T> clazz;
    private String version;

    protected AbstractMordaExport() {
        this.version = "undefined";
        this.name = getExportName();
        this.clazz = getExportClass();
    }

    public abstract List<E> getData();

    public List<Object> getJsonData() {
        return getData().stream()
                .map(Entry::getJson)
                .collect(Collectors.toList());
    }

    public T populate() {
        return populate(URI.create("https://www.yandex.ru"));
    }

    public T populate(String mordaHost) {
        return populate(URI.create(mordaHost));
    }

    private Response getExport(URI mordaHost) {
        URI exportUri = UriBuilder.fromUri(mordaHost)
                .queryParam("cleanvars", "1")
                .queryParam("export", getExportName())
                .build();

        LOGGER.info("Gettings export " + getExportName() + " from " + exportUri);

        Client client = MordaClientBuilder.mordaClient()
                .failOnUnknownProperties(false)
                .acceptSingleValueAsArray(true)
                .withLogging(false)
                .build();

        return client.target(exportUri)
                .request()
                .buildGet()
                .invoke();
    }

    public T populate(URI mordaHost) {
        T export = getExport(mordaHost).readEntity(getExportClass());

        updateData(export.getData());

        LOGGER.info("Found " + export.getData().size() + " entries");

        return getExportClass().cast(this);
    }

    private void updateData(List<E> list) {
        this.getData().clear();
        this.getData().addAll(list);
    }

    @SafeVarargs
    public final E findOne(Predicate<? super E>... predicates) {
        List<E> result = getData().stream()
                .filter(e -> asList(predicates).stream().allMatch(p -> p.test(e)))
                .collect(Collectors.toList());
        if (result.size() != 1) {
            throw new IllegalStateException("Expected exactly 1 matching entry. Found: " + result.size());
        }
        return result.get(0);
    }

    @SafeVarargs
    public final List<E> find(Predicate<? super E>... predicates) {
        return getData().stream()
                .filter(e -> asList(predicates).stream().allMatch(p -> p.test(e)))
                .collect(Collectors.toList());
    }

    public Class<T> getClazz() {
        return clazz;
    }

    public String getName() {
        return name;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    protected String getExportName() {
        if (this.getClass().isAnnotationPresent(MordaExportDescription.class)) {
            MordaExportDescription description = this.getClass().getAnnotation(MordaExportDescription.class);
            return description.name();
        } else {
            throw new IllegalStateException("Add MordaExportDescription annotation or override getExportName() method");
        }
    }

    @SuppressWarnings("unchecked")
    protected Class<T> getExportClass() {
        if (this.getClass().isAnnotationPresent(MordaExportDescription.class)) {
            MordaExportDescription description = this.getClass().getAnnotation(MordaExportDescription.class);
            return (Class<T>) description.clazz();
        } else {
            throw new IllegalStateException("Add MordaExportDescription annotation or override getExportClass() method");
        }
    }

    @Override
    public String toString() {
        return "Export \"" + name + "\"";
    }
}
