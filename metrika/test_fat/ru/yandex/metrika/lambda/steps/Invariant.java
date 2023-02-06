package ru.yandex.metrika.lambda.steps;

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.IOUtils;

import ru.yandex.inside.yt.kosher.cypress.YPath;

public class Invariant {

    private static final Pattern TABLE_NAME_PATTERN = Pattern.compile("(^|/)(?<name>\\w+)($|.yql$)");

    private final String version;
    private final String scriptName;
    private String scriptTemplate;

    public Invariant(String version, String scriptName) {
        this.version = version;
        this.scriptName = scriptName;
        loadScriptTemplate();
    }

    @Override
    public String toString() {
        return String.format("%s (%s)", scriptName, version);
    }

    private void loadScriptTemplate() {
        try {
            scriptTemplate = IOUtils.toString(this.getClass().getResource(String.format("invariants/%s/%s", version, scriptName)), Charset.defaultCharset());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public String getVersion() {
        return version;
    }

    public String getScriptName() {
        return scriptName;
    }

    public String getTableName() {
        Matcher matcher = TABLE_NAME_PATTERN.matcher(scriptName);
        if (matcher.find()) {
            return matcher.group("name");
        } else {
            return null;
        }
    }

    public String getScriptTemplate() {
        return scriptTemplate;
    }

    public YPath getTable() {
        return YPath.simple(InvariantsChecker.INVARIANT_ROOT).child(getTableName());
    }
}
