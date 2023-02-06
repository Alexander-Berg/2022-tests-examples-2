package ru.yandex.metrika.segments.core.parser.filter;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.jetbrains.annotations.NotNull;

/**
 * Created by orantius on 06.06.16.
 */
public class ParserComparator {
    public static void main(String[] args) throws Exception {
        Map<String, List<String>> map = getMap("/home/orantius/Downloads/paramsparse/visit_param");
        Map<String, List<String>> mapPre = getMap("/home/orantius/Downloads/paramsparse/visit_param_pre");
        System.out.println("map = " + map.size());
        System.out.println("mapPre = " + mapPre.size());

        for (Map.Entry<String, List<String>> ee : map.entrySet()) {
            System.out.println("ee = " + ee);
        }
        /*for (String key : mapPre.keySet()) {
            if(map.get(key).equals(mapPre.get(key))) {

            } else {
                System.out.println("key = " + key+" \\\\ "+map.get(key)+" // "+ mapPre.get(key));
            }
        }*/
    }

// key = src: { "" : 1 , "a" : [ ] } \\ [.1........ = 1 * 1, a......... = 0 * 1,
// src: { "a" : 1.0 , "a" : [ ] }, a.1.0........ = 1 * 1, a......... = 0 * 1,
// src: { "b" : 1.0 , "a" : [ ] }, b.1.0........ = 1 * 1, a......... = 0 * 1,
// src: { "-1" : 1.0 , "a" : [ ] }, -1.1.0........ = 1 * 1, a......... = 0 * 1,
// src: { "" : 1.0 , "a" : [ ] }, .1.0........ = 1 * 1, a......... = 0 * 1] // [.1........ = 1 * 1, src: { "a" : 1.0 , "a" : [ ] }, a.1.0........ = 1 * 1, src: { "b" : 1.0 , "a" : [ ] }, b.1.0........ = 1 * 1, src: { "-1" : 1.0 , "a" : [ ] }, -1.1.0........ = 1 * 1, src: { "" : 1.0 , "a" : [ ] }, .1.0........ = 1 * 1]

    @NotNull
    public static Map<String, List<String>> getMap(String fileName) throws FileNotFoundException {
        BufferedReader br = new BufferedReader(new FileReader(fileName));
        List<String> lines = br.lines().collect(Collectors.toList());
        Map<String,List<String>> res = new HashMap<>();
        String key = null;
        List<String> value = null;
        for (String line : lines) {
            if(line.contains("..")) {
                value.add(line);
            } else {
                if(key != null) {
                    res.put(key, value);
                }
                key = line;
                value = new ArrayList<>();
            }
        }
        res.put(key, value);
        return res;
    }
}
