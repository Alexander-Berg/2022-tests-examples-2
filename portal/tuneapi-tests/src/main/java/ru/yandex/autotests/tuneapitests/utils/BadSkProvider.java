package ru.yandex.autotests.tuneapitests.utils;

import ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory;

import javax.ws.rs.client.Client;
import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.TimeUnit;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22/01/15
 */
public class BadSkProvider {
    public static String empty() {
        return "";
    }

    public static String nullSk() {
        return null;
    }

    public static String random(Domain domain, Client client) {
        return CookieUtilsFactory.cookieUtils(client).isLogged(domain.getCookieDomain()) ? "u" + md5(String.valueOf(System.currentTimeMillis()))
                : "y" + md5(String.valueOf(System.currentTimeMillis()));
    }

    public static String unauth(Domain domain, Client client) {
        long days = TimeUnit.MILLISECONDS.toDays(System.currentTimeMillis());
        String yandexUid = CookieUtilsFactory.cookieUtils(client).getCookieNamed("yandexuid", domain.getCookieDomain()).getValue();
        return "y" + md5("0:" + yandexUid + ":" + days);
    }

    public static String withoutFirstLetter(Domain domain, Client client) {
        return CookieUtilsFactory.cookieUtils(client).getSecretKey(domain.getCookieDomain()).substring(1);
    }
    private static String md5(String data) {
        StringBuilder hexString;
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
        return hexString.toString();
    }

    private static StringBuilder getHexString(byte[] hash) {
        StringBuilder hexString = new StringBuilder();
        for (byte symbol : hash) {
            String tmp = (Integer.toHexString(0xFF & symbol));
            if (tmp.length() == 1) {
                hexString.append("0");
            }
            hexString.append(tmp);
        }
        return hexString;
    }

}
