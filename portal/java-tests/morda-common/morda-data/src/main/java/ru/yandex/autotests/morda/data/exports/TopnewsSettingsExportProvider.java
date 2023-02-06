package ru.yandex.autotests.morda.data.exports;

import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.autotests.morda.beans.exports.topnews_settings.TopnewsSettingsExport;

import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/06/16
 */
public class TopnewsSettingsExportProvider {
    private static final MordaPagesProperties PAGES_CONFIG = new MordaPagesProperties();
    private static final TopnewsSettingsExport TOPNEWS_SETTINGS = new TopnewsSettingsExport().populate(
            desktopMain(PAGES_CONFIG.getEnvironment()).getUrl()
    );

//    public static TopnewsSettingsEntry getTopnewsEntry(Morda<?> morda) throws JsonProcessingException {
//        List<TopnewsSettingsEntry> entries = TOPNEWS_SETTINGS.find(
//                MordaContentFilter.filter(morda.getMordaType().getContent()),
//                MordaDomainFilter.filter(morda.getDomain()),
//                MordaLanguageFilter.filter(morda.getLanguage()),
////                MordaGeoFilter.filter(morda.getRegion())
//        );
//
//        Comparator<TopnewsSettingsEntry> c = Comparator.nullsLast(new MordaContentFilter.MordaContentFilterComparator());
//
//        entries.sort(c);
//
//        for (TopnewsSettingsEntry entry : entries) {
//            System.out.println(entry.getDomain() + " " + entry.getContent() + " " + entry.getGeo().getRegion());
//        }
//        return null;
//    }
//
//    public static void main(String[] args) throws JsonProcessingException {
//        getTopnewsEntry(desktopMain().region(Russia.MOSCOW));
//    }

//    public ServicesV122Entry getServicesV12Entry(String serviceId, Morda<?> morda) {
//        return getServicesV12Entry(serviceId, morda.getDomain());
//    }

}
