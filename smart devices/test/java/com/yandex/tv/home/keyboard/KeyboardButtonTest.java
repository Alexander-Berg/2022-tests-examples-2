package com.yandex.tv.home.keyboard;

import android.os.Build;

import com.yandex.tv.home.EmptyTestApp;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = {Build.VERSION_CODES.P} , application = EmptyTestApp.class)
public class KeyboardButtonTest {

    @Test(expected = IllegalArgumentException.class)
    public void SimpleGettersAndSettersTest() {
        KeyboardView.KeyButton button = new KeyboardView.KeyButton();
        Assert.assertEquals(button.getType(), KeyboardView.KeyButton.EMPTY);

        button.setLabel("test");
        button.setType(KeyboardView.KeyButton.NUM);
        button.setSpanSize(1000);
        Assert.assertEquals(button.getType(), KeyboardView.KeyButton.NUM);
        Assert.assertEquals(button.getSpanSize(), 1000);
        Assert.assertEquals(button.getLabel(), "test");
        button.setSpanSize(-1);
    }

}
