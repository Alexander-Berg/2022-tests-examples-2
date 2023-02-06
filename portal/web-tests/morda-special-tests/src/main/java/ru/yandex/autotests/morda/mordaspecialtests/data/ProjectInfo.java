package ru.yandex.autotests.morda.mordaspecialtests.data;

import ch.lambdaj.function.convert.Converter;
import org.openqa.selenium.By;
import ru.yandex.testlab.wiki.annotations.WikiColumn;
import ru.yandex.testlab.wiki.annotations.WikiRow;

import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.convert;

/**
 * Created by eoff on 13/10/14.
 */
@WikiRow(pageUrl = "Users/eoff/spec/list")
public class ProjectInfo {
    @WikiColumn(name = "project")
    private String project;

    @WikiColumn(name = "prod")
    private String prod;

    @WikiColumn(name = "test")
    private String test;

    @WikiColumn(name = "urls")
    private String urls;

    @WikiColumn(name = "exclude")
    private String exclude;

    @WikiColumn(name = "js")
    private String js;

    @WikiColumn(name = "inProd")
    private boolean inProd;

    public String getProject() {
        return project;
    }

    public void setProject(String project) {
        this.project = project;
    }

    public String getExclude() {
        return exclude;
    }

    public void setExclude(String exclude) {
        this.exclude = exclude;
    }

    public String getJs() {
        return js;
    }

    public void setJs(String js) {
        this.js = js;
    }

    private List<String> getParsedUrls() {
        List<String> result = new ArrayList<>();

        for (String s : urls.split("\n")) {
            String trimmed = s.trim();
            if (!trimmed.isEmpty()) {
                result.add(trimmed);
            }
        }

        return result;
    }

    public List<By> getParsedExclusions() {
        List<By> result = new ArrayList<>();

        for (String s : exclude.split("\n")) {
            String trimmed = s.trim();
            if (!trimmed.isEmpty()) {
                result.add(By.xpath(trimmed));
            }
        }

        return result;
    }

    public List<ProjectInfoCase> getProjectInfoCases() {
        final String project = this.project;
        final String prod = this.prod;
        final String test = this.test;

        return convert(getParsedUrls(), new Converter<String, ProjectInfoCase>() {
            @Override
            public ProjectInfoCase convert(String s) {
                return new ProjectInfoCase(project, prod, test, s, getParsedExclusions(), getJs());
            }
        });
    }

    public void setUrls(String urls) {
        this.urls = urls;
    }

    public String getUrls() {
        return urls;
    }

    public String getProd() {
        return prod;
    }

    public void setProd(String prod) {
        this.prod = prod;
    }

    public String getTest() {
        return test;
    }

    public void setTest(String test) {
        this.test = test;
    }

    public boolean isInProd() {
        return inProd;
    }

    public void setInProd(boolean inProd) {
        this.inProd = inProd;
    }

    public static class ProjectInfoCase {
        private String project;
        private String prod;
        private String test;
        private String url;
        private List<By> excude;
        private String js;

        public ProjectInfoCase(String project, String prod, String test, String url, List<By> excude,
                               String js) {
            this.project = project;
            this.prod = prod + url;
            this.test = test + url;
            this.url = url;
            this.excude = excude;
            this.js = js;
        }

        public String getProject() {
            return project;
        }

        public void setProject(String project) {
            this.project = project;
        }

        public String getProd() {
            return prod;
        }

        public void setProd(String prod) {
            this.prod = prod;
        }

        public String getTest() {
            return test;
        }

        public void setTest(String test) {
            this.test = test;
        }

        public List<By> getExcude() {
            return excude;
        }

        public void setExcude(List<By> excude) {
            this.excude = excude;
        }

        public String getJs() {
            return js;
        }

        @Override
        public String toString() {
            return project + ": " + url;
        }
    }
}
