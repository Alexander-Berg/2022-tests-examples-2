<html>
<head>
    <meta charset="utf-8">
    <title></title>
    <style>
        body {
            font-family: sans-serif;
        }

        a:hover, a:visited, a:link, a:active {
            text-decoration: underline;
        }

        a {
            color: inherit;
        }

        table {
            border-collapse: collapse;
        }

        table, td, th {
            border: thin solid black;
        }

        td, th {
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
<h1>Общие результаты тестов</h1>
<h3>${suite.startDateTime} - ${suite.finishDateTime} (${suite.duration})</h3>
<table style="border: thin solid black">
    <tr>
        <th>Демон</th>
        <th>Ручка</th>
        <th>Всего запросов (доля)</th>
        <th>Нач. вр.</th>
        <th>Кон. вр.</th>
        <th>Длит</th>
        <th class="red">${ResultKind.NEGATIVE}</th>
        <th class="red">${ResultKind.NOT_SIMILAR}</th>
        <th class="yellow">${ResultKind.BROKEN}</th>
        <th class="yellow">${ResultKind.UNEXPECTED}</th>
        <th class="yellow">${ResultKind.EXTERNAL_TEST_ERROR}</th>
        <th class="yellow">${ResultKind.INTERNAL_TEST_ERROR}</th>
        <th class="grey">${ResultKind.BAD_REQUEST}</th>
        <th class="lightblue">${ResultKind.ALMOST_BAD_REQUEST}</th>
        <th class="lightblue">${ResultKind.NO_DATA}</th>
        <th class="green">${ResultKind.POSITIVE}</th>
    </tr>
    <#macro render_cell class, value, anchor, destination, handle, total>
      <td<#if (value>0)> class="${class}"</#if>><a href="${destination}${handle}/index.html#${anchor}">${value}<#if (value>0)> (${value/total})</#if></a></td>
    </#macro>
  <#list suite.results as testCase>
    <tr>
        <td>${testCase.destination}</td>
        <td><a href="${testCase.destination}${testCase.handle}/index.html">${testCase.handle}</a></td>
        <td>${testCase.totalSamples} (${testCase.percentile})</td>
        <td>${testCase.startDateTime}</td>
        <td>${testCase.finishDateTime}</td>
        <td>${testCase.duration}</td>
        <@render_cell "red", testCase.totalSamplesNegative, ResultKind.NEGATIVE.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "red", testCase.totalSamplesNotSimilar, ResultKind.NOT_SIMILAR.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "yellow", testCase.totalSamplesBroken, ResultKind.BROKEN.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "yellow", testCase.totalSamplesUnexpected, ResultKind.UNEXPECTED.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "yellow", testCase.totalSamplesExternalError, ResultKind.EXTERNAL_TEST_ERROR.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "yellow", testCase.totalSamplesInternalError, ResultKind.INTERNAL_TEST_ERROR.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "grey", testCase.totalSamplesBadRequest, ResultKind.BAD_REQUEST.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "lightblue", testCase.totalSamplesAlmostBadRequest, ResultKind.ALMOST_BAD_REQUEST.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "lightblue", testCase.totalSamplesNoData, ResultKind.NO_DATA.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
        <@render_cell "green", testCase.totalSamplesPositive, ResultKind.POSITIVE.name(), testCase.destination, testCase.handle, testCase.totalSamples/>
    </tr>
  </#list>
</table>
</body>
</html>
