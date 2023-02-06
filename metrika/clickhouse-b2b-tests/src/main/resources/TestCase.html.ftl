<html>
<head>
    <meta charset="utf-8">
    <title></title>
    <style>
        body {
            font-family: sans-serif;
        }
        a:hover, a:visited, a:link, a:active
        {
            text-decoration: underline;
        }
        a {color: inherit; }
        table {
            border-collapse: collapse;
        }

        table, td, th {
            border: thin solid black;
        }
        td {
            padding: 3px;

        }
        .grey {
            color: black;
            background-color: grey;
        }

        .green {
            color: white;
            background-color: green;
        }

        .yellow {
            color: black;
            background-color: yellow;
        }

        .red {
            color: white;
            background-color: red;
        }

        .lightblue {
            color: white;
            background-color: lightblue;
        }
    </style>
</head>
<body>
<h1 id="top">Сводка</h1>
<h3>${testCase.startDateTimeAsString} - ${testCase.finishDateTimeAsString} (${testCase.durationAsString})</h3>
<table style="border: thin solid black">
    <tr>
        <td>Всего запросов:</td>
        <td>${testCase.totalSamples}</td>
        <td>${testCase.percentile}</td>
    </tr>
    <tr class="red" ">
        <td><a href="#${ResultKind.NEGATIVE.name()}">${ResultKind.NEGATIVE}</a></td>
        <td>${testCase.totalSamplesNegative}</td>
        <td>${testCase.totalSamplesNegative/testCase.totalSamples}</td>
    </tr>
    <tr class="red">
        <td><a href="#${ResultKind.NOT_SIMILAR.name()}">${ResultKind.NOT_SIMILAR}</a></td>
        <td>${testCase.totalSamplesNotSimilar}</td>
        <td>${testCase.totalSamplesNotSimilar/testCase.totalSamples}</td>
    </tr>
    <tr class="yellow">
        <td><a href="#${ResultKind.BROKEN.name()}">${ResultKind.BROKEN}</a></td>
        <td>${testCase.totalSamplesBroken}</td>
        <td>${testCase.totalSamplesBroken/testCase.totalSamples}</td>
    </tr>
    <tr class="yellow">
        <td><a href="#${ResultKind.UNEXPECTED.name()}">${ResultKind.UNEXPECTED}</a></td>
        <td>${testCase.totalSamplesUnexpected}</td>
        <td>${testCase.totalSamplesUnexpected/testCase.totalSamples}</td>
    </tr>
    <tr class="yellow">
        <td><a href="#${ResultKind.EXTERNAL_TEST_ERROR.name()}">${ResultKind.EXTERNAL_TEST_ERROR}</a></td>
        <td>${testCase.totalSamplesExternalError}</td>
        <td>${testCase.totalSamplesExternalError/testCase.totalSamples}</td>
    </tr>
    <tr class="yellow">
        <td><a href="#${ResultKind.INTERNAL_TEST_ERROR.name()}">${ResultKind.INTERNAL_TEST_ERROR}</a></td>
        <td>${testCase.totalSamplesInternalError}</td>
        <td>${testCase.totalSamplesInternalError/testCase.totalSamples}</td>
    </tr>
    <tr class="grey">
        <td><a href="#${ResultKind.BAD_REQUEST.name()}">${ResultKind.BAD_REQUEST}</a></td>
        <td>${testCase.totalSamplesBadRequest}</td>
        <td>${testCase.totalSamplesBadRequest/testCase.totalSamples}</td>
    </tr>
    <tr class="lightblue">
        <td><a href="#${ResultKind.ALMOST_BAD_REQUEST.name()}">${ResultKind.ALMOST_BAD_REQUEST}</a></td>
        <td>${testCase.totalSamplesAlmostBadRequest}</td>
        <td>${testCase.totalSamplesAlmostBadRequest/testCase.totalSamples}</td>
    </tr>
    <tr class="lightblue">
        <td><a href="#${ResultKind.NO_DATA.name()}">${ResultKind.NO_DATA}</a></td>
        <td>${testCase.totalSamplesNoData}</td>
        <td>${testCase.totalSamplesNoData/testCase.totalSamples}</td>
    </tr>
    <tr class="green">
        <td><a href="#${ResultKind.POSITIVE.name()}">${ResultKind.POSITIVE}</a></td>
        <td>${testCase.totalSamplesPositive}</td>
        <td>${testCase.totalSamplesPositive/testCase.totalSamples}</td>
    </tr>
</table>

<h1>Подробно</h1>
<!-- RED - NEGATIVE, NOT_SIMILAR -->
<#if (testCase.samplesNegative?size>0) >
<h2 id="${ResultKind.NEGATIVE.name()}"><a href="#top">${ResultKind.NEGATIVE}</a></h2>
<table class="red">
<#list testCase.samplesNegative as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td><#if (sample.diff.consoleDiff?length<200)>${sample.diff.consoleDiff}<#else>${sample.diff.consoleDiff?substring(0, 200)}</#if></td>
    </tr>
</#list>
</table>
</#if>

<#if (testCase.samplesNotSimilar?size>0)>
<h2 id="${ResultKind.NOT_SIMILAR.name()}"><a href="#top">${ResultKind.NOT_SIMILAR}</a></h2>
<table class="red">
<#list testCase.samplesNotSimilar as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>получен ответ ${sample.diff.fromTest.code}, а ожидался ${sample.diff.fromRef.code}</td>
    </tr>
</#list>
</table>
</#if>
<!-- YELLOW - BROKEN, UNEXPECTED, INTERNAL -->
<#if (testCase.samplesBroken?size>0)>
<h2 id="${ResultKind.BROKEN.name()}"><a href="#top">${ResultKind.BROKEN}</a></h2>
<table class="yellow">
<#list testCase.samplesBroken as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>получен ответ ${sample.diff.fromTest.code}</td>
    </tr>
</#list>
</table>
</#if>
<#if (testCase.samplesUnexpected?size>0)>
<h2 id="${ResultKind.UNEXPECTED.name()}"><a href="#top">${ResultKind.UNEXPECTED}</a></h2>
<table class="yellow">
<#list testCase.samplesUnexpected as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>получен ответ ${sample.diff.fromTest.code}</td>
    </tr>
</#list>
</table>
</#if>
<#if (testCase.samplesExternalError?size>0)>
<h2 id="${ResultKind.EXTERNAL_TEST_ERROR.name()}"><a href="#top">${ResultKind.EXTERNAL_TEST_ERROR}</a></h2>
<table class="yellow">
<#list testCase.samplesExternalError as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>${sample.diff.externalError}</td>
    </tr>
</#list>
</table>
</#if>
<#if (testCase.samplesInternalError?size>0)>
<h2 id="${ResultKind.INTERNAL_TEST_ERROR.name()}"><a href="#top">${ResultKind.INTERNAL_TEST_ERROR}</a></h2>
<table class="yellow">
<#list testCase.samplesInternalError as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>${sample.diff.internalError}</td>
    </tr>
</#list>
</table>
</#if>
<!-- GREY - BAD_REQUEST -->
<#if (testCase.samplesBadRequest?size>0)>
<h2 id="${ResultKind.BAD_REQUEST.name()}"><a href="#top">${ResultKind.BAD_REQUEST}</a></h2>
<table class="grey">
<#list testCase.samplesBadRequest as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>получен код ответа: ${sample.diff.fromTest.code}</td>
    </tr>
</#list>
</table>
</#if>
<!-- LIGHTBLUE - ALMOST_BAD_REQUEST, NO_DATA -->
<#if (testCase.samplesAlmostBadRequest?size>0)>
<h2 id="${ResultKind.ALMOST_BAD_REQUEST.name()}"><a href="#top">${ResultKind.ALMOST_BAD_REQUEST}</a></h2>
<table class="lightblue">
<#list testCase.samplesAlmostBadRequest as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td>получен код ответа: ${sample.diff.fromTest.code}</td>
    </tr>
</#list>
</table>
</#if>
<#if (testCase.samplesNoData?size>0)>
<h2 id="${ResultKind.NO_DATA.name()}"><a href="#top">${ResultKind.NO_DATA}</a></h2>
<table class="lightblue">
<#list testCase.samplesNoData as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td></td>
    </tr>
</#list>
</table>
</#if>
<!-- GREEN - POSITIVE -->
<#if (testCase.samplesPositive?size>0)>
<h2 id="${ResultKind.POSITIVE.name()}"><a href="#top">${ResultKind.POSITIVE}</a></h2>
<table class="green">
<#list testCase.samplesPositive as sample>
    <tr>
        <td>${sample.seq}</td>
        <td>
            <a href="${sample.diff.resultKind.name()}/${sample.id}.html" target="_blank">${sample.id}</a>
        </td>
        <td></td>
    </tr>
</#list>
</table>
</#if>
</body>
</html>
