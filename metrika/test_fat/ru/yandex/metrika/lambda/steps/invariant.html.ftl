<html>
<head>
    <meta charset="utf-8">
    <title></title>
    <style>
        body {
            font-family: sans-serif;
        }

        table {
            border-collapse: collapse;
        }

        table, td, th {
            border: thin solid black;
        }

        td {
            padding: 3px;

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
    </style>
</head>
<body>
<h1>Инвариант ${result.name}</h1>
<h3>${result.version}</h3>
<div>YQL-скрипт:</div>
<pre>${(result.script)!}</pre>
<#if (result.hasResult) >
    <#if (result.result) >
        <div class="green">Инвариант выполнен</div>
    <#else>
        <div class="red">Инвариант не выполнен</div>
        <#if (result.hasDetails) >
            <table style="border: thin solid black">
                <tr>
                    <#list result.detailsKeys as key >
                        <th>${key!}</th>
                    </#list>
                </tr>
                <#list result.details as row >
                    <tr>
                        <#list result.detailsKeys as key >
                            <td>${row[key]!}</td>
                        </#list>
                    </tr>
                </#list>
            </table>
        </#if>
        </table>
    </#if>
<#else>
    <#if (result.hasError) >
        <div class="yellow"><pre>${result.error.toString()}</pre></div>
    <#else>
        <div class="yellow">Результат проверки инварианта отсутствует</div>
    </#if>
</#if>
</body>
</html>
