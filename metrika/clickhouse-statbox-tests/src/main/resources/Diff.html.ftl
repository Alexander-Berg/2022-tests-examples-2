<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <style type="text/css">
        body {
            padding-bottom: 100px;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        }

        table {
            border: none;
        }

        td, th {
            padding-left: 4px;
            padding-right: 4px;

        }

        th {
            background-color: #428BCA;
            color: #fff;
        }

        tr.diff-insert {
            background-color: green;
        }

        tr.diff-delete {
            background-color: red;
        }

        tr.diff-change {
            background-color: yellow;
        }
    </style>
</head>
<body>
<table>
    <thead>
    <tr>
        <th>№ строки</th>
        <th>Аннотация (добавлено/удалено/изменено)</th>
        <th>Результат на stable</th>
        <th>Результат на test</th>
    </tr>
    </thead>
        <#list diff as row>
          <#if row.tag == Tag.INSERT>
            <#assign row_class="diff-insert"/>
            <#assign annotation="Добавлено"/>
          <#elseif row.tag == Tag.DELETE>
            <#assign row_class="diff-delete"/>
            <#assign annotation="Удалено"/>
          <#elseif row.tag == Tag.CHANGE>
            <#assign row_class="diff-change"/>
            <#assign annotation="Изменено"/>
          <#else>
            <#assign row_class="diff-no-change"/>
            <#assign annotation=""/>
          </#if>
          <#if row.tag == Tag.INSERT || row.tag == Tag.DELETE || row.tag == Tag.CHANGE>
            <tr class="${row_class}">
                <td><pre>${row?counter}</pre></td>
                <td>
                  <pre>${annotation}</pre>
                </td>
                <td>
                  <pre>${row.oldLine}</pre>
                </td>
                <td>
                  <pre>${row.newLine}</pre>
                </td>
            </tr>
          </#if>
        </#list>
</table>
</body>
</html>
