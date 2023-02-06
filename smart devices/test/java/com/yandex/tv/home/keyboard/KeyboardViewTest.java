package com.yandex.tv.home.keyboard;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;

import com.yandex.tv.home.EmptyTestApp;
import com.yandex.tv.home.R;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;
import org.xmlpull.v1.XmlPullParserFactory;

import java.io.InputStreamReader;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = {Build.VERSION_CODES.P}, application = EmptyTestApp.class)
public class KeyboardViewTest {

    @Test
    public void SimpleCreateTest() throws XmlPullParserException {
        final Context context = RuntimeEnvironment.application;
        KeyboardView keyboard = new KeyboardView(context, null);

        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();
        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/input_test.xml")));
        keyboard.setInputXml(xmlInput);

        keyboard.bindInput(new Listener());
    }

    @Test
    public void SetAttributesTest() throws XmlPullParserException {
        final Context context = RuntimeEnvironment.application;
        KeyboardView keyboard = new KeyboardView(context, null);

        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();
        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/input_test.xml")));
        keyboard.setInputXml(xmlInput);
        keyboard.setTextSize(1);
        keyboard.setTextColor(ColorStateList.valueOf(Color.RED));
        keyboard.setKeySelector(context.getDrawable(R.drawable.keyboard_text_button_background));
        keyboard.setKeyAnimator(R.animator.keyboard_list_animator);
        keyboard.bindInput(new Listener());
    }

    @Test
    public void ChangeNumAndLangTest() throws XmlPullParserException {
        final Context context = RuntimeEnvironment.application;
        KeyboardView keyboard = new KeyboardView(context, null);

        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();
        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/input_test.xml")));
        keyboard.setInputXml(xmlInput);

        keyboard.bindInput(new Listener());
        keyboard.setLanguages(17);
        Assert.assertEquals(keyboard.adapter.getItemCount(), 38);
        keyboard.adapter.changeNum();
        Assert.assertEquals(keyboard.adapter.getItemCount(), 16);
        keyboard.adapter.changeNum();
        Assert.assertEquals(keyboard.adapter.getItemCount(), 38);
        keyboard.adapter.changeLang();
        Assert.assertEquals(keyboard.adapter.getItemCount(), 38);
    }

    class Listener implements KeyboardView.KeyboardListener {

        @Override
        public void onInput(Character symbol) {

        }

        @Override
        public void onDelete() {

        }

        @Override
        public void onDeleteAll() {

        }

        @Override
        public void onEnter() {

        }

        @Override
        public void onChangeLang() {

        }

        @Override
        public void onChangeNum() {

        }
    }
}
