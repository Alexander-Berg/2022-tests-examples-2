package ru.yandex.autotests.mainmorda.blocks;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * User: alex89
 * Date: 17.12.12
 */

public class WidgetInCatalog extends Widget {
    private static final String WIDGET_ID_PATTERN = "[A-Za-z0-9/.:-]+\\?add=([_A-Za-z0-9]+)&[=A-Za-z0-9%&/.-]+";
    Pattern validationPattern = Pattern.compile(WIDGET_ID_PATTERN);

    @Override
    public String getWidgetName() {
        Matcher idFormat = validationPattern.matcher(getWrappedElement().getAttribute("href"));
        idFormat.matches();
        return idFormat.group(1);
    }
}
