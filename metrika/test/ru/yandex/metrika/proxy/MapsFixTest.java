package ru.yandex.metrika.proxy;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Arrays;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.url.NormalizedURI;

import static org.junit.Assert.assertEquals;

/**
 * @author Ivan Gorbachev
 * @version $ld$
 * @since 6/25/12
 */
public class MapsFixTest {

    MapsFix gmf = new MapsFix();

    @Before
    public void setUp() throws Exception {
        gmf.setGoogleMapsApiKey("v3");
    }

    String testStr = "Learning Scala\n" +
            "Created by bagwell on 2009-03-24. Updated: 2012-04-22, 16:31\n" +
            "The best way to learn Scala depends on what you know already and the way you prefer to learn things. You will find there are a variety of different resources you can use to speed up the whole process. These include books, tutorials, training courses, presentations, and of course the Scala compiler for practice. Many people find a good combination is to have one of the Scala books at hand and to start right away trying the examples with the Scala Compiler. On the other hand, you may want to get started without a book or take a Scala training course. In that case, you will find on this website resources to help you get right on with the task but, as you may expect, in a somewhat more disjointed way.\n" +
            "As your knowledge of Scala grows, you will find there is more advanced material and a very friendly Scala community at hand to help you. They all share a passion for Scala and welcome newcomers warmly. Many have written helpful material for programmers new to Scala, will respond to emails asking for help or are sharing neat new techniques, advanced concepts or tools in one of several Scala forums or personal blogs. Perhaps join a Scala user group close by. \n" +
            "To know more, just select one of the options below according to your existing experience:\n" +
            "Several years of Java programming\n" +
            "Some Scala programming\n" +
            "Several years experience of C++, Ruby, Python, Visual Basic, etc\n" +
            "Experience of a functional language like Haskell, ML, F#, Lisp, Clojure etc as well as an imperative one.\n" +
            "Researcher in Computer Languages\n" +
            "Beginner, never programmed in any language\n" +
            " \n" +
            "Java Programmer\n" +
            "Many things you already know from your Java experience directly carry over to the Scala environment. Scala programs run on the Java VM and are bytecode compatible with Java, so you can make full use of existing Java libraries or existing application code. You can call Scala from Java and you can call Java from Scala, the integration is quite seamless. Moreover, you will also be able to use familiar development tools, Eclipse, NetBeans, or Intellij for example, all of which support Scala. So you have far less to learn.\n" +
            "Many top-notch programmers and industry leaders have been captivated by Scala. They have already created a growing range of books on Scala for you to choose from. Many people prefer the organised structure of a good book to guide them through their learning process but typically like to complement this with hands on practice running the code examples with the Scala compiler. To do this you will need to install the Scala compiler.\n" +
            "Scala supports OO and Functional programming styles. You do not need to know any functional programming languages in order to learn Scala. Most of the books and learning materials will introduce you to the concept of passing functions to methods just like other variables, and other functional language features, like immutability, that make the support of multi-core concurrency much easier.\n" +
            "Resources\n" +
            '\n' +
            "While you wait for a book you will find the following resources useful:\n" +
            "Video Talk on Scala by Martin Odersky\n" +
            "This talk was given by Martin Odersky, the creator of Scala, at the FODEM conference. It provides an excellent introduction to the language features and much of the rationale behind its design. You can find this copy of his slides and a transcription of his talk handy.\n" +
            " \n" +
            "Try Simply Scala\n" +
            "Simply Scala is a web site where you can interactively try Scala. There you will find a tutorial that gives a rapid overview of the basic language features, the syntax, examples you can run and the ability to try your own code with an interactive interpreter.\n" +
            " \n" +
            "Scala Training Courses \n" +
            "Typesafe and its partners provide regular Scala training courses and Scala consulting in many locations world-wide. They provide expert teachers, including Martin Odersky, Iulian Dragos, Heiko Seeberger and other certified Scala trainers, to take you through the Scala language in a systematic way either in group classes at their facilities or on your own site.\n" +
            " \n" +
            "Free On-Line Books on Scala\n" +
            "A free sample of Scala for the Impatient, a book written by Cay Horstmann is available from Typesafe for download. A very practical book for developers with Java experience learning Scala. O'Reilly has made Programming Scala, a book written by Alex Payne and Dean Wampler freely available on-line. This comprehensive book will appeal to experienced programmers wanting to learn Scala. It is packed with examples and clearly explains in a pragmatic way most of the more advanced features of Scala.   \n" +
            " \n" +
            "\"Programming in Scala,\" 2nd ed., by Martin Odersky, Lex Spoon, and Bill Venners\n" +
            "This is the award winning, authoritative book co-written by Scala's designer. The second edition comes with more than 100 pages of new material covering new features in 2.8, while the first edition of the book has been made freely available. For more on this and other books, see the list of available Scala books.\n" +
            "Try Kojo\n" +
            "Kojo is a Scala development environment designed for use in schools. It comes with a Scala tutorial that gives a rapid overview of the basic language features, the syntax, examples you can run and the ability to try your own code. It is simple to download and install.\n" +
            " \n" +
            "Java to Scala with the Help of Experts\n" +
            "A collection of some of the almost endless supply of tips available for Java programmers new to Scala. There are also mini-blog series designed to take you through many of the important features of the Scala language in a friendly way.\n" +
            " \n" +
            "Brief Scala Tutorial\n" +
            "A 20 page introduction to scala and some of the basic concepts and a good place to start. You will find more code examples here.\n" +
            " \n" +
            "Scala By Example\n" +
            "Takes you through the Scala features with many examples. It does assume that you are already familiar with the basic Scala syntax and a basic understanding of functional programming. It is an excellent way to expand your knowledge and skill.\n" +
            " \n" +
            "Scala Overview\n" +
            "This is a paper summarizing the features of the Scala Language in a formal and concise way. An excellent reference for language researchers or advanced programmers.\n" +
            " \n" +
            "Tour of Scala\n" +
            "Here is a more descriptive, yet formal, summary of the Scala language features with many code examples. A great language reference for programmers needing to check correct use of a specific Scala feature or its correct syntax. Once you have mastered the basic Scala syntax then this is a good place to look to learn specific features.\n" +
            " \n" +
            "Scala Programmer\n" +
            "If you are a Scala programmer looking for more examples and help, you will a list of useful resources by following this link. You may want to check out the community resources too, or browse the list of the available documentation on this page.\n" +
            "  \n" +
            "C++, C#, Ruby, Python, Visual Basic, etc Programmer\n" +
            "If you have no Java experience and are coming from these languages, then you will need to learn about the Java ecosystem. However, many concepts such as closures, passing functions, type inferencing or generics will already be familiar to you. Since Scala makes full use of the Java libraries and runs on the JVM you would probably find it useful to have a book on Java and the Java libraries handy: Scala code can call Java code and Java code can call Scala code, and some of the basic concepts and APIs in the two are related. In order to discover Scala and its features, you will probably need one of the Scala books, and the Scala compiler. You will also find useful some of the introductory resources available on this website.\n" +
            "If you are a C# programmer, you may find the series \"Scala for C# programmers\" by Ivan Towlson on flatlander quite helpful:\n" +
            "Part 1 Mixins and Traits\n" +
            "Part 1a Mixins and Traits, Behind the scenes\n" +
            "Part 2 Singletons\n" +
            "Part 3 Pass by Name\n" +
            "Part 4 Multiple return values\n" +
            "Part 5 Implicits\n" +
            "Part 6 Infix Operators\n" +
            " \n" +
            "From Haskell, ML, F#, Lisp, Clojure, etc Programmer\n" +
            "If you come to Scala from a functional programming background, you will find most of the more advanced functional programming style familiar. Scala integrates OO and functional programming together into one uniform language environment. By the very nature of this integration, the syntax is a little more complex than in pure functional languages. Scala supports OO programming in a very natural way, and you can use a purely functional programming style if you prefer. Since Scala makes full use of the Java libraries and runs on the JVM, you will probably find it useful to have a book on Java and the Java libraries handy: Scala code can call Java code and Java code can call Scala code, and some of the features of the two are related. In order to discover Scala and its features, you will need one of the Scala books, and the Scala compiler. You will also find the introductory resources available on this website.\n" +
            " \n" +
            "Computer Language Researcher\n" +
            "If you are a language researcher, you will find \"Programming in Scala\", the book by Martin Odersky et al, a good place to obtain a general overview of the language. You will find papers, talks, and other academic-related material on Scala, including in-depth discussion of the formal and theoretical aspects of the language, as well as implementation details, in the Language Research section of this website. More introductory material on Scala can be found in the resources section of this page, above. For an in-depth view of the technical details of the language, you may also find of interest the Scala Language Specification.\n" +
            " \n" +
            "Beginner Programmer\n" +
            "Nearly all of the material existing for Scala assume that you already have some programming experience and are familiar with the basic jargon. If you have never done any programming, you may like to consider starting with Java first, as there is a large amount of beginner material available. You may then want to progress to Scala from there. If you're impatient, however, it is entirely possible to start directly to Scala; in that case, we would recommend you find someone to help you setting up the Scala compiler and an IDE on your computer. The book \"Beginning in Scala\" would then be a good companion to start with; you can find further details on that and the other books here.";


    String test2() {
        String s1 = '\n' +
                '\n' +
                "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n" +
                "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n" +
                "<head>\n" +
                "<meta name=\"google-site-verification\" content=\"VEO5z9in4XN1cgdXZtyNe6UUbtnI1N7P4-REVsfhag0\" />\n" +
                "<meta name=\"google-site-verification\" content=\"IdhyK7IIHM6f3Bsdz3Dtx4YNA0BCokO7Ynm2RUlQr9k\" />\n" +
                "<meta http-equiv=\"content-type\" content=\"text/html; charset=windows-1251\" />\n" +
                '\n' +
                "<title>Пансионат Подмосковные Липки</title>\n" +
                "<!-- подключаем нужные стили:\n" +
                "файл content.css содержит стили для основного контента,\n" +
                "файл summer_day.css содержит стили для только для дизайна \"Лето-День\"\n" +
                "файл news.css содержит стили для только для отображения новостей, таким образом его можно подключать при надобности\n" +
                " -->\n" +
                "<link rel=\"shortcut icon\" href=\"/images/ptravel.ico\" type=\"image/x-icon\" />\n" +
                "<link href=\"/css/summer_day.css\" rel=\"stylesheet\" type=\"text/css\" media=\"all\" />\n" +
                "<link href=\"/css/content.css\" rel=\"stylesheet\" type=\"text/css\" media=\"all\" />\n" +
                "<link href=\"/css/news.css\" rel=\"stylesheet\" type=\"text/css\" media=\"all\" />\n" +
                "<!--link href=\"css/treeview.css\" rel=\"stylesheet\"  media=\"all\" /-->\n" +
                "<link href=\"/css/jquery.treeview.css\" rel=\"stylesheet\" type=\"text/css\" /> \n" +
                "<link href=\"/js/jquery/plugin/highslide/highslide.css\"  rel=\"stylesheet\" type=\"text/css\" /> \n" +
                "<link href=\"/js/jquery/plugin/ui/css/smoothness/jquery-ui-1.8.7.custom.css\" rel=\"stylesheet\" type=\"text/css\" /> \n" +
                "<link href=\"/js/jquery/plugin/css/jquery.lightbox-0.5.css\"  rel=\"stylesheet\" type=\"text/css\" />\n" +
                '\n' +
                "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js\" type=\"text/javascript\"></script>\n" +
                "<script src=\"http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js\" type=\"text/javascript\"></script>\n" +
                "<script src= \"/js/jquery/plugin/jquery.validate.js\" type=\"text/javascript\"></script>\n" +
                "<script src=\"/js/jquery/plugin/jquery.lightbox-0.5.js\" type=\"text/javascript\"></script>\n" +
                "<script src=\"/js/ga.js\" type=\"text/javascript\"></script>\n" +
                "<script src=\"/js/ping.js\" type=\"text/javascript\"></script>\n" +
                '\n' +
                "<script type=\"text/javascript\" src=\"http://vkontakte.ru/js/api/share.js?10\" charset=\"windows-1251\"></script>\n" +
                "<link href=\"http://stg.odnoklassniki.ru/share/odkl_share.css\" rel=\"stylesheet\" />\n" +
                "<script src=\"http://stg.odnoklassniki.ru/share/odkl_share.js\" type=\"text/javascript\" ></script>\n" +
                "<style type=\"text/css\">\n" +
                ".odkl-klass, .odkl-klass:hover {background:none;}\n" +
                ".odkl-klass {background: url(http://ptravel.ru/images/social/odnoklassniki.png) no-repeat;}\n" +
                "</style>\n" +
                "<script type=\"text/javascript\" src=\"//yandex.st/share/share.js\" charset=\"utf-8\"></script>\n" +
                "<script type=\"text/javascript\" src=\"http://userapi.com/js/api/openapi.js?34\"></script>\n" +
                "<script type=\"text/javascript\">    VK.init({ apiId: 2472050, onlyWidgets: true });</script>\n" +
                "<script type=\"text/javascript\" src=\"https://apis.google.com/js/plusone.js\"></script>\n" +
                "</head>\n" +
                '\n' +
                "<body>\n" +
                '\n' +
                "<script type=\"text/javascript\" src=\"/js/qts.js\"></script>\n" +
                '\n' +
                "<!-- Шапка, картинка и логотип -->\n" +
                "<div id=\"header\">\n" +
                "<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\" align=\"right\">\n" +
                "  <tr height=\"240\">\n" +
                "    <td style=\"padding-right:60px;background-image:url(/images/summer_day/duck_bg.png); background-position:bottom right; background-repeat:no-repeat;\" align=\"right\" valign=\"top\">\n" +
                "    <div id=\"companylogo\" style=\"float:left;\"><a href=\"/\"><img src=\"/images/summer_day/companylogo.png\" width=\"190\" height=\"60\" alt=\"Протей Тревел\" border=\"0\" style=\"padding-top:15px;\" /></a></div><br /><br />\n" +
                "<br /><br />\n" +
                '\n' +
                "\t</td>\n" +
                "    <td><img src=\"/images/summer_day/icons.png\" width=\"30\" height=\"228\" border=\"0\" usemap=\"#Map\" /></td>\n" +
                "  </tr>\n" +
                "</table>\n" +
                "</div>\n" +
                '\n' +
                "<table width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" align=\"center\">\n" +
                "  <tr>\n" +
                "    <td width=\"710\"><img src=\"/images/summer_day/header1.jpg\" alt=\"Протэй Трэвэл\" width=\"710\" height=\"228\" border=\"0\" /></td>\n" +
                "\t<td width=\"190\" style=\"background-image:url(/images/summer_day/header2.jpg); background-repeat:no-repeat; padding-top:20px;\" valign=\"top\">\n" +
                "\t</td>\n" +
                "\t<td style=\"background-image:url(/images/summer_day/header_bg.jpg); background-repeat:repeat-x;\">&nbsp;</td>\n" +
                "\t<td width=\"110\"><img src=\"/images/summer_day/header3.jpg\" alt=\"Протэй Трэвэл\" width=\"110\" height=\"228\" border=\"0\"/></td>\n" +
                "  </tr>\n" +
                "</table>\n" +
                '\n' +
                "<!-- Верхнее меню -->\n" +
                "<table width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" align=\"center\">\n" +
                "  <tr>\n" +
                "    <td width=\"50\" height=\"27\"><img src=\"/images/summer_day/menu_start.jpg\" width=\"50\" height=\"27\" /></td>\n" +
                "    \n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/SimpleMap.aspx?n=13\">ОТДЫХ В ПОДМОСКОВЬЕ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/News.aspx\">НОВОСТИ И СПЕЦПРЕДЛОЖЕНИЯ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/News.aspx?id=253\">ДЛЯ ТУРИСТОВ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/Agency.aspx\">ДЛЯ ТУРАГЕНТСТВ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/Corporation.aspx\">КОРПОРАТИВНЫМ КЛИЕНТАМ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/ta/TISearch.aspx\">ПОИСК ЗАРУБЕЖНЫХ ТУРОВ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td class=\"menu1\" height=\"27\"><a href=\"/About.aspx\">О КОМПАНИИ</a></td>\n" +
                "\t<td width=\"1\"><img src=\"images/menu1_div.png\" width=\"1\" height=\"27\" /></td>\n" +
                "\t<td width=\"50\" height=\"27\"><img src=\"/images/summer_day/menu_end.jpg\" width=\"50\" height=\"27\" /></td>\n" +
                "  </tr>\n" +
                "</table>\n" +
                '\n' +
                "<table width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" align=\"center\">\n" +
                "  <tr>\n" +
                "        <td align=\"left\" valign=\"top\" width=\"210\">\n" +
                "    <!-- Первая колонка слева -->\n" +
                "<!--Поиск-->\n" +
                "<div id=\"search_new1\">\n" +
                "<div class=\"leftline\" style=\"height:64px;\"></div>\n" +
                "<div class=\"cornert\">\n" +
                "<div class=\"corner\" id=\"cornerlt\"></div>\n" +
                "<div class=\"corner\" id=\"cornerrt\"></div>\n" +
                "</div>\n" +
                '\n' +
                "<font>Быстрый поиcк</font><br/><br/>\n" +
                '\n' +
                "<div style=\"magrin-top:-10px;\"><form action=\"Search.aspx\" method=\"post\" enctype=\"multipart/form-data\">\t\n" +
                "<div id=\"search_inp\">\n" +
                "<div id=\"search_inpl\"></div>\n" +
                "<input name=\"search_pattern\" type=\"text\" value=\"Введите запрос\" onclick=\"if(this.value=='Введите запрос')this.value='';\" onblur=\"if(this.value=='')this.value='Введите запрос';\"/>\n" +
                "<div id=\"search_inpr\"></div>\n" +
                "</div><input name=\"search\" type=\"image\" src=\"/images/autumn_day/search_btn.jpg\" align=\"middle\" style=\"margin-top:-5px;\"/>\n" +
                "</form></div>\n" +
                "<!--a href=\"AdvSearch.aspx\" id=\"search_full\">Расширенный поиск</a-->\n" +
                '\n' +
                "<div class=\"cornerb\">\n" +
                "<div class=\"corner\" id=\"cornerlb\"></div>\n" +
                "<div class=\"corner\" id=\"cornerrb\"></div></div>\n" +
                "</div><br />\n" +
                "<!--конец поиска-->\n" +
                "   \t<div class=\"spacerl_1\"><div class=\"spacerl_2\"></div></div>\n" +
                "    \n" +
                "        <div id=\"banner\">\n" +
                "\t<a href=\"/NYSpecials.aspx\">\n" +
                '\n' +
                "\t    <img src=\"/bb/ny09.jpg\" alt=\"Новый Год\" width=\"200\" border=\"0\"/></a>\n" +
                "        </div>\n" +
                '\n' +
                "     <div class=\"spacerl_1\"><div class=\"spacerl_2\"></div></div>\n" +
                "     \n" +
                "    <ul class=\"nav_x\">\n" +
                "    <li><a href=\"/SimpleMap.aspx?p=86\">Подмосковье</a></li><li><a href=\"/SimpleMap.aspx?n=4\">Регионы России</a></li><li><a href=\"/SimpleMap.aspx?p=5\">Краснодарский край</a></li><li><a href=\"/SimpleMap.aspx?p=7\">Крым</a></li><li><a href=\"/SimpleMap.aspx?p=91\">Кавказкие Минеральные Воды</a></li><li><a href=\"/SimpleMap.aspx?p=109\">Беларусь</a></li><li><a href=\"/Excurs.aspx\">Экскурсионные туры</a></li><li><a href=\"/Cruises.aspx\">Круизы</a></li><li><a href=\"/SimpleMap.aspx?n=8\">Отдых за рубежом</a></li><li><a href=\"#\">Авиа и ж/д билеты</a></li><li><a href=\"/Animation.aspx\">Анимация</a></li><li><a href=\"/SimpleMap.aspx?p=110\">Украина</a></li>\n" +
                "    </ul>\n" +
                "    <br />\n" +
                '\n' +
                "\t\n" +
                '\n' +
                "\t<div id=\"news_leftcol\"> \n" +
                "\t\t<div id=\"news_leftcol_title\">Новости</div>\t\n" +
                "\t\t\t<div id=\"news_leftcol_center\"> \n" +
                "\t\t\t<div class=\"news_date_my\"><img src=\"/images/rating_light.png\" style=\"margin:-3px 5px -3px 5px;\" />20.08.12</div> <a href=\"News.aspx?id=293\">Специальное предложение для родителей и детей в отели\"Best Western Кантри Резорт\"\n" +
                '\n' +
                "</a><br/><br/><div class=\"news_date_my\"><img src=\"/images/rating_light.png\" style=\"margin:-3px 5px -3px 5px;\" />20.08.12</div> <a href=\"News.aspx?id=294\">Изменения в режиме работы офиса с 1 сентября 2012г.\n" +
                "</a><br/><br/><div class=\"news_date_my\"><img src=\"/images/rating_light.png\" style=\"margin:-3px 5px -3px 5px;\" />15.08.12</div> <a href=\"News.aspx?id=292\">Скидки для групп туристов  более 20 человек в ДО \"Ершово\" с 01.09.12г. по 31.10.12 г. - 10%</a><br/><br/>\n" +
                "\t\t\t</div>\n" +
                "\t\t\t<div id=\"news_leftcol_bottom\"> \n" +
                "\t\t\t<img src=\"/images/rating_light.png\" width=\"14\" height=\"14\" />&nbsp;\n" +
                "\t\t\t<a href=\"News.aspx\">архив новостей</a> \n" +
                "\t\t</div>\t\n" +
                "\t</div> \t\t\t\n" +
                "\t\n" +
                "\t<div id=\"main_spacer\"></div> \n" +
                " \n" +
                "\t<!--Колонка статьи--> \n" +
                "\t\n" +
                "\t<div id=\"stat_leftcol\"> \n" +
                "\t\t<div id=\"stat_leftcol_title\">Статьи</div>\t\n" +
                "\t\t\t<div id=\"stat_leftcol_center\">\n" +
                "\t\t\t<div class=\"stat_date_my\"><img src=\"/images/rating_green.png\" style=\"margin:-3px 5px -3px 5px;\" />30.08.11</div><a href=\"Article.aspx?id=17\">Санаторий Истра - Жемчужина Подмосковья</a> <br/><font>\n" +
                "Недалеко от Ново-Иерусалимского монастыря, в окрестностях города Истры расположилась дворянская усадьба Покровское-Рубцово, которая принадлежала знаменитому промышленнику России Савве Тимофеевичу Морозову - основателю Богородско-Глуховской хлопчатобумажной мануфактуры в 19 веке.</font> </br></br><div class=\"stat_date_my\"><img src=\"/images/rating_green.png\" style=\"margin:-3px 5px -3px 5px;\" />29.08.11</div><a href=\"Article.aspx?id=16\">Незабываемый отдых в Тверской области</a> <br/><font>На берегах реки Медведица, которая протекает в Тверской области, среди пышного соснового леса расположился <a href=\"/Object.aspx?id=545\">дом отдыха Тетьково</a> – красивейший комплекс деревянных корпусов, созданных руками Троицких мастеров.</font> </br></br><div class=\"stat_date_my\"><img src=\"/images/rating_green.png\" style=\"margin:-3px 5px -3px 5px;\" />26.08.11</div><a href=\"Article.aspx?id=15\">Уголок для блаженства</a> <br/><font>В эпоху ускоренной городской жизни, в суете мегаполисов, в решении бесконечной вереницы проблем, нам так не хватает простого человеческого отдыха, спокойствия и умиротворения.</font> </br></br>\n" +
                "\t\t</div>\t\n" +
                "\t\t\n" +
                "\t\t<div id=\"stat_leftcol_bottom\"> \n" +
                "\t\t<img src=\"/images/rating_green.png\"/>&nbsp;\n" +
                "\t\t<a href=\"Article.aspx\">архив статей</a> \n" +
                "\t\t</div>\t\n" +
                "\t</div> \n" +
                "\t<!--конец колонки статьи-->\t\n" +
                "\t</td>\n" +
                '\n' +
                "    <td valign=\"top\">\n" +
                "    <!-- Центральный блок -->\n" +
                "    <h1 class=\"slogan1\">Мы работаем только по прямым ценам здравниц!</h1>\n" +
                "    <!--marquee><div id=\"content\"><h2>Дежурный круглосуточный номер 229-28-71</h2></div></marquee-->\n" +
                " \t<div id=\"main\">\n" +
                "    <div id=\"content\"></div>\n" +
                "    <div id=\"breadcrumbs\"><a href=\"Default.aspx\">Главная страница </a><font>\\<a href=\"SimpleMap.aspx?n=13\">Отдых в Подмосковье</a>\\<a href=\"SimpleMap.aspx?p=86\">Московская область</a>\\<a href=\"SimpleMap.aspx?r=144\">Запад</a>\\Пансионат Подмосковные Липки</font></div>\n" +
                "    \n" +
                "    <link rel=\"stylesheet\" type=\"text/css\" href=\"/css/scrollable.css\" />\n" +
                "    <link rel=\"stylesheet\" href=\"/js/jquery/plugin/colorbox/colorbox.css\" />\n" +
                "    <script type=\"text/javascript\" src=\"http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=ABQIAAAAlIDfCh2wKLB4iB4XQ4vCyhSIGqxFdlnFcvK1a31CEF9UQuANlhSAYbCjJ2Tu5RoiKzi9vTYJTX1wdg\"></script>\n" +
                "    <script type=\"text/javascript\" src=\"js/gmap.js\"></script>\n" +
                "    <!--script type=\"text/javascript\" src=\"http://cdn.jquerytools.org/1.2.7/all/jquery.tools.min.js\"></script-->\n" +
                "    <script type=\"text/javascript\" src=\"js/jquery/plugin/scrollable.js\"></script>\n" +
                "    <script type=\"text/javascript\" src=\"js/jquery/plugin/jquery.colorbox-min.js\"></script>\n" +
                "    <script type=\"text/javascript\" src=\"/js/ordercheck.js\"></script>\n" +
                "    <script type=\"text/javascript\">\n" +
                '\n' +
                "$(window).unload( function () { GUnload(); } );\n" +
                '\n' +
                '\n' +
                "function ShowDiv(divID, n,count) {\n" +
                "    var tab_inner = null;\n" +
                "    var tab_outer = null;\n" +
                "    var tab_href = null;\n" +
                "    var vis_tab = null;\n" +
                '\n' +
                "    for (var i = 1; i <= count; i++) {\n" +
                "        var elemID = \"tab\" + i.toString();\n" +
                "        var visibleTab = document.getElementById(elemID);\n" +
                "        if (visibleTab.style.display == \"\") {\n" +
                "            tab_inner = document.getElementById(\"tab_i\" + i);\n" +
                "            tab_outer = document.getElementById(\"tab_o\" + i);\n" +
                "            tab_inner.className = \"tab_dis_inner\";\n" +
                "            tab_outer.className = \"tab_dis_outer\";\n" +
                "            tab_href = document.getElementById(\"a_tab\" + i);\n" +
                "            tab_href.style.color = \"#FFFFFF\";\n" +
                "            visibleTab.style.display = \"none\";\n" +
                "            //visibleTD.style.backgroundColor = \"#FFFFFF\";\n" +
                "            break;\n" +
                "        }\n" +
                "    }\n" +
                '\n' +
                "    vis_tab = document.getElementById(divID);\n" +
                "    if(vis_tab != null) vis_tab.style.display = \"\";\n" +
                '\n' +
                "    tab_inner = document.getElementById(\"tab_i\" + n);\n" +
                "    if(tab_inner != null) tab_inner.className = \"tab_en_inner\";\n" +
                '\n' +
                "    tab_outer = document.getElementById(\"tab_o\" + n);\n" +
                "    tab_outer.className = \"tab_en_outer\";\n" +
                "    tab_href = document.getElementById(\"a_tab\" + n);\n" +
                "    tab_href.style.color = \"#666666\";\n" +
                "    document.cookie = \"tab=\" + n;\n" +
                '\n' +
                "    \n" +
                "    \n" +
                "    if (tab_href.innerHTML == \"Проезд\") initGmap(36.9489940,55.7646860);\n" +
                "    \n" +
                "    return false;\n" +
                "}\n" +
                "    </script>\n" +
                "    <script type=\"text/javascript\">\n" +
                '\n' +
                "    function SetDate(period) {\n" +
                "        var today = new Date();\n" +
                "        return today.getFullYear() + period;\n" +
                "    }\n" +
                '\n' +
                "    function resizeScrollPane()\n" +
                "    {\n" +
                "        $('div.#scroolPane').width($('div.#tab1').width());\n" +
                "        $('div.#scrollable').width($('div.#tab1').width() - 90);\n" +
                "    }\n" +
                "    \n" +
                "    $(document).ready(function() {\n" +
                "        $(\".scrollable\").scrollable({circular : true, size:1});\n" +
                "        //$('.items a').lightBox();\n" +
                "        $('#scrollable a').colorbox({photo:true});\n" +
                "        //resizeScrollPane();\n" +
                '\n' +
                "        window.onresize = function() {\n" +
                "            //resizeScrollPane();\n" +
                "        }\n" +
                "        \n" +
                "        //var d = [\"1\", \"2\", \"3\"]\n" +
                "        \n" +
                "        //восстанавливаю вкладку\n" +
                "\t\tvar obj = 56;\n" +
                "\t\tvar savedTab = 0;\n" +
                "\t\tvar savedObj = 0;\n" +
                "\t\tvar p = 0;\n" +
                "\t\tvar t = 0;\n" +
                "\t\tvar f = 0;\n" +
                "\t\tvar tabsId = [1,2,3,65,9,7,6];\n" +
                "\t\tvar totalTabs = 8;\n" +
                "\t\tif(p == 0)\n" +
                "\t\t{\n" +
                "\t\t\tif(f == 0)\n" +
                "\t\t\t{\n" +
                "\t\t\t\tif(t == 0)\n" +
                "\t\t\t\t{\n" +
                "\t\t\t\t\tarr = document.cookie.split(\"; \");\n" +
                "\t\t\t\t\tfor (var i = 0; i < arr.length; i++) {\n" +
                "\t\t\t\t\t\tval = arr[i].split(\"=\");\n" +
                "\t\t\t\t\t\tif (val[0] == \"tab\") {\n" +
                "\t\t\t\t\t\t\tsavedTab = val[1];\n" +
                "\t\t\t\t\t\t}\n" +
                "\t\t\t\t\t\tif (val[0] == \"obj\") {\n" +
                "\t\t\t\t\t\t\tsavedObj = val[1];\n" +
                "\t\t\t\t\t\t}\n" +
                "\t\t\t\t\t} //for(....)\n" +
                "\t\t\t\t\tif ((savedObj != 0) && (savedTab != 0)) {\n" +
                "\t\t\t\t\t\tif(savedObj == obj) {\n" +
                "                            if(savedTab <= totalTabs)\n" +
                "                            {\n" +
                "\t\t\t\t\t\t\t    ShowDiv(\"tab\"+savedTab,savedTab,totalTabs);\n" +
                "                            }\n" +
                "                            else\n" +
                "                            {\n" +
                "                                ShowDiv(\"tab1\",1,totalTabs);\n" +
                "                            }\n" +
                "\t\t\t\t\t\t}\n" +
                "\t\t\t\t\t}\n" +
                "\t\t\t\t\telse\n" +
                "\t\t\t\t\t{\n" +
                "\t\t\t\t\t\tShowDiv(\"tab1\",1,totalTabs);\n" +
                "\t\t\t\t\t}\n" +
                "\t\t\t\t}\n" +
                "\t\t\t\telse\n" +
                "\t\t\t\t{\n" +
                "\t\t\t\t\tif(t <= totalTabs){\n" +
                "\t\t\t\t\t\tShowDiv(\"tab\"+t,t,totalTabs);\n" +
                "\t\t\t\t\t}\n" +
                "\t\t\t\t\telse\n" +
                "\t\t\t\t\t{\n" +
                "\t\t\t\t\t\tShowDiv(\"tab1\",1,totalTabs);\n" +
                "\t\t\t\t\t}\n" +
                "\t\t\t\t}\n" +
                "\t\t\t}\n" +
                "\t\t\telse\n" +
                "\t\t\t{\n" +
                "\t\t\t\tShowDiv(\"tab\"+tabsId.length+1,tabsId.length+1,totalTabs);\n" +
                "\t\t\t}\n" +
                "\t\t}//if(p==0)\n" +
                "\t\telse\n" +
                "\t\t{\n" +
                "\t\t\t//p - это какая вкладка?\n" +
                "\t\t\tfor(var i=0;i<totalTabs;i++)\n" +
                "\t\t\t\tif(tabsId[i] == p) break;\n" +
                "\t\t\ti++;\n" +
                "\t\t\tShowDiv(\"tab\"+i,i,totalTabs);\n" +
                "\t\t}\n" +
                "        if(savedObj == 0 || savedObj != obj)\n" +
                "            document.cookie = \"obj=\" + obj;\n" +
                "    });\n" +
                "    \n" +
                "        //для фоток    \n" +
                "        var fotoIndex = 0;\n" +
                "        var fotoArray = [];\n" +
                "        var visFoto = [];\n" +
                "        var fotoTitle = [];\n" +
                "        var startIndex = 0;\n" +
                "        var endIndex = 0;\n" +
                "        \n" +
                "    function updateCode() {\n" +
                "        var td = document.getElementById(\"capchaImage\");\n" +
                "        td.innerHTML = \"<img width=120 height=54 src=\\\"Capcha.aspx?\" + Math.random() + \"\\\" />\";\n" +
                "    }\n" +
                "    </script>\n" +
                "    <div id=\"content\">\n" +
                "        <!--div>Исключение возникло:28 августа 2012 г., at 14:43<br/>\n" +
                '\n' +
                '\n' +
                "Местоположение страницы: /Object.aspx?id=788<br/>\n" +
                '\n' +
                '\n' +
                "IP адрес клиента: 94.241.62.201<br/>\n" +
                '\n' +
                '\n' +
                "Сообщение: Thread was being aborted.<br/>\n" +
                '\n' +
                '\n' +
                "Источник: mscorlib<br/>\n" +
                '\n' +
                '\n' +
                "Метод: Void AbortInternal()<br/>\n" +
                '\n' +
                '\n' +
                "Трасса стека:    at System.Threading.Thread.AbortInternal()\n" +
                "   at System.Threading.Thread.Abort(Object stateInfo)\n" +
                "   at System.Web.HttpResponse.End()\n" +
                "   at System.Web.HttpServerUtility.Transfer(String path)\n" +
                "   at Protey.Object.Page_Load(Object sender, EventArgs e)<br/>\n" +
                '\n' +
                '\n' +
                "Строка: 7<br/>\n" +
                "Thread was being aborted. in Page_Load()<br/>\n" +
                "</div-->\n" +
                "        \n" +
                "        <div class=\"tab_menu_container\">\n" +
                "            <h1>\n" +
                "                Пансионат Подмосковные Липки</h1>\n" +
                "            <ul id=\"tab_menu\">\n" +
                "                <li><div id=\"tab_o1\" class=\"tab_en_outer\"><div id=\"tab_i1\" tab:id=\"1\" class=\"tab_en_inner\"><a id=\"a_tab1\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#666666; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab1','1','8');\">Описание</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o2\" class=\"tab_dis_outer\"><div id=\"tab_i2\" tab:id=\"2\" class=\"tab_dis_inner\"><a id=\"a_tab2\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab2','2','8');\">Номерной фонд</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o3\" class=\"tab_dis_outer\"><div id=\"tab_i3\" tab:id=\"3\" class=\"tab_dis_inner\"><a id=\"a_tab3\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab3','3','8');\">Инфраструктура</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o4\" class=\"tab_dis_outer\"><div id=\"tab_i4\" tab:id=\"65\" class=\"tab_dis_inner\"><a id=\"a_tab4\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab4','4','8');\">SPA услуги</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o5\" class=\"tab_dis_outer\"><div id=\"tab_i5\" tab:id=\"9\" class=\"tab_dis_inner\"><a id=\"a_tab5\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab5','5','8');\">Стоимость за номер в сутки (руб.)</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o6\" class=\"tab_dis_outer\"><div id=\"tab_i6\" tab:id=\"7\" class=\"tab_dis_inner\"><a id=\"a_tab6\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab6','6','8');\">Примечания</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o7\" class=\"tab_dis_outer\"><div id=\"tab_i7\" tab:id=\"6\" class=\"tab_dis_inner\"><a id=\"a_tab7\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab7','7','8');\">Проезд</a></div></div></li>\n" +
                '\n' +
                "<li><div id=\"tab_o8\" class=\"tab_dis_outer\"><div id=\"tab_i8\" tab:id=\"-4\" class=\"tab_dis_inner\"><a id=\"a_tab8\" style=\"font-family:Tahoma, Verdana, Arial, Helvetica, sans-serif; font-size:12px; color:#FFFFFF; text-decoration:none;\" href=\"#\" onclick=\"return ShowDiv('tab8','8','8');\">Бронирование</a></div></div></li>\n" +
                '\n' +
                '\n' +
                "            </ul>\n" +
                "        </div>\n" +
                "        \t<div class=\"tab_content\" id=\"tab1\" style=\"\"><h2>Описание</h2>\n" +
                "<div style=\"margin:0 auto; width: 93%; height:90px;\" id=\"scroolPane\">\n" +
                "<!-- \"previous page\" action -->\n" +
                "<a class=\"prev browse left\"></a>\n" +
                "<div id=\"scrollable\" class=\"scrollable\" style=\"width:93%\"><div class=\"items\">\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=11511\" rel=\"lightbox\" title=\"Пансионат \"Липки\"\"><img src=\"GetThumb.ashx?id=11511\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1105\" rel=\"lightbox\" title=\"Корпус\"><img src=\"GetThumb.ashx?id=1105\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=11512\" rel=\"lightbox\" title=\"Главный вход\"><img src=\"GetThumb.ashx?id=11512\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1110\" rel=\"lightbox\" title=\"Общий вид\"><img src=\"GetThumb.ashx?id=1110\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5713\" rel=\"lightbox\" title=\"Бар «Зимний Сад»\"><img src=\"GetThumb.ashx?id=5713\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1109\" rel=\"lightbox\" title=\"Бар «Зимний Сад»\"><img src=\"GetThumb.ashx?id=1109\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5708\" rel=\"lightbox\" title=\"Ресторан «Лепота»\"><img src=\"GetThumb.ashx?id=5708\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5709\" rel=\"lightbox\" title=\"Ресторан «Лепота»\"><img src=\"GetThumb.ashx?id=5709\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1107\" rel=\"lightbox\" title=\"Бассейн 25 м\"><img src=\"GetThumb.ashx?id=1107\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1127\" rel=\"lightbox\" title=\"Спортзал\"><img src=\"GetThumb.ashx?id=1127\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5714\" rel=\"lightbox\" title=\"Теннисный корт\"><img src=\"GetThumb.ashx?id=5714\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5715\" rel=\"lightbox\" title=\"Волейбольная площадка\"><img src=\"GetThumb.ashx?id=5715\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5711\" rel=\"lightbox\" title=\"Ресторан «На Костровой»\"><img src=\"GetThumb.ashx?id=5711\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5710\" rel=\"lightbox\" title=\"Ресторан «На Костровой»\"><img src=\"GetThumb.ashx?id=5710\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5712\" rel=\"lightbox\" title=\"Ресторан «На Костровой»\"><img src=\"GetThumb.ashx?id=5712\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1113\" rel=\"lightbox\" title=\"Столовая\"><img src=\"GetThumb.ashx?id=1113\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5703\" rel=\"lightbox\" title=\"Коттедж\"><img src=\"GetThumb.ashx?id=5703\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5704\" rel=\"lightbox\" title=\"Коттедж\"><img src=\"GetThumb.ashx?id=5704\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5705\" rel=\"lightbox\" title=\"Коттедж\"><img src=\"GetThumb.ashx?id=5705\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1131\" rel=\"lightbox\" title=\"1-местный номер\"><img src=\"GetThumb.ashx?id=1131\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5706\" rel=\"lightbox\" title=\"Коттедж\"><img src=\"GetThumb.ashx?id=5706\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5707\" rel=\"lightbox\" title=\"Коттедж\"><img src=\"GetThumb.ashx?id=5707\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1130\" rel=\"lightbox\" title=\"2-местный \"Стандарт\"\"><img src=\"GetThumb.ashx?id=1130\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1111\" rel=\"lightbox\" title=\"2-комнатный \"Евролюкс\"\"><img src=\"GetThumb.ashx?id=1111\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1118\" rel=\"lightbox\" title=\"2-комнатный \"Евролюкс\"\"><img src=\"GetThumb.ashx?id=1118\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1112\" rel=\"lightbox\" title=\"2-комнатный \"Евролюкс\"\"><img src=\"GetThumb.ashx?id=1112\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1120\" rel=\"lightbox\" title=\"2-комнатный \"Евролюкс\"\"><img src=\"GetThumb.ashx?id=1120\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1119\" rel=\"lightbox\" title=\"2-комнатный \"Люкс\"\"><img src=\"GetThumb.ashx?id=1119\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1121\" rel=\"lightbox\" title=\"2-комнатный \"Люкс\"\"><img src=\"GetThumb.ashx?id=1121\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1126\" rel=\"lightbox\" title=\"2-комнатный \"Люкс\"\"><img src=\"GetThumb.ashx?id=1126\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1108\" rel=\"lightbox\" title=\"2-комнатный \"Люкс\"\"><img src=\"GetThumb.ashx?id=1108\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1128\" rel=\"lightbox\" title=\"2-комнатный \"Люкс\"\"><img src=\"GetThumb.ashx?id=1128\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1122\" rel=\"lightbox\" title=\"2-местный \"Эконом\"\"><img src=\"GetThumb.ashx?id=1122\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1123\" rel=\"lightbox\" title=\"2-местный \"Эконом\"\"><img src=\"GetThumb.ashx?id=1123\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=1125\" rel=\"lightbox\" title=\"2-комнатный \"Полулюкс\"\"><img src=\"GetThumb.ashx?id=1125\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5716\" rel=\"lightbox\" title=\"Аудитория №2 (80 человек)\"><img src=\"GetThumb.ashx?id=5716\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5717\" rel=\"lightbox\" title=\"Аудитория №3\"><img src=\"GetThumb.ashx?id=5717\"/></a>\n" +
                "</div>\n" +
                "<div>\n" +
                "<a href=\"ShowImg.aspx?id=5718\" rel=\"lightbox\" title=\"Большой холл (конференц-зал)\"><img src=\"GetThumb.ashx?id=5718\"/></a>\n" +
                "</div></div>\n" +
                "</div>\n" +
                "<!-- \"next page\" action -->\n" +
                "<a class=\"next browse right\"></a>\n" +
                "</div><div  align=\"justify\">\n" +
                "<p><strong>Пансионат «Подмосковные Липки»</strong> расположен в Подмосковье. По отзывам - отличный дом отдыха! В чем его отличие от других? В особой атмосфере, которая создана персоналом и администрацией пансионата. База отдыха «Подмосковные Липки» действительно особая. Здесь особо радушный прием, и особые впечатления от отдыха. Небольшая удаленность от Москвы (35 км) позволяет любому желающему с пользой для себя и своего здоровья провести в культурно-оздоровительном пансионате Липки выходные или праздничные дни. Вы до сих пор ломаете голову над тем, где можно отдохнуть всей семьей, где будет одинаково весело и комфортно детям и взрослым? Обратите свое внимание на пансионат и базу отдыха «Подмосковные Липки», который круглый год принимает посетителей и дарит полноценный отдых.&nbsp;</p>\n" +
                "<p>В выборе места для отдыха решающее значение имеет не столько внешний вид территории и самого пансионата «Липки», фото которого представлено на нашем сайте, сколько те услуги, которые вы сможете получить в <strong>пансионате «Подмосковные Липки»</strong> за умеренные цены.</p>\n" +
                "<p>Качество обслуживания в пансионате выше всяких похвал, а возможностей для увлекательного отдыха - хоть отбавляй. Отдыхайте в баре или на танцевальной площадке, поддерживайте физическую форму на теннисном корте или в тренажерном зале, заводите новые знакомства в бильярдном зале или на катке. Встряхнитесь, наконец, и добавьте адреналина, скатившись с ледяной горы или сыграв в пейнтбол. Сотрудники пансионата предложат вам еще массу других развлечений и присмотрят за детьми, пока вы будете наслаждаться отдыхом.</p>\n" +
                "<p>Стоит заметить, что<strong> пансионат «Подмосковные Липки»</strong> в Московской области не потеряется среди множества других заведений, оказывающих подобные услуги, благодаря особенности своего персонала: умению создавать комфортные условия для отдыха. Решили ехать? Схема проезда к подмосковному пансионату «Липки» и вся представленная у нас информация, в том числе и телефоны, взята с сайта пансионата и полностью достоверна. Взяв путевку, вы сможете убедиться сами в том, что пансионат «Подмосковные Липки» заслуживает тех восторженных отзывов, которые о нем оставляют.</p>\n" +
                "</div>\n" +
                "</div>\n" +
                '\n' +
                "\t<div class=\"tab_content\" id=\"tab2\" style=\"display:none;\"><h2>Номерной фонд</h2>\n" +
                "<p><b>Корпус Основной </b></p>\n" +
                "<ul>\n" +
                "\t<li>1-местный 1-комнатный </li>\n" +
                "\t<li>2-местный 1-комнатный «Эконом» </li>\n" +
                "\t<li>2-местный 1-комнатный «Бюджет» </li>\n" +
                "\t<li>3-местный 1-комнатный «Семейный» </li>\n" +
                "\t<li>2-местный 1-комнатный «Стандарт» </li>\n" +
                "\t<li>2-местный 2-комнатный «Полулюкс» </li>\n" +
                "\t<li>2-местный 2-комнатный «Люкс» </li>\n" +
                "\t<li>2-местный 2-комнатный «Евролюкс» </li>\n" +
                "</ul>\n" +
                "<p><b>Коттедж № 1,2,3,4 </b></p>\n" +
                "<ul>\n" +
                "\t<li>Коттедж на 4 человека</li>\n" +
                "</ul>\n" +
                "<p><b>Коттедж № 5 </b></p>\n" +
                "<ul>\n" +
                "\t<li>Коттедж на 15 человек</li>\n" +
                "</ul>\n" +
                " \n" +
                "</div>\n" +
                '\n' +
                "\t<div class=\"tab_content\" id=\"tab3\" style=\"display:none;\"><h2>Инфраструктура</h2>\n" +
                "<p><b>Восстановительный отдых:</b></p>\n" +
                "<ul>\n" +
                "\t<li>комплекс VIP-саун  на 10 мест с выходом в большой бассейн (турецкая баня, финская сауна, инфракрасная кабина, джакузи, мини-бассейн, фито-бар, 2 комнаты отдыха с баром, двумя ТВ, видео, музыкальным центром, холодильником и фенами)</li>\n" +
                "\t<li>зона отдыха с фонтанами </li>\n" +
                "\t<li>зимний сад </li>\n" +
                "</ul>\n" +
                "<p><b>Активный отдых:</b></p>\n" +
                "<ul>\n" +
                "\t<li>закрытый бассейн (25 метров, 4 дорожки, с противотоком, гейзером и джакузи)</li>\n" +
                "\t<li>тренажерный зал </li>\n" +
                "\t<li>открытая волейбольная площадка </li>\n" +
                "\t<li>2 открытых теннисных корта </li>\n" +
                "\t<li>спортивный зал площадь 475 кв.м </li>\n" +
                "\t<li>прокат спортинвентаря </li>\n" +
                "\t<li>пейнтбол </li>\n" +
                "\t<li>конный прокат (верховая езда и прогулки в фаэтоне) </li>\n" +
                "\t<li>дайвинг </li>\n";
               String s2 = "\t<li>открытая баскетбольная площадка </li>\n" +
                "\t<li>оборудованное футбольное поле с трибунами </li>\n" +
                "</ul>\n" +
                "<p><b>Корпоративные мероприятия:</b></p>\n" +
                "<ul>\n" +
                "\t<li>площадка для проведения выставок 400 м2 </li>\n" +
                "\t<li>конференц-зал  на 350 мест</li>\n" +
                "\t<li>аудитории для занятий и переговоров от 15 до 80 человек </li>\n" +
                "\t<li>2 банкетных зала </li>\n" +
                "\t<li>организация кофе-брейков, банкетов, фуршетов и т.п. </li>\n" +
                "</ul>\n" +
                "<p><b>Досуг и развлечения:</b></p>\n" +
                "<ul>\n" +
                "\t<li>развлекательные и шоу-программы </li>\n" +
                "\t<li>диско-бар  на 110 мест</li>\n" +
                "\t<li>ресторан </li>\n" +
                "\t<li>летнее кафе на воде </li>\n" +
                "\t<li>площадка для костра </li>\n" +
                "\t<li>VIP-ресторан «Лепота»  на 70 мест</li>\n" +
                "\t<li>организация экскурсий </li>\n" +
                "\t<li>бар-шашлык </li>\n" +
                "\t<li>рыбалка </li>\n" +
                "\t<li>караоке </li>\n" +
                "\t<li>настольный теннис </li>\n" +
                "\t<li>игровые автоматы </li>\n" +
                "</ul>\n" +
                "<p><b>Детский отдых:</b></p>\n" +
                "<ul>\n" +
                "\t<li>детский бассейн с дополнительным подогревом </li>\n" +
                "\t<li>детская игровая площадка </li>\n" +
                "\t<li>детская игровая комната с воспитателем  </li>\n" +
                "</ul>\n" +
                "<p><b>Прочие услуги:</b></p>\n" +
                "<ul>\n" +
                "\t<li>бесплатная охраняемая автостоянка </li>\n" +
                "</ul>\n" +
                "</div>\n" +
                       '\n' +
                "\t<div class=\"tab_content\" id=\"tab4\" style=\"display:none;\"><h2>SPA услуги</h2>\n" +
                "<ul>\n" +
                "<li>Три финские сауны(на 2,4 и 6 мест) с выходом в бассейн.</li>\n" +
                "<li>Vip- комплекс, включающий сауну на 10 мест с выходом в большой бассейн, джакузи, турецкая баня, инфракрасная кабина, 2 комфортабельные комнаты отдыха.</li>\n" +
                "<li>Кабинет релаксации, где вам предложат массаж классический, медовый, антицеллюлитный, оздоравливающюю экспресс-мини- баню «Кедровая бочка»- «искупаешься» в целебном пару и как заново на свет родился.</li>\n" +
                "<li>В приятной и уютной атмосфере чайной комнаты вы  можете отдохнуть и расслабиться после оздоровительных, массажных и банных процедур. Вам предложат травяной душистый чай с цветами алое, а также вы можете заказать различные чаи и напитки.</li>\n" +
                "<li>Квалифицированный косметолог предложит Вам свои услуги по уходу за кожей лица, шеи, области декольте и рук, косметологический массаж, антицеллюлитная программа «Водоросли»,шоколадное обертывание, морские ванны для детей и взрослым.</li>\n" +
                       '\n' +
                "</ul>\n" +
                       '\n' +
                       '\n' +
                       '\n' +
                "</div>\n" +
                       '\n' +
                "\t<div class=\"tab_content\" id=\"tab5\" style=\"display:none;\"><h2>Стоимость за номер в сутки (руб.)</h2>\n" +
                "<h1>Гарантированные места!!!с 1 сентября по 31 мая 2013 года</h1>\n" +
                "<table width=\"100%\" border=\"1\" cellspacing=\"2\" cellpadding=\"0\" rules=\"all\"><tr><td rowspan=\"2\" id=\"table_header\">Категория номера</td><td colspan=\"2\" id=\"table_header\">01.09 - 31.05</td></tr><tr><td id=\"table_header\">Будни</td><td id=\"table_header\">Выходные и праздники</td></tr><tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>Корпус Основной </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>2-местный 1-комнатный «Стандарт» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3600</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3800</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3000</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>2-местный 2-комнатный «Евролюкс» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">5000</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">5200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4200</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4600</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>2-местный 1-комнатный «Эконом» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3000</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2400</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2600</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>1-местный 1-комнатный </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2300</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2400</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>2-местный 2-комнатный «Полулюкс» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4200</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4400</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3600</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3800</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>2-местный 2-комнатный «Люкс» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4600</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4800</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4000</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>3-местный 1-комнатный «Семейный» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3900</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3200</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3400</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>Коттедж № 5 </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"3\" ><b>Коттедж на 15 человек</b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">15-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">27000</td><td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">30000</td></tr>\n" +
                "</table><h1>Гарантированные места на лето!!! Цены действительны с 1 июня по 31 августа 2012 года</h1>\n" +
                "<table width=\"100%\" border=\"1\" cellspacing=\"2\" cellpadding=\"0\" rules=\"all\"><tr><td id=\"table_header\">Категория номера</td><td id=\"table_header\">Стоимость</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>Корпус Основной </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>2-местный 1-комнатный «Стандарт» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4000</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3300</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>2-местный 2-комнатный «Евролюкс» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">5400</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4800</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>2-местный 1-комнатный «Эконом» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3400</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2800</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>1-местный 1-комнатный </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2500</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>2-местный 2-комнатный «Полулюкс» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4600</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>2-местный 2-комнатный «Люкс» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">5000</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4400</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>3-местный 1-комнатный «Семейный» </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">2-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">4200</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">1-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">3500</td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>Коттедж № 5 </b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\" colspan=\"2\" ><b>Коттедж на 15 человек</b></td></tr>\n" +
                "<tr><td id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">15-местное размещение</td>\n" +
                "<td style=\"text-align:center\" id=\"table_content\" class=\"table_bg_summer1 table_left_border_summer\">33000</td></tr>\n" +
                "</table><div  align=\"justify\">\n" +
                       '\n' +
                "<p><b>В стоимость входит:</b> проживание в номере выбранной категории, 3-разовое питание «шведский стол», посещение бассейна (с 08:00 до 22:00), детской комнаты, тренажерного зала (с 11.00 до 12.00 и с 16.00 до 17.00), парковка, дискотека - пятница суббота с 23.00 до 01.00.</p>\n" +
                       '\n' +
                "</div>\n" +
                "</div>\n" +
                       '\n' +
                "\t<div class=\"tab_content\" id=\"tab6\" style=\"display:none;\"><h2>Примечания</h2>\n" +
                "<div  align=\"justify\">\n" +
                       '\n' +
                "<ul>\n" +
                "<li>Расчётный час: заезд с 17:00, выезд до 15:00</li>\n" +
                "<li>Возможен заезд с 9:00 утра - завтрак, выезд - 7:00; заезд с 13:00 -обед, выезд 11-00 дня.</li>\n" +
                "<li>Заезд в выходные не менее 2 суток</li>\n" +
                "<li>Будни: воскресенье - пятница/ Выходные:пятница - воскресенье.</li>\n" +
                "<li>Дети принимаются с любого возраста</li>\n" +
                "<li>Дополнительное место в номере: раскладушка.</li>\n" +
                "<li>Детская кроватка - 300 руб/сут.</li>\n" +
                "<li>Ребенок до 3-х лет без дополнительного места и без питания – бесплатно. Детская кроватка – 300 руб./сутки.</li>\n" +
                "<li>Заезд ранее определённого часа и выезд позже расчётного часа оплачивается в размере 100% от стоимости проживания в сутки. Досрочный выезд не компенсируется.</li>\n" +
                "<li>Гости с животными не принимаются.</li>\n" +
                "<li>Категорически запрещён ввоз на территорию пансионата продуктов питания и напитков.</li>\n" +
                       '\n' +
                "</ul>\n" +
                "<p>Режим питания</p>\n" +
                "<ul>\n" +
                "<li>Завтрак с 08:45 до 11:00</li>\n" +
                "<li>Обед с 13:00 до 14:30</li>\n" +
                "<li>Ужин с 18:00 до 19:30</li>\n" +
                "</ul>\n" +
                       '\n' +
                "</div></div>\n" +
                       '\n' +
                "\t<div class=\"tab_content\" id=\"tab7\" style=\"display:none;\"><h2>Проезд</h2>\n" +
                "<div  align=\"justify\">\n" +
                       '\n' +
                "<p><b>На общественном траспорте:</b></p>\n" +
                "<ul>\n" +
                "<li><b>электропоездом</b> от Белорусского вокзала до станции \"Звенигород\", далее автобусом № 25, № 11 до г. Звенигорода, далее автобусом № 452 или № 54 до д. Синьково, далее по указателю пансионат «Липки» пешком 500 м. От станции \"Звенигород\" до пансионата \"Липки\" ежедневно отправлятся в 17:45 служебный автотранспорт (для пассажиров электропоезда уходящего с Белорусского вокзала в 16:08). Служебный автотранспорт пансионата: ГАЗель госномер р436мх, ГАЗель госномер -в556ав.</li>\n" +
                "<li><b>автобусом</b> №452 от станции метро Кунцевская (последний вагон из центра, выход на улицу направо) автобус «Экспресс» Кунцево-Звенигород. Ехать до остановки д. Синьково, далее по указателю пансионат «Липки» пешком 500 м. </li>\n" +
                "</ul>\n" +
                       '\n' +
                "<p><b>На автомобиле:</b></p>\n" +
                "<ul>\n" +
                "<li><b>по Новорижскому шоссе</b> поворот на г. Звенигород, возле автозаправочной станции «BP» повернуть налево. Далее ехать до указателя пансионат «Липки» – поворот налево.</li>\n" +
                "<li><b>по Рублево-Успенскому шоссе</b> поворот на Николину гору, далее прямо через деревни Ивановка, Аксиньино, Козино, Грязь до деревни Синьково, по указателю «Пансионат «Липки» 500 метров.</li>\n" +
                "</ul>\n" +
                       '\n' +
                "<p><b>Адрес:</b> Московская область, Одинцовский район, Аксининская сельская администрация, д. Липки.</p>\n" +
                       '\n' +
                "</div>\n" +
                       '\n' +
                       '\n' +
                       '\n' +
                "<div align=\"center\"><div id=\"mapgoogle\" style=\"width: 394px; height: 295px;\"></div></div>\n" +
                "</div>\n" +
                       '\n' +
                       '\n' +
                "        \n" +
                "        \n" +
                "        <div class=\"tab_content\" id=\"tab8\" style=\"display: none;\">\n" +
                "            \n" +
                "        <form action=\"Object.aspx\" method=\"post\" name=\"orderForm\" id=\"orderForm\" enctype=\"multipart/form-data\">\n" +
                "            \n" +
                "            <table width=\"100%\">\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Дата заезда:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"date1\" id=\"date1\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"date1_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Время заезда:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <select name=\"time1\" id=\"time1\" value=\"\">\n" +
                "                            <option value=\"0\">завтрак</option>\n" +
                "                            <option value=\"1\">обед</option>\n" +
                "                            <option value=\"2\">ужин</option>\n" +
                "                        </select>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"time1_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Дата отъезда:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"date2\" id=\"date2\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"date2_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Время отъезда:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <select name=\"time2\" id=\"time2\">\n" +
                "                            <option value=\"0\">завтрак</option>\n" +
                "                            <option value=\"1\">обед</option>\n" +
                "                            <option value=\"2\">ужин</option>\n" +
                "                        </select>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"time2_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Категория номера:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"room\" id=\"room\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"room_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Количество взрослых:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"adult_qty\" id=\"adult_qty\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"adult_qty_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Количество детей:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"child_qty\" id=\"child_qty\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"child_qty_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Возраст детей:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"child_age\" id=\"child_age\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"child_age_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            ФИО:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"fio\" id=\"fio\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"fio_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            Контактный телефон:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"tel\" id=\"tel\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"tel_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td>\n" +
                "                        <p>\n" +
                "                            e-mail:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <input type=\"text\" name=\"email\" id=\"email\" value=\"\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p id=\"email_error\">\n" +
                "                        </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td valign=\"top\">\n" +
                "                        <p>\n" +
                "                            Примечание:</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <textarea rows=\"5\" name=\"notes\"></textarea>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td valign=\"bottom\">\n" +
                "                        <p>\n" +
                "                            Чему равно</p>\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <div id=\"capchaImage\">\n" +
                "                            <img src=\"Capcha.aspx?id=3281fed2-cfb4-4604-9664-7c1c004b74b3\" alt=\"Включите отображение картинок\" width=\"120\" height=\"54\" /></div>\n" +
                "                        <!--br/-->\n" +
                "                        <a href=\"#\" style=\"vertical-align: middle; display: inline\" onclick=\"updateCode();return false;\">\n" +
                "                            не вижу цифры</a><br />\n" +
                "                        <input type=\"text\" size=\"40\" name=\"code\" id=\"code\" style=\"vertical-align: bottom\" />\n" +
                "                    </td>\n" +
                "                    <td>\n" +
                "                        <p class=\"error_mes\" id=\"code_error\">\n" +
                "                            </p>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "                <tr>\n" +
                "                    <td colspan=\"3\" align=\"center\">\n" +
                "                        <input type=\"submit\" value=\"Отправить заказ\" />\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "            </table>\n" +
                "            <input type=\"hidden\" name=\"oid\" value=\"56\" />\n" +
                "            <input type=\"hidden\" name=\"order_form\" value=\"true\" />\n" +
                "            \n" +
                "        </form>\n" +
                       '\n' +
                "        </div>\n" +
                "        <p>\n" +
                "            </p>\n" +
                "        \n" +
                "        <div style=\"height: 30px; padding-bottom: 10px; margin-left: 30px; min-width: 300px;\n" +
                "            owerflow-x: hidden;\">\n" +
                "            <!-- ВКОНТАКТЕ -->\n" +
                "            <div style=\"float: left\">\n" +
                "                <div id=\"vk_like\" style=\"float: left\">\n" +
                "                </div>\n" +
                "                <script type=\"text/javascript\">\n" +
                "                    VK.Widgets.Like(\"vk_like\", { type: \"button\" });\n" +
                "                </script>\n" +
                "            </div>\n" +
                "            <!-- FACEBOOK -->\n" +
                "            <div style=\"float: left; margin-top: 2px; margin-left: -25px; margin-right: -25px;\">\n" +
                "                <div id=\"fb-root\">\n" +
                "                </div>\n" +
                "                <script>                    (function (d) {\n" +
                "                        var js, id = 'facebook-jssdk'; if (d.getElementById(id)) { return; }\n" +
                "                        js = d.createElement('script'); js.id = id; js.async = true;\n" +
                "                        js.src = \"//connect.facebook.net/en_US/all.js#appId=150304138394750&xfbml=1\";\n" +
                "                        d.getElementsByTagName('head')[0].appendChild(js);\n" +
                "                    } (document));</script>\n" +
                "                <div class=\"fb-like\" data-send=\"true\" data-layout=\"button_count\" data-width=\"80\"\n" +
                "                    data-show-faces=\"true\">\n" +
                "                </div>\n" +
                "            </div>\n" +
                "            <!-- GOOGLE -->\n" +
                "            <div style=\"float: left;\">\n" +
                "                <g:plusone></g:plusone>\n" +
                "            </div>\n" +
                "            <!-- TWITTER -->\n" +
                "            <div style=\"float: left; margin-left: -20px; margin-top: 2px;\">\n" +
                "                <a href=\"http://twitter.com/share\" class=\"twitter-share-button\" data-count=\"horizontal\">\n" +
                "                    Tweet</a><script type=\"text/javascript\" src=\"http://platform.twitter.com/widgets.js\"></script>\n" +
                "            </div>\n" +
                "            <!-- MAIL.RU -->\n" +
                "            <div style=\"float: left;\">\n" +
                "                <a target=\"_blank\" class=\"mrc__plugin_uber_like_button\" href=\"http://connect.mail.ru/share\"\n" +
                "                    data-mrc-config=\"{'type' : 'small', 'caption-mm' : '1', 'caption-ok' : '2', 'counter' : 'true', 'width' : '300', 'nt' : '1'}\">\n" +
                "                    Нравится</a>\n" +
                "                <script src=\"http://cdn.connect.mail.ru/js/loader.js\" type=\"text/javascript\" charset=\"UTF-8\"></script>\n" +
                "            </div>\n" +
                "        </div>\n" +
                "        <!-- Time:0,8125-->\n" +
                "    </div>\n" +
                       '\n' +
                "\t<div id=\"foots\"></div>\n" +
                "\t</div>\n" +
                "\t</td>\n" +
                "\t\n" +
                "\t<td align=\"left\" valign=\"top\" width=\"223\">\n" +
                "    <!-- Третья колонка -->\n" +
                       '\n' +
                "<!-- О компании-->\n" +
                "<div id=\"frameright\">\n" +
                "<div class=\"rightline\" style=\"height:280px;\"></div>\n" +
                "<div class=\"cornert\">\n" +
                "<div class=\"corner\" id=\"cornerlt\"></div>\n" +
                "<div class=\"corner\" id=\"cornerrt\"></div>\n" +
                "</div>\n" +
                "<!--font style=\"color:#409f0f;\">О компании</font-->\n" +
                "<img src=\"/images/autumn_day/companylogo.png\" width=\"200\"/>\n" +
                "<div align=\"center\" style=\"margin:10px 0px 0px 0px; color:#409f0f;\">\n" +
                "<font class=\"ci5\"> +7(495) 229 28 71</font>\n" +
                "</div>\n" +
                "<div style=\"margin:5px 0px 0px 60px; color:#5B5335; font-family:Arial, Helvetica, sans-serif;\" ><b>\n" +
                "<img src=\"/images/skype.png\" width=\"20\" height=\"20\" />&nbsp;ptravel2001<br />\n" +
                "<img src=\"/images/icq.png\" width=\"20\" height=\"20\" />&nbsp;342011968<br />\n" +
                "</b>\n" +
                "</div>\n" +
                "<div style=\"margin:10px 8px 5px 15px;\" align=\"center\">\n" +
                "<p style=\"font-size:11px; font-family:Arial, Helvetica, sans-serif; color:#000;\">\n" +
                "г. Москва, ул. Никольская, д.17, стр.2, <br />\n" +
                "Деловой центр \"Славянский\", <br />3 этаж, офис № 3.3. <br />\n" +
                "<b>м.</b> Лубянка, Площадь<br /> \n" +
                "Революции, Театральная,  <br />\n" +
                "Охотный ряд</p>\n" +
                "</div>\n" +
                "<div style=\"margin:0px 20px 0px 20px;\"><a target=\"_blank\" class=\"about_link\" style=\"padding-left:0px;\" href=\"http://reestr.russiatourism.ru/?ac=view&id_reestr=2242\">Реестровый номер туроператора МВТ №007404</a></div>\n" +
                "<div class=\"cornerb\">\n" +
                "<div class=\"corner\" id=\"cornerlb\"></div>\n" +
                "<div class=\"corner\" id=\"cornerrb\"></div>\n" +
                "</div>\n" +
                "</div><br />\n" +
                       '\n' +
                "<div class=\"spacerl_1\"><div class=\"spacerl_2\"></div></div>    \n" +
                       '\n' +
                       '\n' +
                " <div style=\"background:url(/images/winter/fr.png) right repeat-y; width:240px; margin-top:10px;\">\n" +
                "<div class=\"leftline\" style=\"height:85px;\"></div>\n" +
                "<div class=\"cornert\">\n" +
                "<div class=\"corner\" id=\"cornerlt\"></div>\n" +
                "<div class=\"corner\" id=\"cornerrt\"></div>\n" +
                "</div>\n" +
                "\t<div style=\"padding-left:20px\" >\n" +
                       '\n' +
                "\t<font style=\"font-family:Arial, Helvetica, sans-serif; font-size:16px; font-weight: bold; color:#409f0f\">Online-бронирование</font> \n" +
                "    <div id=\"content\">\n" +
                "    <p>Бронирование осуществляется со страницы здравницы или отеля на вкладке &laquo;Бронирование&raquo;.</p>\n" +
                "    </div>\n" +
                "\t</div>\n" +
                "\t<div class=\"cornerb\">\n" +
                "<div class=\"corner\" id=\"cornerlb\"></div>\n" +
                "<div class=\"corner\" id=\"cornerrb\"></div></div></div><br/>\n" +
                       '\n' +
                "    \n" +
                "\t\n" +
                "<div class=\"spacerl_1\"><div class=\"spacerl_2\"></div></div>\n" +
                "<div>\n" +
                "<img src=\"/images/rating_light.png\" style=\"margin:-3px -15px -3px 20px;\" />\n" +
                "<a href=\"Login.aspx\" class=\"about_link\">Вход в личный кабинет</a>\n" +
                "</div><br />\n" +
                "<!------------------>\n" +
                "<div class=\"spacerl_1\"><div class=\"spacerl_2\"></div></div>\n" +
                " <div style=\"padding-left:20px\" class=\"yashare-auto-init\" data-yashareL10n=\"ru\" data-yashareType=\"none\" data-yashareQuickServices=\"yaru,vkontakte,facebook,twitter,odnoklassniki,moimir,lj,friendfeed,moikrug\"></div>\t<br/>\n" +
                "    <div id=\"banner\">\n" +
                "\t<a href=\"http://ptravel.ru/News.aspx?id=253\">\n" +
                "    <img src=\"/images/banner3-7.gif\" alt=\"Баннер\" width=\"163\" height=\"97\" border=\"0\"/></a>\n" +
                       '\n' +
                "\t</div>\n" +
                "\t<div id=\"gallery\"><div id=\"galleryheader\"><h1>Артурс</h1></div>\n" +
                "\t<div id=\"galleryfoto\"><a href=\"/Object.aspx?f=6219\"> <img src=\"/GetThumb.ashx?id=6219&w=140\" alt=\"Детская площадка\" width=\"128\" height=\"88\" border=\"0\" /></a></div>\n" +
                "\t<div id=\"gallerytext\"><img src=\"/images/spring_day/ltl_sun.gif\" alt=\" \" width=\"14\" height=\"14\" align=\"absmiddle\" /> <a href=\"/Object.aspx?f=6219\">Детская площадка</a>&nbsp;</div>\n" +
                "\t</div>\n" +
                "</td>\n" +
                "  </tr>\n" +
                "</table>\n" +
                       '\n' +
                "<!-- Нижняя часть -->\n" +
                "<table width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" align=\"center\">\n" +
                "  <tr valign=\"top\">\n" +
                "    <td width=\"210\">\n" +
                "\t<div id=\"copyright\">\n" +
                "\t<p>Copyright &copy; 2009-2011<br />Все права защищены</p>\n" +
                "\t</div>\n" +
                "\t</td>\n" +
                "    <td>\n" +
                "\t<div id=\"btm_spacer1_1\"><div id=\"btm_spacer1_2\"></div></div>\n" +
                "\t<div id=\"address\"><p>109012, г. Москва, ул. Никольская, д.17, стр.2, Деловой центр \"Славянский\", офис № 3.3<br /><b style=\"font-weight:bold\">M</b> Лубянка, <b style=\"font-weight:bold\">M</b> Театральная,<b style=\"font-weight:bold\">M</b> Охотный ряд, <br /><b style=\"font-weight:bold\">M</b> Китай-город,<b style=\"font-weight:bold\">M</b> Площадь Революции</p></div>\t\n" +
                "\t</td>\n" +
                "    <td><div id=\"btm_spacer2\"></div>\n" +
                "\t<div id=\"telephone\"><font class=\"bggreen\">&nbsp;наш телефон:&nbsp;</font><br />\n" +
                "\t<font class=\"tel1\">+7 (495)</font><font class=\"tel2\"> 229 28 71</font></div>\n" +
                "\t</td>\n" +
                "    <td width=\"233\"><div id=\"btm_spacer3\"></div>\n" +
                "\t<div id=\"company\"><!--p>Создание сайта <a href=\"#\">Компания</a></p-->\n" +
                "    <!--LiveInternet counter--><script type=\"text/javascript\">                                   document.write(\"<a href='http://www.liveinternet.ru/click' target=_blank><img src='http://counter.yadro.ru/hit?t26.6;r\" + escape(document.referrer) + ((typeof (screen) == \"undefined\") ? \"\" : \";s\" + screen.width + \"*\" + screen.height + \"*\" + (screen.colorDepth ? screen.colorDepth : screen.pixelDepth)) + \";u\" + escape(document.URL) + \";i\" + escape(\"Жж\" + document.title.substring(0, 80)) + \";\" + Math.random() + \"' border=0 width=88 height=15 alt='' title='LiveInternet: показано число посетителей за сегодня'><\\/a>\")</script><!--/LiveInternet-->\n" +
                "\t</div>\n" +
                "\t</td>\n" +
                "  </tr>\n" +
                "</table>\n" +
                "<div id=\"grass\"></div>\n" +
                "<map name=\"Map\" id=\"Map\"><area shape=\"rect\" coords=\"4,160,22,174\" href=\"\\\" /><area shape=\"rect\" coords=\"8,182,22,194\" href=\"/SimpleMap.aspx\" /><area shape=\"rect\" coords=\"7,199,19,210\" href=\"mailto:info@ptravel.ru\" /></map>\n" +
                "<script type=\"text/javascript\">\n" +
                "    var gaJsHost = ((\"https:\" == document.location.protocol) ? \"https://ssl.\" : \"http://www.\");\n" +
                "    document.write(unescape(\"%3Cscript src='\" + gaJsHost + \"google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E\"));\n" +
                "</script>\n" +
                "<script type=\"text/javascript\">\n" +
                "    try {\n" +
                "        var pageTracker = _gat._getTracker(\"UA-12840497-1\");\n" +
                "        pageTracker._trackPageview();\n" +
                "    } catch (err) { } \n" +
                "</script>\n" +
                       '\n' +
                "<!-- Yandex.Metrika counter -->\n" +
                "<script src=\"//mc.yandex.ru/metrika/watch.js\" type=\"text/javascript\"></script>\n" +
                "<script type=\"text/javascript\">\n" +
                "    try { var yaCounter1931878 = new Ya.Metrika({ id: 1931878, enableAll: true, webvisor: true }); }\n" +
                "    catch (e) { }\n" +
                "</script>\n" +
                "<noscript><div><img src=\"//mc.yandex.ru/watch/1931878\" style=\"position:absolute; left:-9999px;\" alt=\"\" /></div></noscript>\n" +
                "<!-- /Yandex.Metrika counter -->\n" +
                       '\n' +
                "<!-- LiveTex Chat & Calls -->\n" +
                "<script type='text/javascript'>    /* build:::7 */\n" +
                "    var liveTex = true,\n" +
                "\t\tliveTexID = 25374,\n" +
                "\t\tliveTex_object = true;\n" +
                "    (function () {\n" +
                "        var lt = document.createElement('script');\n" +
                "        lt.type = 'text/javascript';\n" +
                "        lt.async = true;\n" +
                "        lt.src = 'http://cs15.livetex.ru/js/client.js';\n" +
                "        var sc = document.getElementsByTagName('script')[0];\n" +
                "        if (sc) sc.parentNode.insertBefore(lt, sc);\n" +
                "        else document.documentElement.firstChild.appendChild(lt);\n" +
                "    })();\n" +
                "</script>\n" +
                "<!-- /LiveTex Chat & Calls -->\n" +
                       '\n' +
                "</body>\n" +
                "</html>";
        return s1 + s2;
    }

    @Test
    public void testGoogleV3Url() throws Exception {
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = gmf.fix(new String("src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\"").getBytes("UTF-8"));
        String expected = "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=v3&amp;sensor=false&amp;indexing=true\"".replace("amp;", "&");
        assertEquals(expected, new String(url));
    }

    @Test
    public void testGoogleV2Url() throws Exception{
        gmf.setGoogleMapsApiKey("v2");

        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = gmf.fix(new String("src=\"http://maps.google.com/maps?file=api&amp;hl=en&amp;v=2&amp;key=ABQIAAAA37ULUZWfLzDP9UNvGnHV0xQj1PAjM0Fk2qGQeca6jIdbTyDahBQx1wMBRSAtyLcfFU1cGps-u53vuQ\"").getBytes("UTF-8"));
        String expected = "src=\"http://maps.google.com/maps?file=api&amp;hl=en&amp;v=2&amp;key=v2\"".replace("amp;", "&");
        assertEquals(expected, new String(url));
    }

    @Test
    public void testGoogleNotAPIUrl() throws Exception {
        gmf.setGoogleMapsApiKey("");
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = gmf.fix("href=\"http://maps.google.com/maps?near=%2B55%C2%B0+39'+27.11%22,+%2B37%C2%B0+51'+9.98\">55.657531".getBytes("UTF-8"));
        String expected = "href=\"" + new NormalizedURI("http://maps.google.com/maps?near=%2B55%C2%B0+39'+27.11%22,+%2B37%C2%B0+51'+9.98\"").toUnicodeString() + ">55.657531";
        assertEquals(expected, new String(url));
    }

    @Test
    public void testYandexV2Url() throws Exception{
        gmf.setYandexMapsApiKey("v2");
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = gmf.fix(new String("src=\"http://api-maps.yandex.ru/2.0.9/release/combine.xml?modules=egeigskxkJkIf0fWf5f2elgMgLkUgKethkeffCfHfEhfhdesekhxhohlhnhmhqeXfbfmffiMiNiOiPiFiHiEiRiIiQiDfTfXfPmDmKmGmEngizl8figqgkgtgnhbeGkyerg5kLkBgvkKgoh8g9kziih2fofYithrfkkYkXeum4g2isk9kZe1kVe8lTfqmffxfwmehgljg3lce7hegylgfne0hahwnjiGfQjgjfjejijhkDjqkki2i8mLjkjlfUkjjmmPi1i7mFknjpmRi6jcmJkmjoi4jamIkljni3i9mHfGjdjMjJjLjIjKjYjUjXjWjVjHjCjGjFjDjQgZm9hinrnqnpl0lXl3ndgznfgae3hQfukwgrioiggJfBfah7h6f7ixlbjwlMlPlhg4dYlKlNfvfeftfFmdg8ncfIfNfVleglkGkHh9ibj2j7kdnWnYi5jbfOfRjZj6nXiliqhhichGmQj4kaidj3j9ijiej1j8mMkievgdexewmOjEmZmVm1mXgcjRjSjTfcenfDfyhjnvg0nAnxnwnynznuntl1lYl4fpe5hvf3gbivlGjAf6lLlIlildlHh4jPfJfSjrlfgmgpe9kbf1eYkckfkhkgj0eziChEikeykRgEm0mYjyfje4e6aefzn6gWl2nMn5n4nNnOlZnDiwlxlElQh3mNfdejepjslphDkSkFjvf8f9lDcxczaJbucMbPnLnBgYe2ipjOjNg1hClmhHkTgCgGiuhzkAgBg7dghFhylRlOih&amp;jsonp_prefix=ymaps2_0_9\"").getBytes("UTF-8"));
        String expected = "src=\"http://api-maps.yandex.ru/2.0.9/release/combine.xml?modules=egeigskxkJkIf0fWf5f2elgMgLkUgKethkeffCfHfEhfhdesekhxhohlhnhmhqeXfbfmffiMiNiOiPiFiHiEiRiIiQiDfTfXfPmDmKmGmEngizl8figqgkgtgnhbeGkyerg5kLkBgvkKgoh8g9kziih2fofYithrfkkYkXeum4g2isk9kZe1kVe8lTfqmffxfwmehgljg3lce7hegylgfne0hahwnjiGfQjgjfjejijhkDjqkki2i8mLjkjlfUkjjmmPi1i7mFknjpmRi6jcmJkmjoi4jamIkljni3i9mHfGjdjMjJjLjIjKjYjUjXjWjVjHjCjGjFjDjQgZm9hinrnqnpl0lXl3ndgznfgae3hQfukwgrioiggJfBfah7h6f7ixlbjwlMlPlhg4dYlKlNfvfeftfFmdg8ncfIfNfVleglkGkHh9ibj2j7kdnWnYi5jbfOfRjZj6nXiliqhhichGmQj4kaidj3j9ijiej1j8mMkievgdexewmOjEmZmVm1mXgcjRjSjTfcenfDfyhjnvg0nAnxnwnynznuntl1lYl4fpe5hvf3gbivlGjAf6lLlIlildlHh4jPfJfSjrlfgmgpe9kbf1eYkckfkhkgj0eziChEikeykRgEm0mYjyfje4e6aefzn6gWl2nMn5n4nNnOlZnDiwlxlElQh3mNfdejepjslphDkSkFjvf8f9lDcxczaJbucMbPnLnBgYe2ipjOjNg1hClmhHkTgCgGiuhzkAgBg7dghFhylRlOih&&jsonp_prefix=ymaps2_0_9\"";
        assertEquals(expected, new String(url));
    }

    @Test
    public void testYandexStaticMapsV1Url() throws Exception{
        gmf.setYandexMapsApiKey("v1");
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = gmf.fix(new String("src=\"http://static-maps.yandex.ru/1.x/?ll=82.941648,55.011438&amp;l=map&amp;size=254,150&amp;key=ACnIg0oBAAAAon-MNwIAiciiypG8jIjEzNbfuHjKNj2mX30AAAAAAAAAAABA-1VfS1eNedhH36cCEriu4KQpeA==&amp;spn=0.011286827,0.00493262239999&amp;pt=82.941648,55.011438,pmlbm&amp;r=47635\"").getBytes("UTF-8"));
        String expected = "src=\"http://static-maps.yandex.ru/1.x/?ll=82.941648,55.011438&&l=map&&size=254,150&&key=v1&&spn=0.011286827,0.00493262239999&&pt=82.941648,55.011438,pmlbm&&r=47635\"";
        assertEquals(expected, new String(url));
    }

    @Test
    public void testYandexMapsV1Url() throws Exception{
        gmf.setYandexMapsApiKey("v1");
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = gmf.fix(new String("src=\"http://api-maps.yandex.ru/1.1/?loadByRequire=1&amp;key=AJY2HkoBAAAANu7DEgIA2RdP-yiRPGuy3hikDuk0TGZn3JgAAAAAAAAAAADqxFocptTEtEGNeUcMdBmrgwu5tA==\"></script>").getBytes("UTF-8"));
        String expected = "src=\"http://api-maps.yandex.ru/1.1/?loadByRequire=1&&key=v1\"></script>";
        assertEquals(expected, new String(url));
    }

    @Test
    public void testStream() throws Exception{
        long time = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            testWithShuffle(i);
        }
        System.out.println("performance: " + (double)(System.currentTimeMillis() - time)/1000);
    }

    private void testWithShuffle(int shuffle) throws IOException {
        byte[] shuffled = new byte[shuffle];
        Arrays.fill(shuffled, (byte)'a');
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = new String(new String(shuffled) + testStr + testStr + testStr + testStr + testStr + testStr +
                "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\"" +
                testStr + testStr + testStr + testStr + testStr + testStr).getBytes("UTF-8");
        String expected = new String(shuffled) + testStr + testStr + testStr + testStr + testStr + testStr + "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=v3&amp;sensor=false&amp;indexing=true\"".replace("amp;", "&") + testStr + testStr + testStr + testStr + testStr + testStr;
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: url) {
            stream.write(b);
        }
        stream.close();

        assertEquals(expected, new String(delegate.toByteArray()));
    }

    @Test
    public void testNoKey() throws Exception {
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = new String(testStr + testStr + testStr + testStr + testStr + testStr +
                "src=\"http://map.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\"" +
                testStr + testStr + testStr + testStr + testStr + testStr).getBytes("UTF-8");
        String expected = testStr + testStr + testStr + testStr + testStr + testStr + "src=\"http://map.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\"" + testStr + testStr + testStr + testStr + testStr + testStr;
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: url) {
            stream.write(b);
        }
        stream.close();

        assertEquals(expected, new String(delegate.toByteArray()));
    }

    String jq = "/**\n" +
            "* @author Remy Sharp\n" +
            "* @url http://remysharp.com/2007/01/25/jquery-tutorial-text-box-hints/\n" +
            "*/\n" +
            '\n' +
            "(function ($) {\n" +
            '\n' +
            "$.fn.hint = function (blurClass)\n" +
            "{\n" +
            "    if (!blurClass) {\n" +
            "        blurClass = 'blur';\n" +
            "    }\n" +
            '\n' +
            "    return this.each(function () {\n" +
            "        // get jQuery version of 'this'\n" +
            "        var $input = $(this),\n" +
            "            title = $input.attr('title'), // capture the rest of the variable to allow for reuse\n" +
            "            $form = $(this.form),\n" +
            "            $win = $(window);\n" +
            '\n' +
            "        function remove() {\n" +
            "            if ($input.val() === title && $input.hasClass(blurClass)) {\n" +
            "                $input.val('').removeClass(blurClass);\n" +
            "            }\n" +
            "        }\n" +
            '\n' +
            "        // only apply logic if the element has the attribute\n" +
            "        if (title) {\n" +
            "            // on blur, set value to title attr if text is blank\n" +
            "            $input.blur(function () {\n" +
            "                if (this.value === '') {\n" +
            "                    $input.val(title).addClass(blurClass);\n" +
            "                }\n" +
            "            }).focus(remove).blur(); // now change all inputs to title\n" +
            '\n' +
            "            // clear the pre-defined text when form is submitted\n" +
            "            $form.submit(remove);\n" +
            "            $win.unload(remove); // handles Firefox's autocomplete\n" +
            "        }\n" +
            "    });\n" +
            "};\n" +
            '\n' +
            "})(jQuery);";

    @Test
    public void testJquery() throws Exception {
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = jq.getBytes("UTF-8");
        String expected = jq;
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: url) {
            stream.write(b);
        }
        stream.close();

        assertEquals(expected, new String(delegate.toByteArray()));
    }

    @Test
    public void testNoKeySmall() throws Exception {
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = new String(
                "src=\"http://map.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\""
                ).getBytes("UTF-8");
        String expected = "src=\"http://map.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\"";
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: url) {
            stream.write(b);
        }
        stream.close();

        assertEquals(expected, new String(delegate.toByteArray()));
    }

    @Test
    public void testStart() throws Exception {
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = new String(
                "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\"" +
                        testStr + testStr + testStr + testStr + testStr + testStr).getBytes("UTF-8");
        String expected = "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=v3&amp;sensor=false&amp;indexing=true\"".replace("amp;", "&") + testStr + testStr + testStr + testStr + testStr + testStr;
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: url) {
            stream.write(b);
        }
        stream.close();

        assertEquals(expected, new String(delegate.toByteArray()));
    }

    @Test
    public void testEnd() throws Exception {
        @SuppressWarnings("RedundantStringConstructorCall")
        byte[] url = new String(testStr + testStr + testStr + testStr + testStr + testStr +
                "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=ABQIAAAA6rZ9anvk7bxskJiH7eEFVxQaZ6D3hhY1AZliGiR20qAnQxKE3hSTp-tTw5I3XYTY0ENsmBRoMhI87w&amp;sensor=false&amp;indexing=true\""
                        ).getBytes("UTF-8");
        String expected = testStr + testStr + testStr + testStr + testStr + testStr + "src=\"http://maps.google.com/maps?file=api&amp;v=3.x&amp;oe=utf-8&amp;hl=ru&amp;key=v3&amp;sensor=false&amp;indexing=true\"".replace("amp;", "&");
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: url) {
            stream.write(b);
        }
        stream.close();

        assertEquals(expected, new String(delegate.toByteArray()));
    }

    @Test
    public void testName2() throws Exception {
        ByteArrayOutputStream delegate = new ByteArrayOutputStream();
        MapsFix.MapsFixOutputStream stream = gmf.new MapsFixOutputStream(delegate);
        for (byte b: test2().getBytes()) {
            stream.write(b);
        }
        stream.close();
        System.out.println(new String(delegate.toByteArray()));
    }
}
