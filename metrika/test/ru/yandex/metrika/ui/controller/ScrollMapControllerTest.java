package ru.yandex.metrika.ui.controller;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;

import org.junit.Ignore;
import org.junit.Test;

/**
 * @author Ivan Gorbachev
 * @version $ld$
 * @since 5/24/12
 */
@Ignore
public class ScrollMapControllerTest {

    private static final String URL = "http://localhost:8083";

    private static final String[] PARAM_NAMES = {
            "id",
            "url",
            "date1",
            "date2",
            "filter",
            "height"};

    //SELECT SUM(scrollCount) ss, tab1.counterId, tab2.uri FROM WV_5.events tab1, (SELECT uri, visitId, watchid FROM WV_5.hits WHERE dayNumber = 1612) tab2 WHERE tab1.dayNumber = 1612 AND  tab1.watchId = tab2.watchId GROUP BY tab1.counterId, tab2.uri ORDER BY ss DESC;
    //SELECT CONCAT('{', tab1.counterId), CONCAT('"', tab2.uri, '"'), '"20120530"', '"20120614"', 5000 FROM WV_5.events tab1, (SELECT uri, visitId, watchid FROM WV_5.hits WHERE dayNumber = 1612) tab2 WHERE tab1.dayNumber = 1612 AND  tab1.watchId = tab2.watchId GROUP BY tab1.counterId, tab2.uri ORDER BY SUM(scrollCount) DESC;
    private static final Object[][] VALUES = {
            {666855, "http://playstation3.nextgame.net/games/index.php?count=all",
                    "20120523", "20120523", "", 2178},
            {1162915, "http://nogtoc.ucoz.com/photo/1",
                    "20120523", "20120523", "", 2178},
            {1157615, "http://dgr.ru/psychology/otvety/6",
                    "20120523", "20120523", "", 2178},
            {995075, "http://tezpoisk.ru/",
                    "20120523", "20120523", "", 2178},
            {1377705, "http://rozhdestvenka.ru/horovod/Pesni-all.htm",
                    "20120523", "20120523", "", 2178},
            {802545, "http://neopoliscasa.ru/catalog.html",
                    "20120523", "20120523", "", 2178},
            {802545, "http://neopoliscasa.ru/catalog.html",
                    "20120521", "20120525", "", 2178},
            {666855, "http://playstation3.nextgame.net/games/index.php?count=all",
                    "20120531", "20120531", "", 2000},
            {995075, "http://tezpoisk.ru/",
                    "20120531", "20120531", "", 2000},
            {1162915, "http://nogtoc.ucoz.com/photo/1",
                    "20120531", "20120531", "", 2000},
            {802545, "http://neopoliscasa.ru/catalog.html",
                    "20120531", "20120531", "", 2000},
            {995075, "http://tezpoisk.ru/",
                    "20120530", "20120607", "", 2000},

            {763105, "http://авточехлы.рф/covers.html/",
                    "20120531", "20120615", "", 8212},
    };

    private static final Object[][] VALUES_2 = {{995075, "http://tezpoisk.ru/", "20120530", "20120610", "", 5000},
            {763105, "http://xn--80aejynxxo3b.xn--p1ai/covers.html", "20120530", "20120610", "", 5000},
            {1162915, "http://nogtoc.ucoz.com/photo/1", "20120530", "20120610", "", 5000},
            {1234985, "http://evalar.ru/ru/consumer/production/alphabet/", "20120530", "20120610", "", 5000},
            {724005, "http://avtobukvar.ru/servise/podbor_podshipnikov_po_razmeram.html", "20120530", "20120610", "", 5000},
            {971125, "http://l-oko.ru/article.php?id=1488", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/?forwhom=male", "20120530", "20120610", "", 5000},
            {520455, "http://a-centre.ru/publ1.php?publid=43", "20120530", "20120610", "", 5000},
            {802545, "http://neopoliscasa.ru/catalog.html", "20120530", "20120610", "", 5000},
            {924375, "http://turbotext.ru/orders/search/", "20120530", "20120610", "", 5000},
            {1170895, "http://tricolor.vip-tv.ru/", "20120530", "20120610", "", 5000},
            {1157615, "http://dgr.ru/psychology/otvety/4", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/?forwhom=female", "20120530", "20120610", "", 5000},
            {949635, "http://paintball-for-all.ru/marker_amateur.html", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/?forwhom=child", "20120530", "20120610", "", 5000},
            {763105, "http://xn--80aejynxxo3b.xn--p1ai/constructor.html", "20120530", "20120610", "", 5000},
            {1010595, "http://stone.sadby.org/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-vechernie-platya-c-10_107", "20120530", "20120610", "", 5000},
            {541525, "http://ultra-music.com/vosien", "20120530", "20120610", "", 5000},
            {669175, "http://neointerno.ru/catalog/stoly-obedennye", "20120530", "20120610", "", 5000},
            {991185, "http://insi.ru/directions/metalocherepica/", "20120530", "20120610", "", 5000},
            {1393625, "http://nogomatch.ru/", "20120530", "20120610", "", 5000},
            {520455, "http://a-centre.ru/", "20120530", "20120610", "", 5000},
            {1389535, "http://edustrong.ru/func.php", "20120530", "20120610", "", 5000},
            {1310205, "http://ecookna.ru/", "20120530", "20120610", "", 5000},
            {1284635, "http://geoplenka.ru/kak-sdelat-prud.html", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/", "20120530", "20120610", "", 5000},
            {630595, "http://dancan.ru/klyuchi-dlya-eset-smart-security-5/", "20120530", "20120610", "", 5000},
            {1209095, "http://ecgz.ru/zakupki_po_fz_223.htm", "20120530", "20120610", "", 5000},
            {673805, "http://mirdvornikov.ru/content/articles/tipy-kreplenij-stekloochistitelej/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-kokteilnye-platya-c-10_109", "20120530", "20120610", "", 5000},
            {532075, "http://vodaservis.ru/price/price8/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-platya-bolshih-razmerov-c-10_113", "20120530", "20120610", "", 5000},
            {1015385, "http://pro-goszakaz.ru/regulations/67413/", "20120530", "20120610", "", 5000},
            {1157615, "http://dgr.ru/psychology/otvety/6", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/iso/13_gosty_iso/13020_gost_iso/1302040_gost_iso/3166-metodika-provedeniya-inventarizacii-vybrosov-zagryaznyayuschih-veschestv-v-atmosferu-na-predpriyatiyah-zheleznodorozhnogo-transporta.html", "20120530", "20120610", "", 5000},
            {1186245, "http://eurobit.ru/cash/sites0/dostavka.html", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/photo_less_2", "20120530", "20120610", "", 5000},
            {1016845, "http://sfort.ru/", "20120530", "20120610", "", 5000},
            {1189225, "http://kipr.grandtour.ru/", "20120530", "20120610", "", 5000},
            {529555, "http://volleymsk.ru/", "20120530", "20120610", "", 5000},
            {570115, "http://astro7.ru/", "20120530", "20120610", "", 5000},
            {991185, "http://insi.ru/edifice/", "20120530", "20120610", "", 5000},
            {780805, "http://horoshevo-mnevniki.ru/governance/okno/multifunctional-centre/", "20120530", "20120610", "", 5000},
            {529555, "http://volleymsk.ru/forum/index.php", "20120530", "20120610", "", 5000},
            {1225635, "http://dentastom.com/clinics.php", "20120530", "20120610", "", 5000},
            {647325, "http://trkr.ru/article/full/1301912611.html", "20120530", "20120610", "", 5000},
            {523015, "http://mafia-world.ru/mafia2-news/368-playboy-mags-from-mafia-2.html", "20120530", "20120610", "", 5000},
            {542755, "http://krd.name/joy/anapa/pozor/3353.html", "20120530", "20120610", "", 5000},
            {1246435, "http://tiptip.ru/beshbarmak.php", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/desyatka_sobak_samih_blizkih_k_volkam_", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/pricheska_iz_dvuh_kosichek_po_bokam", "20120530", "20120610", "", 5000},
            {666855, "http://xbox360.nextgame.net/accessories/", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/pricheska_iz_obratnoi_francuzskoi_kosi", "20120530", "20120610", "", 5000},
            {701695, "http://belhuntclub.net/forums/", "20120530", "20120610", "", 5000},
            {1361285, "http://my-strongdc.ru/%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0-strong-dc/", "20120530", "20120610", "", 5000},
            {1253415, "http://svarog-spb.ru/catalog/invertors/mma/", "20120530", "20120610", "", 5000},
            {777915, "http://netuning.ru/index.php?show_aux_page=10", "20120530", "20120610", "", 5000},
            {561575, "http://amocrm.ru/", "20120530", "20120610", "", 5000},
            {949635, "http://paintball-for-all.ru/marker_sport.html", "20120530", "20120610", "", 5000},
            {1128625, "http://domostroymedia.ru/", "20120530", "20120610", "", 5000},
            {1139975, "http://autlet.ru/eshop.php", "20120530", "20120610", "", 5000},
            {1315865, "http://vezetvsem.info/map/avito", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/pricheska_iz_kosichek_vechernia", "20120530", "20120610", "", 5000},
            {756865, "http://loveinacity.ru/love/glotat-ili-net.html", "20120530", "20120610", "", 5000},
            {859365, "http://skylink.ms/tarifs/", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/pricheska_dlya_kaskadnyh_volos", "20120530", "20120610", "", 5000},
            {859365, "http://skylink.ms/?mode=rubric&rid=2", "20120530", "20120610", "", 5000},
            {582765, "http://infanty.ru/category/tekstil/aksessuary?view=all", "20120530", "20120610", "", 5000},
            {981365, "http://domocomplect.ru/all_katalog/proekty_domov/vse_proekty/", "20120530", "20120610", "", 5000},
            {1408915, "http://nakolomenskoy-mitsubishi.ru/special-offers/563/", "20120530", "20120610", "", 5000},
            {1198225, "http://kosmetiksavto.ru/", "20120530", "20120610", "", 5000},
            {666855, "http://playstation3.nextgame.net/accessories/", "20120530", "20120610", "", 5000},
            {1003925, "http://best-of-moto.ru/index.php?categoryID=1736&category_slug=elektroskutery-i-elektrovelosipedy_s1", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/vypusknye-platya-c-140", "20120530", "20120610", "", 5000},
            {658315, "http://zakon-help.ru/", "20120530", "20120610", "", 5000},
            {1420155, "http://k-v-a-r-t-i-r-a.ru/", "20120530", "20120610", "", 5000},
            {1280275, "http://tranio.ru/world/analytics/property_buyers_report_2012/", "20120530", "20120610", "", 5000},
            {1246435, "http://tiptip.ru/recept-kuksi.php", "20120530", "20120610", "", 5000},
            {1132765, "http://portative.by/", "20120530", "20120610", "", 5000},
            {1144085, "http://nissan.nnmotors.ru/nissan/cars/nissan_qashqai/specifications/", "20120530", "20120610", "", 5000},
            {949635, "http://paintball-for-all.ru/price_paintball.html", "20120530", "20120610", "", 5000},
            {647325, "http://trkr.ru/article/full/1256654999.html", "20120530", "20120610", "", 5000},
            {1089855, "http://zagran-passport.ru/poryadok.php", "20120530", "20120610", "", 5000},
            {1190985, "http://naprostore.ru/node/6", "20120530", "20120610", "", 5000},
            {1333235, "http://arsagera.ru/kuda_i_kak_investirovat/investicionnye_opasnosti/foreks_genii_marketinga/", "20120530", "20120610", "", 5000},
            {655865, "http://camozzi.ru/", "20120530", "20120610", "", 5000},
            {1237885, "http://housebt.ru/auxpage_dostavka1/", "20120530", "20120610", "", 5000},
            {1246435, "http://tiptip.ru/recept-lagman.php", "20120530", "20120610", "", 5000},
            {1356125, "http://krasotka-story.ru/story-foto", "20120530", "20120610", "", 5000},
            {1157505, "http://cinemaniashop.ru/", "20120530", "20120610", "", 5000},
            {1188885, "http://quto.ru/pdd/question/#pdd", "20120530", "20120610", "", 5000},
            {1188885, "http://quto.ru/pdd/result/", "20120530", "20120610", "", 5000},
            {960295, "http://master-deco.ru/catalog211_1.html", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/node/37", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/kamchatka/", "20120530", "20120610", "", 5000},
            {1127925, "http://menobr.ru/materials/164/4930/", "20120530", "20120610", "", 5000},
            {722185, "http://read.ru/genre/2373/", "20120530", "20120610", "", 5000},
            {1393625, "http://nogomatch.ru/foto/%D0%90%D0%B4%D1%81%D0%BA%D0%B8%D0%B5-%D1%84%D0%BE%D1%82%D0%BE-%D0%B8-%D0%B7%D0%B0%D0%B3%D0%BE%D1%82%D0%BE%D0%B2%D0%BA%D0%B8-%D0%B6%D0%B0%D0%B1", "20120530", "20120610", "", 5000},
            {1011595, "http://teplodar.ru/catalog/pechi-sauna-banya/", "20120530", "20120610", "", 5000},
            {1320385, "http://taxibox.ru/", "20120530", "20120610", "", 5000},
            {666985, "http://domosedka.com/publ/samye_vkusnye_bljuda_iz_kabachkov/9-1-0-633", "20120530", "20120610", "", 5000},
            {926065, "http://sochi.aelita.su/sanatorii-sochi-price/", "20120530", "20120610", "", 5000},
            {591685, "http://infop.ru/products/buchgalteria/free/", "20120530", "20120610", "", 5000},
            {1394195, "http://detkiuch.ru/stuff/igry_dlja_detej/detskie_obuchajushhie/prover_tablicu_umnozhenija/6-1-0-5170", "20120530", "20120610", "", 5000},
            {497685, "http://pardi.ru/index.php?categoryID=151&sort=name_in_stock&direction=DESC&show_all=yes", "20120530", "20120610", "", 5000},
            {1280275, "https://tranio.ru/my-adt/create/", "20120530", "20120610", "", 5000},
            {1190985, "http://naprostore.ru/", "20120530", "20120610", "", 5000},
            {1190985, "http://naprostore.ru/ChooseRealtor", "20120530", "20120610", "", 5000},
            {738665, "http://luxclimat.ru/katalog/daikin/", "20120530", "20120610", "", 5000},
            {1345175, "http://new-cian.ru/", "20120530", "20120610", "", 5000},
            {859365, "http://skylink.ms/?mode=rubric&rid=1", "20120530", "20120610", "", 5000},
            {1157505, "http://cinemaniashop.ru/chemodani/siutsasesadult/britto/b703-2624-987/", "20120530", "20120610", "", 5000},
            {1281755, "http://es-gaming.ru/", "20120530", "20120610", "", 5000},
            {733775, "http://giftbasket.ru/catalog/balloons/", "20120530", "20120610", "", 5000},
            {1043975, "http://afisha-ola.ru/?content=47&module=repertoire&id=16", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/pricheska_dla_nastoiashih_ledy", "20120530", "20120610", "", 5000},
            {924375, "http://turbotext.ru/microtask/search/", "20120530", "20120610", "", 5000},
            {717235, "http://puffy-shop.ru/9-sumki-perenoski", "20120530", "20120610", "", 5000},
            {1157505, "http://cinemaniashop.ru/chemodani/siutsasesadult/monroe/59113-401/", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/node/65", "20120530", "20120610", "", 5000},
            {647325, "http://trkr.ru/article/full/1273601318.html", "20120530", "20120610", "", 5000},
            {1129175, "http://redkassa.ru/", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/kamchatka", "20120530", "20120610", "", 5000},
            {788235, "http://dom.ya1.ru/index.php?newsid=2278", "20120530", "20120610", "", 5000},
            {1016845, "http://sfort.ru/flats/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-vechernie-platya-c-10_107?sort=3b&page=3", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/israel/", "20120530", "20120610", "", 5000},
            {885965, "http://shinamarket.ru/podborparam/", "20120530", "20120610", "", 5000},
            {717235, "http://puffy/", "20120530", "20120610", "", 5000},
            {1234985, "http://evalar.ru/ru/consumer/purchase/evalar/", "20120530", "20120610", "", 5000},
            {802545, "http://neopoliscasa.ru/catalog/mebel-gostinaya_3.html", "20120530", "20120610", "", 5000},
            {582765, "http://infanty.ru/category/mebel/detskie-krovatki?view=all", "20120530", "20120610", "", 5000},
            {676095, "http://askona-shop.ru/catalogmatras/49/", "20120530", "20120610", "", 5000},
            {582765, "http://infanty.ru/category/mebel/detskie-krovatki", "20120530", "20120610", "", 5000},
            {1203425, "http://intercollege.su/", "20120530", "20120610", "", 5000},
            {1043975, "http://afisha-ola.ru/?content=39&module=repertoire&id=15", "20120530", "20120610", "", 5000},
            {630595, "http://dancan.ru/esli-ne-zapuskaetsya-ili-vyletaet-skyrim/", "20120530", "20120610", "", 5000},
            {1246435, "http://tiptip.ru/recept-manty.php", "20120530", "20120610", "", 5000},
            {734635, "http://rys-stroi.ru/service/3-remont-sanuzlov.html", "20120530", "20120610", "", 5000},
            {717235, "http://puffy-shop.ru/", "20120530", "20120610", "", 5000},
            {1127775, "http://magok.ru/cart/", "20120530", "20120610", "", 5000},
            {1408915, "http://nakolomenskoy-mitsubishi.ru/auto/outlander-xl/equipment/", "20120530", "20120610", "", 5000},
            {1234985, "http://evalar.ru/ru/presscentre/articles/index.php?id_4=228", "20120530", "20120610", "", 5000},
            {782585, "http://nym-nym.msk.ru/", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/?forwhom=hit", "20120530", "20120610", "", 5000},
            {1408915, "http://nakolomenskoy-mitsubishi.ru/auto/cars-in-stock/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-kokteilnye-platya-c-10_109?sort=3b&page=2", "20120530", "20120610", "", 5000},
            {1408915, "http://nakolomenskoy-mitsubishi.ru/auto/asx/equipment/", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/", "20120530", "20120610", "", 5000},
            {1237885, "http://housebt.ru/auxpage_samovyvoz/", "20120530", "20120610", "", 5000},
            {1253415, "http://svarog-spb.ru/", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/", "20120530", "20120610", "", 5000},
            {1370655, "http://rostov.aif.ru/society/news/42482", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/sobachi_godi_-_chelovecheskaya_zhizn/", "20120530", "20120610", "", 5000},
            {1129175, "http://redkassa.ru/events/52673-bilety_na_festival_nashestvie_2012/", "20120530", "20120610", "", 5000},
            {991185, "http://insi.ru/edifice/bvd2/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/klassicheskie-platya-c-146", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/iso/03_gosty_iso/03040_gost_iso/2044-tarifno-kvalifikacionnye-harakteristiki-po-obscheotraslevym-dolzhnostyam-sluzhaschih.html", "20120530", "20120610", "", 5000},
            {1127775, "http://magok.ru/", "20120530", "20120610", "", 5000},
            {917345, "http://invaprom.ru/cat.php?cat_id=28", "20120530", "20120610", "", 5000},
            {1334485, "http://mir-vann.ru/", "20120530", "20120610", "", 5000},
            {1310205, "http://ecookna.ru/rates/", "20120530", "20120610", "", 5000},
            {971125, "http://l-oko.ru/article.php?id=1472", "20120530", "20120610", "", 5000},
            {502715, "http://shatura-mebel.com/goods/fyudjn", "20120530", "20120610", "", 5000},
            {1234985, "http://evalar.ru/ru/consumer/production/parameter/?id_4=37", "20120530", "20120610", "", 5000},
            {591685, "http://infop.ru/products/buchgalteria/", "20120530", "20120610", "", 5000},
            {1234475, "http://braintools.ru/article/9775", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/node/40", "20120530", "20120610", "", 5000},
            {721875, "http://salon-shakti.msk.ru/catalog/list.php?SECTION_ID=94", "20120530", "20120610", "", 5000},
            {717235, "http://puffy-shop.ru/8-maiki-dlya-sobak", "20120530", "20120610", "", 5000},
            {1144085, "http://nissan.nnmotors.ru/nissan/cars/nissan_x_trail/specifications/", "20120530", "20120610", "", 5000},
            {1254195, "http://iib.com.ua/actionopen.asp?cid=114&act=636&lang=ua", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/pletenie_kosichek_foto_urok_po_pleteniu_koloska", "20120530", "20120610", "", 5000},
            {619515, "http://fstrf.ru/", "20120530", "20120610", "", 5000},
            {1007905, "http://audiocoding.ru/%D1%81%D1%82%D0%B0%D1%82%D1%8C%D0%B8/%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D0%B0-wav-%D1%84%D0%B0%D0%B9%D0%BB%D0%B0.html", "20120530", "20120610", "", 5000},
            {1350495, "http://kp40.ru/index.php?cid=600&nid=642491", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/desyatka_samih_umnih_sokak/", "20120530", "20120610", "", 5000},
            {858555, "http://mironclock.ru/catalog.php?id=53&id1=1472", "20120530", "20120610", "", 5000},
            {1258435, "http://bgznk.ru/catalog/28-181688.html", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/node/18", "20120530", "20120610", "", 5000},
            {649405, "http://prochtu.ru/list.php", "20120530", "20120610", "", 5000},
            {949635, "http://paintball-for-all.ru/mask_dye.html", "20120530", "20120610", "", 5000},
            {1393625, "http://nogomatch.ru/foto/%D0%B4%D0%B5%D0%B2%D1%83%D1%88%D0%BA%D0%B8-%D1%81%D0%B8%D1%81%D1%8C%D0%BA%D0%B8-%D0%BD%D0%B0-%D1%84%D1%83%D1%82%D0%B1%D0%BE%D0%BB%D0%B5-%D1%81%D1%82%D0%B0%D0%B4%D0%B8%D0%BE%D0%BD%D0%B5-%D0%BF%D0%BE%D0%BB%D0%B5", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/fighting_dogs/", "20120530", "20120610", "", 5000},
            {763105, "http://xn--80aejynxxo3b.xn--p1ai/covers/toyota/corolla.html", "20120530", "20120610", "", 5000},
            {1350495, "http://kp40.ru/index.php?cid=600&nid=642650", "20120530", "20120610", "", 5000},
            {716925, "http://visherasemena.ru/2009-03-11-14-26-58", "20120530", "20120610", "", 5000},
            {1402105, "http://nmsk.dp.ua/", "20120530", "20120610", "", 5000},
            {529555, "http://volleymsk.ru/forum/", "20120530", "20120610", "", 5000},
            {502715, "http://shatura-mebel.com/goods/sofa", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/gadzhety/audio/", "20120530", "20120610", "", 5000},
            {1246435, "http://tiptip.ru/plov.php", "20120530", "20120610", "", 5000},
            {1089855, "http://zagran-passport.ru/bio.php", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/photoalbum/albums/7", "20120530", "20120610", "", 5000},
            {1394195, "http://detkiuch.ru/stuff/igry_dlja_detej/detskie_obuchajushhie/6", "20120530", "20120610", "", 5000},
            {1361095, "http://arbist.ru/catalog/plitka_premium/?IBLOCK_CODE=plitka_premium&arrFilter_ff[SECTION_ID]=&arrFilter_pf[COUNTRY]=&arrFilter_pf[SIZE]=&arrFilter_pf[COLOR]=7684%2C11019%2C11613%2C6962%2C6951%2C6961&arrFilter_pf[APPLICATION]=&arrFilter_pf[BRAND_GUID]=&arrFilter_pf[DESTINATION]=&arrFilter_pf[MATERIAL]=&arrFilter_pf[SURFPROC]=&arrFilter_pf[IMGTYPE]=&arrFilter_cf%5B10%5D[LEFT]=0&arrFilter_cf%5B10%5D[RIGHT]=1500&set_filter=%D4%E8", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/node/24", "20120530", "20120610", "", 5000},
            {788235, "http://dom.ya1.ru/index.php?newsid=2297", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-vechernie-platya-c-10_107?sort=3b&page=2", "20120530", "20120610", "", 5000},
            {652875, "http://restoranam.net/recipe-1303-lukovie-koltsa/", "20120530", "20120610", "", 5000},
            {1029745, "http://atrix63.ru/produkciia.php", "20120530", "20120610", "", 5000},
            {1128625, "http://domostroymedia.ru/obj_list/type1/105493/", "20120530", "20120610", "", 5000},
            {1157505, "http://cinemaniashop.ru/chemodani/siutsasesadult/britto/b702-3028-976/", "20120530", "20120610", "", 5000},
            {1361285, "http://my-strongdc.ru/%D1%81%D0%BA%D0%B0%D1%87%D0%B0%D1%82%D1%8C-%D0%B1%D0%B5%D1%81%D0%BF%D0%BB%D0%B0%D1%82%D0%BD%D0%BE-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-strongdc-%D1%81%D1%82%D1%80%D0%BE%D0%BD%D0%B3-%D0%B4%D1%81/", "20120530", "20120610", "", 5000},
            {1334485, "http://mir-vann.ru/catalog/26/", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/5807-rm-78.36.001-99-spravochnik-inzhenerno-tehnicheskih-rabotnikov-i-elektromonterov-tehnicheskih-sredstv-ohranno-pozharnoy-signalizacii.html", "20120530", "20120610", "", 5000},
            {1253415, "http://svarog-spb.ru/contacts/", "20120530", "20120610", "", 5000},
            {733775, "http://giftbasket.ru/catalog/picnic/section.php?SECTION_ID=1778", "20120530", "20120610", "", 5000},
            {1015385, "http://pro-goszakaz.ru/regulations/50079/", "20120530", "20120610", "", 5000},
            {1157615, "http://dgr.ru/psychology/otvety/19", "20120530", "20120610", "", 5000},
            {777005, "http://bymobile.ru/cat/kozhanye_chekhly_dlja_iphone_4/", "20120530", "20120610", "", 5000},
            {1246435, "http://tiptip.ru/recept-shurpa.php", "20120530", "20120610", "", 5000},
            {780805, "http://horoshevo-mnevniki.ru/", "20120530", "20120610", "", 5000},
            {749595, "http://zakazanchik.ru/index.php?categoryID=91", "20120530", "20120610", "", 5000},
            {529555, "http://volleymsk.ru/main/finali_chetireh_sezona_2011-2012_otchet/", "20120530", "20120610", "", 5000},
            {571985, "http://cyberclinika.com/diagnostic/diagnostic-mrt.html", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-vechernie-platya-c-10_107?sort=3b&page=4", "20120530", "20120610", "", 5000},
            {792985, "http://irso.ru/", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/index.php?option=com_virtuemart&page=shop.browse&category_id=42&Itemid=2", "20120530", "20120610", "", 5000},
            {792715, "http://metro-photo.ru/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/kokteilnye-platya-bolshih-razmerov-c-130", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/hardest_dog/", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/biggest_dog/", "20120530", "20120610", "", 5000},
            {1280275, "http://tranio.ru/search/3c682a84b7b59ef75e13d9fc371c1a68f35b1c6c/", "20120530", "20120610", "", 5000},
            {1003925, "http://best-of-moto.ru/index.php?categoryID=1323", "20120530", "20120610", "", 5000},
            {937355, "http://chebhotel.ru/rus/nomera.html", "20120530", "20120610", "", 5000},
            {724005, "http://avtobukvar.ru/servise/podbor_salnikov_po_razmeram.html", "20120530", "20120610", "", 5000},
            {502715, "http://shatura-mebel.com/goods/Stulya-derevyannye", "20120530", "20120610", "", 5000},
            {782585, "http://nym-nym.msk.ru/ukrachenia-blyd/2720-ukrashenie-blyud-vse.html", "20120530", "20120610", "", 5000},
            {832065, "http://miraero.com.ua/tseni", "20120530", "20120610", "", 5000},
            {520455, "http://a-centre.ru/imgwork.php", "20120530", "20120610", "", 5000},
            {1281945, "http://fitnesstrener.ru/", "20120530", "20120610", "", 5000},
            {949635, "http://paintball-for-all.ru/feeders_main.html", "20120530", "20120610", "", 5000},
            {582765, "http://infanty.ru/category/tekstil/komplekty-dlya-krovatok?view=all", "20120530", "20120610", "", 5000},
            {1221985, "http://smart76.ru/prodazha-avtostekla/128/", "20120530", "20120610", "", 5000},
            {1157615, "http://dgr.ru/psychology/otvety/1", "20120530", "20120610", "", 5000},
            {1286615, "http://blesna.net/voblery_na_schuku.html", "20120530", "20120610", "", 5000},
            {1225635, "http://dentastom.com/", "20120530", "20120610", "", 5000},
            {756865, "http://loveinacity.ru/love/pervyj-seks-kak-podgotovitsya-k-takomu-sobytiyu-zhenshhine.html", "20120530", "20120610", "", 5000},
            {1015385, "http://pro-goszakaz.ru/practice/68682/", "20120530", "20120610", "", 5000},
            {1280275, "http://tranio.ru/search/", "20120530", "20120610", "", 5000},
            {1253415, "http://svarog-spb.ru/service/", "20120530", "20120610", "", 5000},
            {1147785, "http://yangross.ru/", "20120530", "20120610", "", 5000},
            {777005, "http://bymobile.ru/cat/koghaniy_chehol_dlya_ipad_2/", "20120530", "20120610", "", 5000},
            {1258435, "http://bgznk.ru/", "20120530", "20120610", "", 5000},
            {1310205, "http://ecookna.ru/products/rollet/", "20120530", "20120610", "", 5000},
            {516565, "http://vpletaysya.ru/main/page/photo_less_1", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/holland", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/index.php?option=com_virtuemart&category_id=53&page=shop.browse&Itemid=2&limit=21&limitstart=168", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/2040-normativy-chislennosti-rabochih-kotelnyh-ustanovok-i-teplovyh-setey.html", "20120530", "20120610", "", 5000},
            {571985, "http://cyberclinika.com/", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/samie_glupie_sobaki/", "20120530", "20120610", "", 5000},
            {582765, "http://infanty.ru/category/toys/razvivayushhie-igrushki-do-goda-pogremushki?view=all", "20120530", "20120610", "", 5000},
            {1015125, "http://otb.by/articles/3/1543-organizatsiya-raboty-po-ohrane-truda", "20120530", "20120610", "", 5000},
            {1279775, "http://za-matrasom.ru/akcii/", "20120530", "20120610", "", 5000},
            {983505, "http://autotovar.by/zapchasti-dlia-opel-astra_f-09.1991_09.1998-kupit", "20120530", "20120610", "", 5000},
            {1387595, "http://sotca.info/zabory/", "20120530", "20120610", "", 5000},
            {738665, "http://luxclimat.ru/kond_kvartiri.php", "20120530", "20120610", "", 5000},
            {1003925, "http://best-of-moto.ru/index.php?categoryID=1295", "20120530", "20120610", "", 5000},
            {722185, "http://read.ru/cabinet/#deferred", "20120530", "20120610", "", 5000},
            {1380305, "http://kattrys.ru/node/6202", "20120530", "20120610", "", 5000},
            {859365, "http://skylink.ms/", "20120530", "20120610", "", 5000},
            {1003925, "http://best-of-moto.ru/index.php?categoryID=1382&category_slug=elektroskutery-i-elektrovelosipedy", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/iso/01_gosty/01080_gost_iso/0108030_gost_iso/1355-gost-2.304-81-eskd.-shrifty-chertezhnye.html", "20120530", "20120610", "", 5000},
            {1201555, "http://furgon-center.ru/cgi-bin/main.cgi?what=contact", "20120530", "20120610", "", 5000},
            {1016845, "http://sfort.ru/flats/three-rooms.html", "20120530", "20120610", "", 5000},
            {1394195, "http://detkiuch.ru/index/obuch_mult/0-2", "20120530", "20120610", "", 5000},
            {621655, "http://gus-hrustal.ru/", "20120530", "20120610", "", 5000},
            {1201555, "http://furgon-center.ru/", "20120530", "20120610", "", 5000},
            {758105, "http://shop-online.kemp1.ru/search/", "20120530", "20120610", "", 5000},
            {912875, "http://yournail.ru/", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/sri-lanka", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-kokteilnye-platya-c-10_109?sort=3b&page=4", "20120530", "20120610", "", 5000},
            {912875, "http://yournail.ru/index/dizajn-nogtej/risunki-na-nogtjah-dlja-nachinajuwih.html", "20120530", "20120610", "", 5000},
            {1127925, "http://menobr.ru/materials/370/5822/", "20120530", "20120610", "", 5000},
            {758105, "http://shop-online.kemp1.ru/", "20120530", "20120610", "", 5000},
            {701695, "http://belhuntclub.net/forums/index.php/topic/2976-%D0%B1%D0%B8%D0%BB%D0%B5%D1%82%D1%8B-%D0%BD%D0%B0-%D1%81%D0%B4%D0%B0%D1%87%D1%83-%D0%BE%D1%85%D0%BE%D1%82%D0%BD%D0%B8%D1%87%D1%8C%D0%B5%D0%B3%D0%BE-%D1%8D%D0%BA%D0%B7%D0%B0%D0%BC%D0%B5%D0%BD%D0%B0/", "20120530", "20120610", "", 5000},
            {800455, "http://chertimvam.ru/lib/post/sopryazheniya/", "20120530", "20120610", "", 5000},
            {1157615, "http://dgr.ru/psychology/otvety/18", "20120530", "20120610", "", 5000},
            {1172785, "http://corporate.enchy.ru/ubki.html", "20120530", "20120610", "", 5000},
            {1170895, "http://vip-tv.ru/ustanovka-antenn.html", "20120530", "20120610", "", 5000},
            {1016845, "http://sfort.ru/flats/two-rooms.html", "20120530", "20120610", "", 5000},
            {910555, "http://video-mp4.ru/", "20120530", "20120610", "", 5000},
            {782585, "http://nym-nym.msk.ru/torty/", "20120530", "20120610", "", 5000},
            {1429975, "http://ds.b-alt.ru/?p=403", "20120530", "20120610", "", 5000},
            {991185, "http://insi.ru/edifice/opisanie/", "20120530", "20120610", "", 5000},
            {1286615, "http://blesna.net/lovlya_tolstoloba.html", "20120530", "20120610", "", 5000},
            {1163845, "http://charters.ru/go/bulgaria/bourgas/", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/svadebnye-platya-c-129", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-kokteilnye-platya-c-10_109?sort=3b&page=5", "20120530", "20120610", "", 5000},
            {717235, "http://puffy-shop.ru/content/13-strijka-sobak-gryming", "20120530", "20120610", "", 5000},
            {1157505, "http://cinemaniashop.ru/chemodani/", "20120530", "20120610", "", 5000},
            {1361285, "http://my-strongdc.ru/", "20120530", "20120610", "", 5000},
            {532075, "http://vodaservis.ru/service/bur/", "20120530", "20120610", "", 5000},
            {780805, "http://horoshevo-mnevniki.ru/social/pfrf/", "20120530", "20120610", "", 5000},
            {792715, "http://metro-photo.ru/img9312", "20120530", "20120610", "", 5000},
            {1138315, "http://ndvl.ru/sell/kvartira/213656", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/iso/13_gosty_iso/13220_gost_iso/1322001_gost_iso/5594-ppbo-85-pravila-pozharnoy-bezopasnosti-v-neftyanoy-promyshlennosti.html", "20120530", "20120610", "", 5000},
            {532075, "http://vodaservis.ru/", "20120530", "20120610", "", 5000},
            {669175, "http://neointerno.ru/catalog/stoly-zhurnalnye", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/balnye-platya-c-139", "20120530", "20120610", "", 5000},
            {724005, "http://avtobukvar.ru/servise/podbor_krestovin_po_razmeram.html", "20120530", "20120610", "", 5000},
            {1357095, "http://fotoshkola.net/mk/58-istoria_odnogo_fotografa/announce", "20120530", "20120610", "", 5000},
            {656995, "http://klybni4ka.net/platya-kokteilnye-platya-c-10_109?sort=3b&page=3", "20120530", "20120610", "", 5000},
            {1266555, "http://rukodelie-sama.ru/", "20120530", "20120610", "", 5000},
            {652875, "http://restoranam.net/recipe-1291-salat-s-kurinoy-grudkoy/", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/dom_i_interer/chasy/", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/britain", "20120530", "20120610", "", 5000},
            {1010525, "http://rapira.sp.ru/index.php/shops", "20120530", "20120610", "", 5000},
            {1089855, "http://zagran-passport.ru/documents.php", "20120530", "20120610", "", 5000},
            {1089855, "http://zagran-passport.ru/price.php", "20120530", "20120610", "", 5000},
            {763105, "http://xn--80aejynxxo3b.xn--p1ai/materials.html", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/holland/", "20120530", "20120610", "", 5000},
            {1279935, "http://nordhouse.ru/materials/kleenyi-brus-fin/", "20120530", "20120610", "", 5000},
            {1157505, "http://cinemaniashop.ru/chemodani/siutsasesadult/britto/b703-3028-988/", "20120530", "20120610", "", 5000},
            {802545, "http://neopoliscasa.ru/catalog/sovremenniy.html", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/index.php?option=com_content&view=article&id=146:-nokia&catid=1:akcii&Itemid=14", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/iso/01_gosty/01110_gost_iso/1678-gost-2.113-75-eskd.-gruppovye-i-bazovye-konstruktorskie-dokumenty.html", "20120530", "20120610", "", 5000},
            {666985, "http://domosedka.com/publ/zona_bikini_kak_udalit_volosy/26-1-0-475", "20120530", "20120610", "", 5000},
            {840625, "http://aquarium-artes.ru/cihlidy.html", "20120530", "20120610", "", 5000},
            {1316685, "http://vvv-bags.ru/deals.php?kod=9870025B-75C7-4ED0-B410-629C2211049D", "20120530", "20120610", "", 5000},
            {1003925, "http://best-of-moto.ru/index.php?categoryID=2054", "20120530", "20120610", "", 5000},
            {735415, "http://altair-kmv.narod.ru/ullu-tau_zagadochnaya_gora_-_gora_zdorovya_-_ozdorovitelnii_tur_vihodnogo_dnya_/", "20120530", "20120610", "", 5000},
            {1134155, "http://hotels72.com/", "20120530", "20120610", "", 5000},
            {1334485, "http://mir-vann.ru/catalog/996/", "20120530", "20120610", "", 5000},
            {855005, "http://tvoe-nebo.ru/photo1/photo1.html", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/index.php?option=com_virtuemart&page=shop.browse&category_id=39&Itemid=2", "20120530", "20120610", "", 5000},
            {1234475, "http://braintools.ru/thinking", "20120530", "20120610", "", 5000},
            {571985, "http://cyberclinika.com/on-line-consultation.html", "20120530", "20120610", "", 5000},
            {717235, "http://puffy-shop.ru/6-kombinezony-dlya-sobak", "20120530", "20120610", "", 5000},
            {985025, "http://uosetra.ru/page/2/", "20120530", "20120610", "", 5000},
            {788685, "http://noveltour.ru/places/novgorod/ostrov_seliger.html", "20120530", "20120610", "", 5000},
            {991185, "http://insi.ru/directions/bvz/", "20120530", "20120610", "", 5000},
            {656505, "http://dostavkakresel.ru/shop/CID_19.html", "20120530", "20120610", "", 5000},
            {738665, "http://luxclimat.ru/otzivy-reyting-kondicionerov.php", "20120530", "20120610", "", 5000},
            {733775, "http://giftbasket.ru/catalog/picnic/", "20120530", "20120610", "", 5000},
            {784555, "http://mebel-id.com/mebelsvoimirukami", "20120530", "20120610", "", 5000},
            {1336695, "http://mir-remonta.ru/p/ceny", "20120530", "20120610", "", 5000},
            {1346035, "http://talismanland.ru/prajs-list.html", "20120530", "20120610", "", 5000},
            {1386075, "http://lefutur.ru/catalog/dom_i_interer/dom/", "20120530", "20120610", "", 5000},
            {814055, "http://zzu.ru/obschie/zzu-prays-obschemash.html", "20120530", "20120610", "", 5000},
            {1132765, "http://portative.by/product/6718/catalog//32/7/1", "20120530", "20120610", "", 5000},
            {1005085, "http://novosibirsk.on-day.ru/", "20120530", "20120610", "", 5000},
            {1163845, "http://charters.ru/", "20120530", "20120610", "", 5000},
            {1201555, "http://furgon-center.ru/cgi-bin/main.cgi?what=prices+pricep", "20120530", "20120610", "", 5000},
            {979555, "http://all-games.ru/poker_rules", "20120530", "20120610", "", 5000},
            {1217835, "http://megapolus-tours.ru/tours/", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/spain1/", "20120530", "20120610", "", 5000},
            {640785, "http://ko-sushi.ru/catalog/?top_id=3", "20120530", "20120610", "", 5000},
            {784555, "http://mebel-id.com/chertezhi-mebeli", "20120530", "20120610", "", 5000},
            {917345, "http://invaprom.ru/cat.php?cat_id=31", "20120530", "20120610", "", 5000},
            {1263145, "http://telejet.ru/catalog/rubric/10/", "20120530", "20120610", "", 5000},
            {520455, "http://a-centre.ru/publs.php?subject=2", "20120530", "20120610", "", 5000},
            {1179995, "http://orengis.ru/afisha/", "20120530", "20120610", "", 5000},
            {862255, "http://prof-svet.ru/brands/slv/", "20120530", "20120610", "", 5000},
            {666855, "http://xbox360.nextgame.net/games/", "20120530", "20120610", "", 5000},
            {497685, "http://pardi.ru/index.php?categoryID=60&sort=name_in_stock&direction=DESC&show_all=yes", "20120530", "20120610", "", 5000},
            {812745, "http://maximum-honda.ru/cars/Honda-cr-v/?yd", "20120530", "20120610", "", 5000},
            {1127925, "http://menobr.ru/materials/370/5703/", "20120530", "20120610", "", 5000},
            {1223085, "http://portal-ug.ru/presentations/budget_01.php", "20120530", "20120610", "", 5000},
            {782585, "http://nym-nym.msk.ru/ukrachenia-blyd/page/2/", "20120530", "20120610", "", 5000},
            {1015385, "http://pro-goszakaz.ru/regulations/71231/", "20120530", "20120610", "", 5000},
            {949635, "http://paintball-for-all.ru/gas_air.html", "20120530", "20120610", "", 5000},
            {1258435, "http://bgznk.ru/catalog/26-7270.html", "20120530", "20120610", "", 5000},
            {1323155, "http://opengost.ru/iso/01_gosty/01110_gost_iso/1738-gost-3.1407-86-estd.-formy-i-trebovaniya-k-zapolneniyu-dokumentov-na-tehnologicheskie-processy-specializirovannye-po-metodam-sborki.html", "20120530", "20120610", "", 5000},
            {1274525, "http://ilimweb.ru/ust-ilimsk.html", "20120530", "20120610", "", 5000},
            {497685, "http://pardi.ru/index.php?categoryID=356&sort=name_in_stock&direction=DESC&show_all=yes", "20120530", "20120610", "", 5000},
            {1011595, "http://teplodar.ru/", "20120530", "20120610", "", 5000},
            {1129175, "http://redkassa.ru/events/51852-bilety_na_koncert_red_hot_chili_peppers/", "20120530", "20120610", "", 5000},
            {668035, "http://astronom.ru/", "20120530", "20120610", "", 5000},
            {1345175, "http://new-cian.ru/modules/showdb/rent_find.php", "20120530", "20120610", "", 5000},
            {1350495, "http://kp40.ru/", "20120530", "20120610", "", 5000},
            {657845, "http://amt-training.ru/content/kadry/36687/", "20120530", "20120610", "", 5000},
            {913925, "http://terradeck.ru/node/95", "20120530", "20120610", "", 5000},
            {522435, "http://solexauto.ru/sale.php", "20120530", "20120610", "", 5000},
            {562735, "http://away.oberweb.ru/thailand", "20120530", "20120610", "", 5000},
            {782585, "http://nym-nym.msk.ru/ukrachenia-blyd", "20120530", "20120610", "", 5000},
            {1343915, "http://klinkershop.ru/catalog/fasadnie-termopaneli/", "20120530", "20120610", "", 5000},
            {1234475, "http://braintools.ru/neuron-the-structure-of-nerve-cell", "20120530", "20120610", "", 5000},
            {1172785, "http://corporate.enchy.ru/jaket.html", "20120530", "20120610", "", 5000},
            {784555, "http://mebel-id.com/chertezhi-mebeli/2011-01-11-10-50-59", "20120530", "20120610", "", 5000},
            {1201555, "http://furgon-center.ru/cgi-bin/main.cgi?what=avto+foton", "20120530", "20120610", "", 5000},
            {595835, "http://bestgav.narod2.ru/desyatka_samih_redkih_sobak/", "20120530", "20120610", "", 5000},
            {1016845, "http://sfort.ru/stage/", "20120530", "20120610", "", 5000},
            {1015385, "http://pro-goszakaz.ru/regulations/15147/", "20120530", "20120610", "", 5000},
            {983505, "http://autotovar.by/zapchasti-dlia-peugeot-406-05.1999_05.2004-kupit", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/index.php?option=com_virtuemart&category_id=42&page=shop.browse&Itemid=2&limit=21&limitstart=126", "20120530", "20120610", "", 5000},
            {777005, "http://bymobile.ru/cat/plastikoviy_chehol_dlya_iphone_4_4s/", "20120530", "20120610", "", 5000},
            {497685, "http://pardi.ru/index.php?categoryID=90&sort=name_in_stock&direction=DESC&show_all=yes", "20120530", "20120610", "", 5000},
            {1388045, "http://cis.minsk.by/", "20120530", "20120610", "", 5000},
            {788235, "http://dom.ya1.ru/index.php?newsid=742", "20120530", "20120610", "", 5000},
            {1254195, "http://iib.com.ua/default.asp?lang=ru", "20120530", "20120610", "", 5000},
            {1043975, "http://afisha-ola.ru/?date=next", "20120530", "20120610", "", 5000},
            {991185, "http://insi.ru/edifice/konstr/", "20120530", "20120610", "", 5000},
            {777915, "http://netuning.ru/index.php?show_aux_page=7", "20120530", "20120610", "", 5000},
            {1234475, "http://braintools.ru/article/9300", "20120530", "20120610", "", 5000},
            {582765, "http://infanty.ru/category/tekstil/aksessuary", "20120530", "20120610", "", 5000},
            {1286615, "http://blesna.net/snast_dlya_lovli_tolstoloba.html", "20120530", "20120610", "", 5000},
            {497685, "http://pardi.ru/", "20120530", "20120610", "", 5000},
            {1387895, "http://prestige-express.ru/category/zhenskaja-obuv/all/", "20120530", "20120610", "", 5000},
            {782585, "http://nym-nym.msk.ru/ukrachenia-blyd/2253-ukrashenie-blyud-foto-podborka-45.html", "20120530", "20120610", "", 5000},
            {780805, "http://horoshevo-mnevniki.ru/construction/slum-clearance/", "20120530", "20120610", "", 5000},
            {1258435, "http://bgznk.ru/catalog/26-5065.html", "20120530", "20120610", "", 5000},
            {1263115, "http://terminal7.ru/index.php?option=com_virtuemart&category_id=42&page=shop.browse&Itemid=2&limit=21&limitstart=147", "20120530", "20120610", "", 5000},
            {668035, "http://astronom.ru/vcd-168/catalog.html", "20120530", "20120610", "", 5000},
            {1217835, "http://megapolus-tours.ru/tours/excursions/", "20120530", "20120610", "", 5000},
            {647325, "http://trkr.ru/article/full/1313149888.html", "20120530", "20120610", "", 5000},
            {1419555, "http://r-training.ru/", "20120530", "20120610", "", 5000},};


    private static String buildUrl(String requestUrl, Object... args) {
        StringBuilder ret = new StringBuilder(requestUrl);
        for (int i = 0; i < args.length; ++i) {
            if (i == 0) {
                ret.append('?');
            } else {
                ret.append('&');
            }
            ret.append(PARAM_NAMES[i]).append('=').append(args[i]);
        }
        return ret.toString();
    }

    private static String sendRequest(String url) {
        StringBuilder ret = new StringBuilder();
        try {
            URL u = new URL(url);
            URLConnection uc = u.openConnection();
            BufferedReader in = new BufferedReader(new InputStreamReader(uc.getInputStream()));
            String line;
            while ((line = in.readLine()) != null) {
                ret.append(line);
            }
            in.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return ret.toString();
    }

    private static void test(int iterations, int idx) {
        long mfsTime = 0;
        long oldTime = 0;
        long mfs2Time = 0;
        Timer timer = new Timer();
        for (int i = 0; i < iterations; ++i) {

            String url1 = URL + "/secure/scroll-map-data.json";
            url1 = buildUrl(url1, VALUES[idx]);
            timer.start();
            String ret1 = sendRequest(url1);
            mfsTime += timer.elapsedTime();
        }
        printTime(mfsTime, mfs2Time, oldTime, iterations);
    }

    private static void testMfs(TimePair time, int idx) {
        Timer timer = new Timer();
        time.requests++;

        String url1 = URL + "/secure/scroll-map-data.json";
        url1 = buildUrl(url1, VALUES_2[idx]);
        timer.start();
        String ret1 = sendRequest(url1);
        time.addMfs(timer.elapsedTime());
    }

    @Test
    public void test10And0() {
        test(10, 0);
    }

    @Test
    public void test10And1() {
        test(10, 1);
    }

    @Test
    public void test10And2() {
        test(10, 2);
    }

    @Test
    public void test10And3() {
        test(10, 3);
    }

    @Test
    public void test10And4() {
        test(10, 4);
    }

    @Test
    public void test10And5() {
        test(10, 5);
    }

    @Test
    public void test10And6() {
        test(10, 6);
    }

    @Test
    public void test10And7() {
        test(10, 7);
    }

    @Test
    public void test10And8() {
        test(10, 8);
    }

    @Test
    public void test10And9() {
        test(10, 9);
    }

    @Test
    public void test10And10() {
        test(10, 10);
    }

    @Test
    public void test10And11() {
        test(10, 11);
    }

    @Test
    public void test1And12() {
        test(1, 12);
    }

    @Test
    public void largeTest() {
        TimePair time = new TimePair();
        System.out.println(VALUES_2.length);
        for (int i = 0; i < VALUES_2.length; ++i) {
            testMfs(time, i);
        }
        printTimeMFS(time);
    }

    private static void printTime(long mfsTime, long mfs2Time, long oldTime, int requests) {
        System.out.println("requests count=" + requests);
        System.out.println("mfsTime:");
        System.out.println("total=" + mfsTime + " per request=" + (mfsTime / requests));

        System.out.println("mfsTime2:");
        System.out.println("total=" + mfs2Time + " per request=" + (mfs2Time / requests));

        System.out.println("oldTime:");
        System.out.println("total=" + oldTime + " per request=" + (oldTime / requests));
    }

    private static void printTimeMFS(TimePair time) {
        System.out.println("requests count=" + time.requests);
        System.out.println("mfsTime:");
        System.out.println("total=" + time.mfs + " per request=" + (time.mfs / time.requests));
        System.out.printf("max = %d, min = %d\n", time.mfsMax, time.mfsMin);
        //System.out.println(time.mfsHistogram.toString());

        System.out.println("mfsTime2:");
        System.out.println("total=" + time.mfs2 + " per request=" + (time.mfs2 / time.requests));
        System.out.printf("max = %d, min = %d\n", time.mfs2Max, time.mfs2Min);
        //stem.out.println(time.mfs2Histogram.toString());
    }

    private static final class Timer {

        private long time = 0;

        private void start() {
            time = System.currentTimeMillis();
        }

        private long elapsedTime() {
            return System.currentTimeMillis() - time;
        }
    }

    private static final class TimePair {
        private long mfs;
        private long mfs2;

        private long mfsMax = Long.MIN_VALUE;
        private long mfsMin = Long.MAX_VALUE;
        private long mfs2Max = Long.MIN_VALUE;
        private long mfs2Min = Long.MAX_VALUE;
        //private final Histogram mfsHistogram = new Histogram(0, 1000, 100);
        //private final Histogram mfs2Histogram = new Histogram(0, 1000, 100);

        private int requests;

        public void addMfs(long time) {
            mfs += time;
            mfsMax = Math.max(mfsMax, time);
            mfsMin = Math.min(mfsMin, time);
            //mfsHistogram.add(time);
        }

        public void addMf2(long time) {
            mfs2 += time;
            mfs2Max = Math.max(mfs2Max, time);
            mfs2Min = Math.min(mfs2Min, time);
            //mfs2Histogram.add(time);
        }
    }
}
