package ru.yandex.quasar.app.webview.cookie;

import android.util.Pair;

import org.junit.Test;
import org.junit.runner.RunWith;

import org.robolectric.RobolectricTestRunner;

import java.util.ArrayList;

import static org.junit.Assert.assertEquals;

@RunWith(value = RobolectricTestRunner.class)
public class CookieHelperUtilTest {
    @Test
    public void testFixThumbUrl() {
        ArrayList<Pair<String, String>> pairs = new ArrayList<>();
        pairs.add(
            new Pair<>("http://avatars.mds.yandex.net/get-ott/236744/2a0000/672x438",
                    "https://avatars.mds.yandex.net/get-ott/236744/2a0000/%%"));
        pairs.add(
            new Pair<>("avatars.mds.yandex.net/get-ott/236744/2a0000/672x438",
                    "https://avatars.mds.yandex.net/get-ott/236744/2a0000/%%"));
        pairs.add(
            new Pair<>("https://avatars.mds.yandex.net/get-ott/236744/2a0000/672x438",
                    "https://avatars.mds.yandex.net/get-ott/236744/2a0000/%%"));
        pairs.add(
            new Pair<>("https://avatars.mds.yandex.net/get-ott/236744/2a0000/%%",
                    "https://avatars.mds.yandex.net/get-ott/236744/2a0000/%%"));
        pairs.add(
            new Pair<>("avatars.mds.yandex.net/get-ott/236744/2a0000/%%",
                    "https://avatars.mds.yandex.net/get-ott/236744/2a0000/%%"));
        pairs.add(
            new Pair<>("ftp://avatars.mds.yandex.net/get-ott/236744/2a0000/%%",
                    "ftp://avatars.mds.yandex.net/get-ott/236744/2a0000/%%"));
        pairs.add(
            new Pair<>("http://avatars.mds.yandex.net/get-ott/236744/xa0000/672x438",
                    "https://avatars.mds.yandex.net/get-ott/236744/xa0000/%%"));
        pairs.add(
            new Pair<>("https://avatars.mds.yandex.net/get-vthumb/924554/d7075e5df2c6a13fb8044d6974da0ba7/%%",
                       "https://avatars.mds.yandex.net/get-vthumb/924554/d7075e5df2c6a13fb8044d6974da0ba7/%%"));

        for (Pair<String, String> pair : pairs) {
            assertEquals(CookieHelperUtil.Companion.fixThumbUrl(pair.first), pair.second);
        }
    }
}