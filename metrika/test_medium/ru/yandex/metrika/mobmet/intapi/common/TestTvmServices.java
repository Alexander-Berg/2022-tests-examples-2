package ru.yandex.metrika.mobmet.intapi.common;

import java.util.List;

import org.springframework.http.HttpHeaders;

import ru.yandex.metrika.tvm2.TestTvmHolder;
import ru.yandex.metrika.tvm2.TvmSettings;

/**
 * https://clubs.at.yandex-team.ru/passport/3040
 * Судя по этушке и примерам в аркадии это нормально сохранять секреты здесь, главное чтобы они были
 * получены с помощью опции unittest (например ya tool tmvknife unittest service --src 1000502 --dst 1000501)
 * dst=1000501 src=значение из enum. для запросов в mobmet-intapi
 * dst=значение из enum src=1000501. для запросов из mobmet-intapi во внешние демоны
 * Секреты тут https://a.yandex-team.ru/arc_vcs/library/recipes/tvmapi/clients/clients.json
 */
public enum TestTvmServices {
    SELF(1000501, "bAicxJVa5uVY7MjDlapthw", "3:serv:CBAQ__________9_IggItYg9ELWIPQ:KPDmIq2nnqHlAMwZ4kleJ7tiwxqUq_ik" +
            "AVWUoucsbaDdv7JL1BIRe0Jqeq1jqGBmBQWKae1XkrLjjncK--xBUgBTBjaJly1l78HzqFsRFYYapL3WhK53Rz077zFZJu3rfKrNYL" +
            "oSelOdUYdNN_GJ9XGTnlesXjXrdGPtgrfXGc8"),
    DIRECT_FRONTEND(1000502, "e5kL0vM3nP-nPf-388Hi6Q", "3:serv:CBAQ__________9_IggItog9ELWIPQ:HpqauXpXkd6gPQgAEVAsv" +
            "yQu2rOd6HL3vCGNYz8bIQRzkRuZ81S0eNt9NNL0shiQ-TThiBKV6kjwYT8616pB0I7bAOf2rRGOJ4ZMnaEyqjc5sjzzmvQN5x5UNAg" +
            "bYL7MVFeLP0yF_pku-3kSu-GatqT32BDqbaVDk_hHhDLCUMM"),
    IDM(1000503, "S3TyTYVqjlbsflVEwxj33w", "3:serv:CBAQ__________9_IggIt4g9ELWIPQ:ObFFC5fFKGaBxMzk5YaiomQMFJ5jp9QGA" +
            "oYoIkKY3dXL0h1a_OvWAk7HzTINyLXKgwR1DsxAFWRyBcPifmi_5G2h9mArrdEmovIbkdPERzYCTlubuFS4X3yiOoMb5OOdnPX2eeX" +
            "_XU3mW9Sp-VK95gcpOVhQ4UcYQsSwwet65_0"),
    TAKEOUT(1000504, "CJua5YZXEPuVLgJDquPOTA", "3:serv:CBAQ__________9_IggIuIg9ELWIPQ:AdLH9Y4Zs79lHCziF6KyT1R0Gzzjb" +
            "OE-g1E60hRLOWh_Ykz3nrW1uQIWFBApfPLg3O0lClsT41tEeXAocxGp6ipLrSz1HFkVbicT3zPI9PC8LhVQzMvMrbuZ5EsBknHlyLJ" +
            "7RJKlQilIehPCRAtrnxZ0GXL53TQgLLzhOMhBhas"),
    PASSPORT_FRONTEND(1000505, "z5oaXOjgB5nV5gycBpzZ-A", "3:serv:CBAQ__________9_IggIuYg9ELWIPQ:NlxhH10girf4pVerr7gr" +
            "GHVtkSjtDDmVIaXIxd18GYdE_xhOZvlBdpl5lwU3PYJds4qcHz9ZUaWLS1_1SMGWrJBKbb9_nfsReBO_qqXvsotPhxJ_fn03PqyckO" +
            "Sj2IGD3rIiEIxMHLk-psoSztc_f62Y1M8085NL1TtnUAHvA0s");
    /**
     * id в рецепте tvm, берутся из
     * https://a.yandex-team.ru/arc/trunk/arcadia/library/recipes/tvmapi/clients/clients.json
     */
    private final long clientId;
    /**
     * Секрет для clientId
     */
    private final String secret;
    /**
     * Секрет для хождения в self
     */
    private final String serviceTicket;

    TestTvmServices(long clientId, String secret, String serviceTicket) {
        this.clientId = clientId;
        this.secret = secret;
        this.serviceTicket = serviceTicket;
    }

    public long getClientId() {
        return clientId;
    }

    public String getSecret() {
        return secret;
    }

    public String getServiceTicket() {
        return serviceTicket;
    }

    public HttpHeaders getServiceHeaders() {
        var headers = new HttpHeaders();
        headers.put(TvmSettings.SERVICE_HEADER, List.of(serviceTicket));
        return headers;
    }

    public HttpHeaders getUserHeaders(long uid) {
        var headers = new HttpHeaders();
        headers.put(TvmSettings.SERVICE_HEADER, List.of(serviceTicket));
        headers.put(TvmSettings.USER_HEADER, List.of(TestTvmHolder.makeFakeUserTicket(uid)));
        return headers;
    }
}
