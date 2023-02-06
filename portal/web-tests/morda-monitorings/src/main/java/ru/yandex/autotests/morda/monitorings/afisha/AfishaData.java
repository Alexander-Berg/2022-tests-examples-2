package ru.yandex.autotests.morda.monitorings.afisha;

import ru.yandex.autotests.utils.morda.region.Region;

import java.util.Arrays;
import java.util.List;

import static ru.yandex.autotests.utils.morda.region.Region.ABAKAN;
import static ru.yandex.autotests.utils.morda.region.Region.AKTAU;
import static ru.yandex.autotests.utils.morda.region.Region.AKTOBE;
import static ru.yandex.autotests.utils.morda.region.Region.ALMATY;
import static ru.yandex.autotests.utils.morda.region.Region.ANGARSK;
import static ru.yandex.autotests.utils.morda.region.Region.ARHANGELSK;
import static ru.yandex.autotests.utils.morda.region.Region.ARMAVIR;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.ASTRAHAN;
import static ru.yandex.autotests.utils.morda.region.Region.ATYRAU;
import static ru.yandex.autotests.utils.morda.region.Region.BARNAUL;
import static ru.yandex.autotests.utils.morda.region.Region.BELAYA_CERKOV;
import static ru.yandex.autotests.utils.morda.region.Region.BELGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.BIYSK;
import static ru.yandex.autotests.utils.morda.region.Region.BLAGOVESHENSK;
import static ru.yandex.autotests.utils.morda.region.Region.BRATSK;
import static ru.yandex.autotests.utils.morda.region.Region.BREST;
import static ru.yandex.autotests.utils.morda.region.Region.BRYANSK;
import static ru.yandex.autotests.utils.morda.region.Region.CHEBOKSARI;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.CHEREPOVEC;
import static ru.yandex.autotests.utils.morda.region.Region.CHERKASSY;
import static ru.yandex.autotests.utils.morda.region.Region.CHERNIGOV;
import static ru.yandex.autotests.utils.morda.region.Region.CHERNOVCY;
import static ru.yandex.autotests.utils.morda.region.Region.CHITA;
import static ru.yandex.autotests.utils.morda.region.Region.DNEPROPETROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.DZERZHINSK;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.GOMEL;
import static ru.yandex.autotests.utils.morda.region.Region.GRODNO;
import static ru.yandex.autotests.utils.morda.region.Region.GROZNYY;
import static ru.yandex.autotests.utils.morda.region.Region.HABAROVSK;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.HERSON;
import static ru.yandex.autotests.utils.morda.region.Region.HMELNITSKIY;
import static ru.yandex.autotests.utils.morda.region.Region.IRKUTSK;
import static ru.yandex.autotests.utils.morda.region.Region.IVANOVO;
import static ru.yandex.autotests.utils.morda.region.Region.IVANO_FRANKOVSK;
import static ru.yandex.autotests.utils.morda.region.Region.IZHEVSK;
import static ru.yandex.autotests.utils.morda.region.Region.KALININGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.KALUGA;
import static ru.yandex.autotests.utils.morda.region.Region.KAMENSK_URALSKIY;
import static ru.yandex.autotests.utils.morda.region.Region.KARAGANDA;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KEMEROVO;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.KIROV;
import static ru.yandex.autotests.utils.morda.region.Region.KIROVOGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.KOSTANAY;
import static ru.yandex.autotests.utils.morda.region.Region.KOSTROMA;
import static ru.yandex.autotests.utils.morda.region.Region.KRASNODAR;
import static ru.yandex.autotests.utils.morda.region.Region.KRASNOYARSK;
import static ru.yandex.autotests.utils.morda.region.Region.KREMENCHUG;
import static ru.yandex.autotests.utils.morda.region.Region.KRIVOY_ROG;
import static ru.yandex.autotests.utils.morda.region.Region.KURSK;
import static ru.yandex.autotests.utils.morda.region.Region.LIPECK;
import static ru.yandex.autotests.utils.morda.region.Region.LUCK;
import static ru.yandex.autotests.utils.morda.region.Region.LVOV;
import static ru.yandex.autotests.utils.morda.region.Region.MAGNITOGORSK;
import static ru.yandex.autotests.utils.morda.region.Region.MAHACHKALA;
import static ru.yandex.autotests.utils.morda.region.Region.MARIUPOL;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOGILYOV;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.MURMANSK;
import static ru.yandex.autotests.utils.morda.region.Region.NABEREZHNIE_CHELNY;
import static ru.yandex.autotests.utils.morda.region.Region.NIKOLAEV;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_TAGIL;
import static ru.yandex.autotests.utils.morda.region.Region.NIZNEVARTOVSK;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOKUZNECK;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOROSSIYSK;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.ODESSA;
import static ru.yandex.autotests.utils.morda.region.Region.OMSK;
import static ru.yandex.autotests.utils.morda.region.Region.OREL;
import static ru.yandex.autotests.utils.morda.region.Region.ORENBURG;
import static ru.yandex.autotests.utils.morda.region.Region.ORSK;
import static ru.yandex.autotests.utils.morda.region.Region.PAVLODAR;
import static ru.yandex.autotests.utils.morda.region.Region.PENZA;
import static ru.yandex.autotests.utils.morda.region.Region.PERM;
import static ru.yandex.autotests.utils.morda.region.Region.PETROPAVLOVSK_KAMCHATSKIY;
import static ru.yandex.autotests.utils.morda.region.Region.PETROZAVODSK;
import static ru.yandex.autotests.utils.morda.region.Region.POLTAVA;
import static ru.yandex.autotests.utils.morda.region.Region.PROKOPIEVSK;
import static ru.yandex.autotests.utils.morda.region.Region.PSKOV;
import static ru.yandex.autotests.utils.morda.region.Region.PYATIGORSK;
import static ru.yandex.autotests.utils.morda.region.Region.ROSTOV_NA_DONU;
import static ru.yandex.autotests.utils.morda.region.Region.ROVNO;
import static ru.yandex.autotests.utils.morda.region.Region.RYAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.SARANSK;
import static ru.yandex.autotests.utils.morda.region.Region.SARATOV;
import static ru.yandex.autotests.utils.morda.region.Region.SEVASTOPOL;
import static ru.yandex.autotests.utils.morda.region.Region.SHAHTI;
import static ru.yandex.autotests.utils.morda.region.Region.SHYMKENT;
import static ru.yandex.autotests.utils.morda.region.Region.SIMFEROPOL;
import static ru.yandex.autotests.utils.morda.region.Region.SMOLENSK;
import static ru.yandex.autotests.utils.morda.region.Region.SOCHI;
import static ru.yandex.autotests.utils.morda.region.Region.STARYY_OSKOL;
import static ru.yandex.autotests.utils.morda.region.Region.STAVROPOL;
import static ru.yandex.autotests.utils.morda.region.Region.STERLITAMAK;
import static ru.yandex.autotests.utils.morda.region.Region.SUMI;
import static ru.yandex.autotests.utils.morda.region.Region.SURGUT;
import static ru.yandex.autotests.utils.morda.region.Region.SYKTYVKAR;
import static ru.yandex.autotests.utils.morda.region.Region.TAGANROG;
import static ru.yandex.autotests.utils.morda.region.Region.TAMBOV;
import static ru.yandex.autotests.utils.morda.region.Region.TERNOPOL;
import static ru.yandex.autotests.utils.morda.region.Region.TOLYATTI;
import static ru.yandex.autotests.utils.morda.region.Region.TOMSK;
import static ru.yandex.autotests.utils.morda.region.Region.TULA;
import static ru.yandex.autotests.utils.morda.region.Region.TUMEN;
import static ru.yandex.autotests.utils.morda.region.Region.TVER;
import static ru.yandex.autotests.utils.morda.region.Region.UFA;
import static ru.yandex.autotests.utils.morda.region.Region.ULAN_UDE;
import static ru.yandex.autotests.utils.morda.region.Region.ULYANOVSK;
import static ru.yandex.autotests.utils.morda.region.Region.URALSK;
import static ru.yandex.autotests.utils.morda.region.Region.UZHGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.VELIKIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.VINNICA;
import static ru.yandex.autotests.utils.morda.region.Region.VITEBSK;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIMIR;
import static ru.yandex.autotests.utils.morda.region.Region.VLADIVOSTOK;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.VOLOGDA;
import static ru.yandex.autotests.utils.morda.region.Region.VOLZSKIY;
import static ru.yandex.autotests.utils.morda.region.Region.VORONEZH;
import static ru.yandex.autotests.utils.morda.region.Region.YALTA;
import static ru.yandex.autotests.utils.morda.region.Region.YAROSLAVL;
import static ru.yandex.autotests.utils.morda.region.Region.YOSHKAR_OLA;
import static ru.yandex.autotests.utils.morda.region.Region.YUZHNO_SAHALINSK;
import static ru.yandex.autotests.utils.morda.region.Region.ZAPOROZHE;
import static ru.yandex.autotests.utils.morda.region.Region.ZELENOGRAD;
import static ru.yandex.autotests.utils.morda.region.Region.ZHITOMIR;

/**
 * User: ivannik
 * Date: 19.09.2014
 */
public class AfishaData {

    public static final List<Region> AFISHA_REGIONS_BIG = Arrays.asList(
            MOSCOW, SANKT_PETERBURG, KRIVOY_ROG, BELAYA_CERKOV, IVANOVO, YAROSLAVL, MURMANSK, PETROZAVODSK,
            VOLGOGRAD, KRASNODAR, ROSTOV_NA_DONU, STAVROPOL, NIZHNIY_NOVGOROD, UFA, KAZAN, SAMARA, EKATERINBURG,
            CHELYABINSK, IRKUTSK, NOVOSIBIRSK, SIMFEROPOL, LVOV, IVANO_FRANKOVSK,  DNEPROPETROVSK,
            HARKOV, ZAPOROZHE, ODESSA, NIKOLAEV, KIEV, VINNICA, CHERKASSY, ZHITOMIR, POLTAVA, CHERNIGOV, SOCHI,
            CHERNOVCY, ASTANA, ALMATY, KARAGANDA, MOGILYOV, MINSK, GOMEL, BREST, VITEBSK, BELGOROD, GRODNO,
            IZHEVSK, KRASNOYARSK, MARIUPOL, PERM, PAVLODAR, SEVASTOPOL, SARATOV, VORONEZH, YALTA,
            TOLYATTI, TAMBOV, LIPECK, KEMEROVO, CHEREPOVEC, KALUGA, KALININGRAD, KOSTANAY, KURSK,
            ARHANGELSK, BARNAUL, NOVOKUZNECK, AKTOBE, SHYMKENT, VLADIVOSTOK, VOLZSKIY, DZERZHINSK, KIROV,
            NIZNEVARTOVSK, SURGUT, TERNOPOL, LUCK, ROVNO, HMELNITSKIY, STARYY_OSKOL, NIZHNIY_TAGIL, BRYANSK,
            CHITA, YOSHKAR_OLA, OMSK, STERLITAMAK, BRATSK, ULAN_UDE, KOSTROMA, PETROPAVLOVSK_KAMCHATSKIY,
            ARMAVIR, TAGANROG, SHAHTI, BIYSK, VELIKIY_NOVGOROD, ZELENOGRAD, MAHACHKALA, NABEREZHNIE_CHELNY,
            PENZA, PROKOPIEVSK, PSKOV, SARANSK, TOMSK, TUMEN, HABAROVSK, ANGARSK, OREL, SMOLENSK, SYKTYVKAR,
            TVER, ULYANOVSK, BLAGOVESHENSK, ORENBURG, TULA, AKTAU, ATYRAU, URALSK,
            VLADIMIR, KAMENSK_URALSKIY, ORSK, NOVOROSSIYSK, YUZHNO_SAHALINSK,
            KIROVOGRAD, KREMENCHUG, SUMI, UZHGOROD, HERSON, ASTRAHAN, ABAKAN, GROZNYY, MAGNITOGORSK,
            RYAZAN, VOLOGDA, CHEBOKSARI, PYATIGORSK
            // https://st.yandex-team.ru/TESTHOME-86#1433146216000
            // DONECK, LUGANSK, KURGAN, MAIKOP, VLADIKAVKAZ, TALDYKORGAN, TEMIRTAU, SCHUCHINSK, NALCHIK, PETROPAVLOVSK
    );
}
