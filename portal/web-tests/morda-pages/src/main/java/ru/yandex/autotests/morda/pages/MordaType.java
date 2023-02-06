package ru.yandex.autotests.morda.pages;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/04/15
 */
public enum MordaType {

//    ** DESKTOP **

    D_COM,
    D_COMTR,
    D_COMTRALL,
    D_COMTRFOOTBALL,
    D_FIREFOX,
    D_HWBMW,
    D_HWLG,
    D_MAIN,
    D_MAINALL,
    D_PAGE404,
    D_COM_404,
    D_YARU,
    D_OP,
    D_SPOK,

//    ** PDA **

    P_COM,
    P_COMTR,
    P_COMTRALL,
    P_RU,
    P_RUALL,
    P_YARU,

//    ** TOUCH **

    T_COM,
    T_COMTR,
    T_COMTRALL,
    T_COMTRWP,
    T_RU,
    T_YARU,
    T_RUALL,
    T_RUWP,
    T_SPOK,

//    ** TUNE **

    TUNE_MAIN,
    TUNE_COM,
    TUNE_COM_TR,

//     ** TV **

    SMART_TV,

//     ** EMBED_SEARCH **

    EMBED_SEARCH;

    public static <T extends Morda<?>> List<T> filter(List<T> mordas, Collection<MordaType> types) {
        return mordas.stream()
                .filter((m) -> types.contains(m.getMordaType()))
                .collect(Collectors.toList());
    }

    public static <T extends Morda<?>> List<T> filter(List<T> mordas, MordaType... types) {
        return filter(mordas, asList(types));
    }

    //unsafe: filter constructor parameters where first parameter is Morda
    public static Collection<Object[]> filter(Collection<Object[]> constructorParameters, Collection<MordaType> types) {
        return  constructorParameters.stream()
                .filter(p -> types.contains(((Morda<?>) p[0]).getMordaType()))
                .collect(Collectors.toList());
    }
}
