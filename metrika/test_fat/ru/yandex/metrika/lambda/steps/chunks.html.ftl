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
    </style>
</head>
<body>
<h1>${name}</h1>
<#if (rows?size > 0)>
    <#assign cols=rows?first?keys>
    <table style="border: thin solid black">
        <tr>
            <#list cols as key >
                <th>${key}</th>
            </#list>
        </tr>
        <#list rows as row >
            <tr>
                <#list cols as key >
                    <td>${row[key]?string}</td>
                </#list>
            </tr>
        </#list>
    </table>
<#else >
    <h3>Данных нет</h3>
</#if>
</body>
</html>
