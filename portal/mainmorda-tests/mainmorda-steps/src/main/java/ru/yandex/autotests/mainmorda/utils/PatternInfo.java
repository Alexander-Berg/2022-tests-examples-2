package ru.yandex.autotests.mainmorda.utils;

import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.utils.morda.auth.User;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public class PatternInfo {
    private User login;

    private String skinId;
    private List<WidgetsData.WidgetInfo> widgets;

    public PatternInfo(User login, String skinId, List<WidgetsData.WidgetInfo> widgets) {
        this.login = login;
        this.skinId = skinId;
        this.widgets = widgets;
    }

    public User getLogin() {
        return login;
    }

    public String getSkinId() {
        return skinId;
    }

    public List<WidgetsData.WidgetInfo> getWidgets() {
        return widgets;
    }

    @Override
    public String toString() {
        return login.getLogin();
    }
}