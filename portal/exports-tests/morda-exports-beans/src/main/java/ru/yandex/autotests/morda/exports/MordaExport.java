package ru.yandex.autotests.morda.exports;

import ru.yandex.autotests.morda.exports.annotations.MordaExportDescription;
import ru.yandex.autotests.morda.utils.client.MordaClientBuilder;

import javax.ws.rs.client.Client;
import java.io.Serializable;
import java.net.URI;
import java.util.List;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
public abstract class MordaExport<T extends MordaExport<T, E>, E> implements Serializable {

    private final String name;
    private final Class<T> clazz;
    private String version;

    protected MordaExport() {
        this.version = "undefined";
        this.name = getExportName();
        this.clazz = getExportClass();
    }

    public abstract List<E> getData();

    public T populate() {
        return populate(URI.create("https://www.yandex.ru"));
    }

    public T populate(String mordaHost) {
        return populate(URI.create(mordaHost));
    }

    public T populate(URI mordaHost) {
        Client client = MordaClientBuilder.mordaClient()
                .failOnUnknownProperties(false)
                .acceptSingleValueAsArray(true)
                .withLogging(false)
                .build();

        T export = client.target(mordaHost)
                .queryParam("cleanvars", "1")
                .queryParam("export", getExportName())
                .request()
                .buildGet()
                .invoke()
                .readEntity(getExportClass());

        updateData(export.getData());

        return getExportClass().cast(this);
    }

    private void updateData(List<E> list) {
        this.getData().clear();
        this.getData().addAll(list);
    }

    @SafeVarargs
    public final Optional<E> findOne(Predicate<? super E>... predicates) {
        return getData().stream()
                .filter(e -> asList(predicates).stream().allMatch(p -> p.test(e)))
                .findFirst();
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
