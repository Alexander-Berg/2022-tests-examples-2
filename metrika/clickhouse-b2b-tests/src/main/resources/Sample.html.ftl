<html>
<head>
    <meta charset="utf-8">
    <title></title>
    <style>
        body {
            font-family: sans-serif;
        }
    </style>
</head>
<body>
<#macro response r>
<h3>Запрос</h3>
<div>URL:
    <pre>${(r.requestUrl)!}</pre>
</div>
<div>Параметры:</div>
<pre>${(r.requestParams)!}</pre>
<h3>Ответ</h3>
  <#if r.hasException>
<div>Произошла ошибка при выполнении запроса</div>
<div>${r.exception}</div>
  <#else>
<pre>${r.code} ${r.message}</pre>
<div>Заголовки:</div>
<pre>${(r.headers)!""}</pre>
<div>Тело:</div>
<pre>${(r.response)!""}</pre>
  </#if>
</#macro>

<h1>${sample.handle}</h1>
<h3>${sample.startDateTime} - ${sample.finishDateTime} (${sample.duration})</h3>
<h1>${sample.diff.resultKind}</h1>
<#if sample.diff.hasInternalError>
<hr/>
<h3>Внутренняя ошибка</h3>
<pre>
  ${sample.diff.internalError}
</pre>
<#else>
  <#if sample.diff.hasDiff>
  <hr/>
  <h3>Различия</h3>
<pre>
  ${sample.diff.consoleDiff}
</pre>
<div>
  ${sample.diff.htmlDiff}
</div>
  </#if>
</#if>
<hr/>
<h2>Test</h2>
<@response r=sample.diff.fromTest/>
<hr/>
<h2>Ref</h2>
<@response r=sample.diff.fromRef/>
</body>
</html>