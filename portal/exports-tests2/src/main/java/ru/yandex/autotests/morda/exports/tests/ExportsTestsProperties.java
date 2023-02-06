package ru.yandex.autotests.morda.exports.tests;

import org.apache.commons.beanutils.ConvertUtils;
import ru.yandex.autotests.morda.exports.tests.checks.ExportChecks;
import ru.yandex.autotests.mordacommonsteps.utils.ListConverter;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eroshenkoam
 * Date: 11/8/13, 1:57 PM
 */
@Resource.Classpath("morda-exports-tests.properties")
public class ExportsTestsProperties {

    public ExportsTestsProperties() {
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("morda.host")
    private URI mordaHost;

    @Property("exports.to.check")
    private List<String> exportsToCheck;

    public URI getMordaHost() {
        return mordaHost;
    }

    public List<String> getExportsToCheck() {
        return exportsToCheck != null
                ? exportsToCheck
                : new ArrayList<>();
    }

    public List<ExportChecks> filter(List<ExportChecks> exportChecks) {
        return exportChecks.stream()
                .filter(this::needCheck)
                .collect(Collectors.toList());
    }

    public boolean needCheck(ExportChecks<?, ?> checks) {
        return getExportsToCheck().contains(checks.getExport().getName());
    }

}
