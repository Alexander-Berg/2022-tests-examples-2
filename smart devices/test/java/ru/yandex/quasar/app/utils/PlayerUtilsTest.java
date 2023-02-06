package ru.yandex.quasar.app.utils;

import android.net.Uri;

import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;

import ru.yandex.quasar.app.video.players.ExoPlayerUtils;

import static com.google.android.exoplayer2.C.TYPE_DASH;
import static com.google.android.exoplayer2.C.TYPE_HLS;
import static com.google.android.exoplayer2.C.TYPE_SS;

@RunWith(value = AndroidJUnit4.class)
public class PlayerUtilsTest {

    @Test
    public void smoothStreamingTest() {
        Assert.assertEquals(TYPE_SS, ExoPlayerUtils.inferContentType(Uri.parse("https://strm.yandex.ru/vh-ott-converted/vod-content/234428222/437cd6a3-df3e-fdbc-9b71-ac6f18ade72b.ism/manifest.sd.ismc?end=1563917831&start=1563910715&vsid=4f921c53a30f23f79f8948e2e474e4b50fcb2e8a15beb285ac96f1026afff8d2")));
    }

    @Test
    public void smoothStreamingTest2() {
        Assert.assertEquals(TYPE_SS, ExoPlayerUtils.inferContentType(Uri.parse("https://strm.yandex.ru/vh-ott-converted/vod-content/234428222/437cd6a3-df3e-fdbc-9b71-ac6f18ade72b.ism/manifest?end=1563917831&start=1563910715&vsid=4f921c53a30f23f79f8948e2e474e4b50fcb2e8a15beb285ac96f1026afff8d2")));
    }

    @Test
    public void hlsTest() {
        Assert.assertEquals(TYPE_HLS, ExoPlayerUtils.inferContentType(Uri.parse("https://strm.yandex.ru/vh-youtube-converted/vod-content/17888634735832364674.m3u8?end=1563976618&start=1563976169&vsid=a438fde5573ded2d269fb5883e65ef5be40392584a7f36428241861f664573c4")));
    }

    @Test
    public void dashTest() {
        Assert.assertEquals(TYPE_DASH, ExoPlayerUtils.inferContentType(Uri.parse("https://strm.yandex.ru/vh-youtube-converted/vod-content/17888634735832364674.mpd?end=1563976618&start=1563976169&vsid=a438fde5573ded2d269fb5883e65ef5be40392584a7f36428241861f664573c4")));
    }
}
