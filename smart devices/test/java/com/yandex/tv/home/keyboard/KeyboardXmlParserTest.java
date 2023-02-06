package com.yandex.tv.home.keyboard;

import android.os.Build;

import com.yandex.tv.home.EmptyTestApp;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;
import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;
import org.xmlpull.v1.XmlPullParserFactory;

import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.List;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = {Build.VERSION_CODES.P}, application = EmptyTestApp.class)
public class KeyboardXmlParserTest {

    @Test
    public void parseCorrectXml() throws IOException, XmlPullParserException {
        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();

        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/input_test.xml")));
        KeyboardView.KeyboardXmlParser parser = new KeyboardView.KeyboardXmlParser(xmlInput);

        HashMap<String, List<KeyboardView.KeyButton>> alphabets = parser.parse();
        Assert.assertEquals(alphabets.get("ru").size(), 38);
        Assert.assertEquals(alphabets.get("num").size(), 16);
        Assert.assertNull(alphabets.get("uk"));
        Assert.assertNull(alphabets.get("en"));
        Assert.assertNull(alphabets.get("tr"));
    }

    @Test
    public void parseEmptyXml() throws IOException, XmlPullParserException {
        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();
        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/empty_test.xml")));
        KeyboardView.KeyboardXmlParser parser = new KeyboardView.KeyboardXmlParser(xmlInput);

        HashMap<String, List<KeyboardView.KeyButton>> alphabets = parser.parse();
        Assert.assertEquals(alphabets.values().size(), 0);
    }

    @Test(expected = XmlPullParserException.class)
    public void parseWrongTypeXml() throws IOException, XmlPullParserException {
        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();
        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/wrong_type_test.xml")));
        KeyboardView.KeyboardXmlParser parser = new KeyboardView.KeyboardXmlParser(xmlInput);
        parser.parse();
    }

    @Test
    public void parseEmptyTextXml() throws IOException, XmlPullParserException {
        XmlPullParser xmlInput;
        xmlInput = XmlPullParserFactory.newInstance().newPullParser();
        xmlInput.setInput(new InputStreamReader(getClass().getClassLoader().getResourceAsStream("xml/empty_text_test.xml")));
        KeyboardView.KeyboardXmlParser parser = new KeyboardView.KeyboardXmlParser(xmlInput);

        HashMap<String, List<KeyboardView.KeyButton>> alphabets = parser.parse();
        Assert.assertEquals(alphabets.get("test").get(0).getLabel(), "");
    }
}
