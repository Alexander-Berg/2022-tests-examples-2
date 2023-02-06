package demand_etl.layer.yt.ods.ucommunication;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import scala.collection.mutable.Seq;
import scala.collection.JavaConverters;

import java.util.*;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SuppressWarnings("unused")
public class UserNotificationSubscriptionLogTest {
    @ParameterizedTest
    @MethodSource
    public void testTagMap(Seq<String> includedTags,
                           Seq<String> excludedTags,
                           HashMap<String, Boolean> expected) {
        assertEquals(expected, UserNotificationSubscriptionLog.tagMap(includedTags, excludedTags));
    }

    private static Stream<Arguments> testTagMap() {
        ArrayList<String> listIncluded = new ArrayList<String>();
        listIncluded.add("i1");
        listIncluded.add("i2");
        Seq seqIncluded = JavaConverters.asScalaBuffer(listIncluded).seq();

        ArrayList<String> listExcluded = new ArrayList<String>();
        listExcluded.add("e1");
        listExcluded.add("e2");
        listExcluded.add("e3");
        Seq seqExcluded = JavaConverters.asScalaBuffer(listExcluded).seq();

        HashMap<String, Boolean> expected1 = new HashMap<>();
        expected1.put("", null);

        HashMap<String, Boolean> expected2 = new HashMap<>();
        expected2.put("i1", true);
        expected2.put("i2", true);

        HashMap<String, Boolean> expected3 = new HashMap<>();
        expected3.put("e1", false);
        expected3.put("e2", false);
        expected3.put("e3", false);

        HashMap<String, Boolean> expected4 = new HashMap<>();
        expected4.put("i1", true);
        expected4.put("i2", true);
        expected4.put("e1", false);
        expected4.put("e2", false);
        expected4.put("e3", false);

        return Stream.of(
                Arguments.of(null, null, expected1),
                Arguments.of(seqIncluded, null, expected2),
                Arguments.of(null, seqExcluded, expected3),
                Arguments.of(seqIncluded, seqExcluded, expected4)
        );
    }
}
