package ru.yandex.autotests.morda.utils.cookie;


import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.TimeUnit;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/04/15
 */
public abstract class MordaCookieUtils<T> implements CookieUtils<T> {

    public static final String MY = "my";
    public static final String SESSION_ID = "Session_id";
    public static final String YANDEXUID = "yandexuid";
    public static final String YANDEX_LOGIN= "yandex_login";
    public static final String FUID_01 = "fuid01";
    public static final String T = "t";
    public static final String YP = "yp";
    public static final String YS = "ys";
    public static final String YANDEX_GID = "yandex_gid";
    public static final String YANDEX_BROWSER_FOOTBALL = "yandex-browser-football";

    public static String getUid(String sessionId) {
        String[] cut = sessionId.split("\\.");
        if (cut.length < 4) {
            throw new IllegalStateException("Cookie 'Session_id' has incorrect format: " + sessionId);
        }
        if (sessionId.startsWith("2")) {
            String uid = cut[3];
            if (uid.startsWith("*")) {
                uid = uid.substring(1);
            }
            return uid;
        } else if (sessionId.startsWith("3")) {
            return cut[4].substring(2);
        }
        throw new RuntimeException("Failed to parse Session_id cookie to get uid");
    }

    public static String md5(String data) {
        String hexString;
        try {
            MessageDigest md = MessageDigest.getInstance("md5");
            md.update(data.getBytes("UTF-8"));
            byte[] hash = md.digest();
            hexString = getHexString(hash);
        } catch (NoSuchAlgorithmException ex) {
            return "";
        } catch (UnsupportedEncodingException e) {
            return "";
        }
        return hexString;
    }

    public static String getHexString(byte[] hash) {
        StringBuilder hexString = new StringBuilder();
        for (byte symbol : hash) {
            String tmp = (Integer.toHexString(0xFF & symbol));
            if (tmp.length() == 1) {
                hexString.append("0");
            }
            hexString.append(tmp);
        }
        return hexString.toString();
    }

    public static String getAuthSecretKey(String sessionId) {
        long days = TimeUnit.MILLISECONDS.toDays(System.currentTimeMillis());
        if (sessionId == null) {
            throw new RuntimeException("session_id must not be null");
        }
        return "u" + md5(getUid(sessionId) + "::" + days);
    }

    public static String getUnauthSecretKey(String yandexUid) {
        long days = TimeUnit.MILLISECONDS.toDays(System.currentTimeMillis());
        if (yandexUid == null) {
            throw new RuntimeException("yandexuid must not be null");
        }
        return "y" + md5("0:" + yandexUid + ":" + days);
    }

    public String getSecretKey(String domain) {
        return isLogged(domain)
                ? getAuthSecretKey(getCookieValue(getCookieNamed(SESSION_ID, domain)))
                : getUnauthSecretKey(getCookieValue(getCookieNamed(YANDEXUID, domain)));
    }

    public boolean isLogged(String domain) {
        String sessionId = getCookieValue(getCookieNamed(SESSION_ID, domain));
        return sessionId != null && !sessionId.startsWith("noauth");
    }

}
