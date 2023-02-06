package ru.yandex.metrika.lambda.steps;

import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.cypress.CypressNodeType;
import ru.yandex.inside.yt.kosher.cypress.YPath;

public final class YtUtils {
    private YtUtils() {
    }

    public static void ensureTable(Yt yt, YPath yPath) {
        String rawType = yt.cypress().get(yPath.attribute("type")).stringValue();
        CypressNodeType nodeType = CypressNodeType.R.fromName(rawType);
        if (!nodeType.equals(CypressNodeType.TABLE)) {
            throw new RuntimeException(String.format("'%s' is not a table", yPath.toString()));
        }
    }

    public static void ensureMap(Yt yt, YPath yPath) {
        String rawType = yt.cypress().get(yPath.attribute("type")).stringValue();
        CypressNodeType nodeType = CypressNodeType.R.fromName(rawType);
        if (!nodeType.equals(CypressNodeType.MAP)) {
            throw new RuntimeException(String.format("'%s' is not a directory", yPath.toString()));
        }
    }

}
