package ru.yandex.metrika.util;

import java.io.BufferedWriter;
import java.io.StringWriter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import org.junit.Ignore;

import ru.yandex.metrika.util.json.CustomJsonFactory;
import ru.yandex.metrika.util.json.ObjectMappersFactory;

import static org.junit.Assert.assertEquals;

/**
 *
 * @author orantius
 * @version $Id$
 * @since 7/29/13
 */
@Ignore
public class JSONBuilderTest {

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper(new CustomJsonFactory());
        /*jf.setCharacterEscapes(new CharacterEscapes() {
            @Override
            public int[] getEscapeCodesForAscii() {
                return standardAsciiEscapesForJSON();
            }

            @Override
            public SerializableString getEscapeSequence(int ch) {
                System.out.println("ch = " + ch);
                if(ch == 0x2028 || ch == 0x2029) {
                    return new SerializedString("\\u"+ch);
                } else {
                    return new SerializedString(String.valueOf((char)ch));
                }
            }
        }); */

        mapper.setPropertyNamingStrategy(PropertyNamingStrategy.CAMEL_CASE_TO_LOWER_CASE_WITH_UNDERSCORES);
        ObjectMappersFactory.setDefaultInclusionStrategy(mapper);
        //mapper.configure(JsonGenerator.Feature.ESCAPE_NON_ASCII, true);
        StringWriter out = new StringWriter();
        BufferedWriter bw = new BufferedWriter(out);
        String arg = new String(new char[] {'a', 'b', 'c', '\u2028', '\u2029', 'ы', 'ы'});
        mapper.writeValue(bw, new Wrapper(arg));
        assertEquals("{\"name\":\""+arg+"\"}", out.toString());
        System.out.println("out.to = " + out + arg);
    }

    public static class Wrapper {
        String name;

        public Wrapper() {
        }

        public Wrapper(String name) {
            this.name = name;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }
    }
}
