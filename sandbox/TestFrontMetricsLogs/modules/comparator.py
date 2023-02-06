# -*- coding: utf-8 -*-

import tarfile
import json


class MetricComparator:

    def __init__(self, stable_path, testing_path, output_html_path, yuid_to_scenario_map):
        self._stable_path = stable_path
        self._testing_path = testing_path
        self._output_html_path = output_html_path
        self._yuid_to_scenario_map = yuid_to_scenario_map
        self._IsMetricsEqual = None

    def Compare(self):
        stableMetricsData = MetricComparator._LoadData(self._stable_path)
        testingMetricsData = MetricComparator._LoadData(self._testing_path)
        allScenarios = set(stableMetricsData.keys() + testingMetricsData.keys())
        totalCount = len(allScenarios)
        addInTesting = allScenarios.difference(stableMetricsData)
        rmInTesting = allScenarios.difference(testingMetricsData)
        successMap = {}
        diffMap = {}
        for sc_id in allScenarios:
            stableMetricsMap = stableMetricsData.get(sc_id, {})
            testingMetricsMap = testingMetricsData.get(sc_id, {})
            if stableMetricsMap == testingMetricsMap:
                successMap[sc_id] = MetricComparator._SortMetrics(stableMetricsMap, testingMetricsMap)
            else:
                diffMap[sc_id] = MetricComparator._SortMetrics(stableMetricsMap, testingMetricsMap)

        assert totalCount == len(diffMap) + len(successMap), "scenarios count missmatch"
        self._IsMetricsEqual = (len(diffMap) == 0)
        report = MetricComparator._GenerateReport(successMap, diffMap, addInTesting, rmInTesting, self._yuid_to_scenario_map)
        with open(self._output_html_path, 'w') as f:
            f.write(report)

    def MetricsAreEquals(self):
        if self._IsMetricsEqual is None:
            raise RuntimeError("Method 'MetricsAreEqual' can not be called before 'Compare'")
        return self._IsMetricsEqual

    @staticmethod
    def _SortMetrics(stableMetricsMap, testingMetricsMap):
        """
        :param: lhs {metricName1: value1, ...}
        :param: rhs {metricName1: value1, ...}
        :return: {metricName: {"stable": value1, "testing": value2}, ...}
        """
        diff = {}
        for metric in set(stableMetricsMap.keys() + testingMetricsMap.keys()):
            metricDiff = {"stable": "", "testing": ""}
            if metric in stableMetricsMap:
                metricDiff["stable"] = stableMetricsMap[metric]
            if metric in testingMetricsMap:
                metricDiff["testing"] = testingMetricsMap[metric]
            diff[metric] = metricDiff

        return diff

    @staticmethod
    def _LoadData(metricsArchivePath):
        """
            return a map. key - scenario_id, value - map of {metricName, metricValue}
            {scenario_id1:{metricName1:metricVal1, metricName2:metricVal2}, ...},
        """
        metrics = {}
        with tarfile.open(metricsArchivePath) as tar:
            for m_file in tar.getmembers():
                scenario_id = m_file.name.split('-')[0]
                metrics[scenario_id] = {}
                opened_file = tar.extractfile(m_file)
                # format description: https://wiki.yandex-team.ru/serp/experiments/statfetcher/
                jsonReport = json.load(opened_file)
                for metricName, valuesList in jsonReport['data']['metrics'].items():
                    metrics[scenario_id][metricName] = valuesList[0]["val"]

        return metrics

    @staticmethod
    def _GenerateScenariosTableHeader(diffScenarios, successScenarios, yuid_to_scenario_map):
        return "".join(
            "<th style='background:red'><a href=https://yt.yandex-team.ru/hahn/#page=navigation&path=//tmp/front_metrics/{} target=_blank>{}</a></th>".format(
                MetricComparator._FindKeyByValue(yuid_to_scenario_map, x),
                x
            ) for x in diffScenarios) + "".join(
            "<th><a href=https://yt.yandex-team.ru/hahn/#page=navigation&path=//tmp/front_metrics/{} target=_blank>{}</a></th>".format(
                MetricComparator._FindKeyByValue(yuid_to_scenario_map, x),
                x
            ) for x in successScenarios)

    @staticmethod
    def _FindKeyByValue(keyValueMap, value):
        for k, v in keyValueMap.items():
            if v == value:
                return k
        return None

    @staticmethod
    def _GetScenariosOutputSequence(scenarioList):
        return sorted(scenarioList)

    @staticmethod
    def _GenerateStatsRows(metricsSet, diffScenarios, successScenarios):
        tableRows = ""
        for metric in metricsSet:
            row = ""
            for sc_id in MetricComparator._GetScenariosOutputSequence(diffScenarios.keys()):
                if metric in diffScenarios[sc_id]:
                    stableValue = diffScenarios[sc_id][metric]["stable"]
                    testingValue = diffScenarios[sc_id][metric]["testing"]
                    assert stableValue != testingValue, "stable and testing value should be NOT equal for diffScenarios"
                    row = row + "<td style='background:red'>{}->{}</td>".format(stableValue, testingValue)
                else:
                    row = row + "<td></td>"
            for sc_id in MetricComparator._GetScenariosOutputSequence(successScenarios.keys()):
                if metric in successScenarios[sc_id]:
                    stableValue = successScenarios[sc_id][metric]["stable"]
                    testingValue = successScenarios[sc_id][metric]["testing"]
                    assert stableValue == testingValue, "stable and testing value should be equal for successScenarios"
                    row = row + "<td style='background:green'>{}</td>".format(stableValue)
                else:
                    row = row + "<td></td>"
            tableRows = tableRows + "<tr><td>{}</td>{}</tr>".format(metric, row)
        return tableRows

    @staticmethod
    def _GetMetricSet(successMap, diffMap):
        metricSet = set()
        for k in successMap.values():
            metricSet.update(MetricComparator._FilterMetrics(k.keys()))
        for k in diffMap.values():
            metricSet.update(MetricComparator._FilterMetrics(k.keys()))
        return sorted(metricSet)

    @staticmethod
    def _FilterMetrics(metricsList):
        allowedMetricsPattern = ["market.searchxml", "market.common"]
        rejectedMetricNames = [
            "market.common.YaMetrika_counters_coverage",
            "market.common.average_click_price",
            "market.common.cpc_trans_to_orders_conversion",
            "market.common.custom.total_transitions",
            "market.common.total_clicks_money",
            "market.common.total_cpc_orders_absolute",
            "market.common.total_cpc_orders_estimate",
            "market.common.total_orders",
            "market.searchxml.total_results",
        ]

        allowedMetrics = [metricName for metricName in metricsList if any(
            metricSubstr in metricName for metricSubstr in
            allowedMetricsPattern
        )]

        return filter(lambda x: x not in rejectedMetricNames, allowedMetrics)

    @staticmethod
    def _GenerateReport(successMap, diffMap, addInTesting, rmInTesting, yuid_to_scenario_map):
        successCount = len(successMap)
        diffCount = len(diffMap)
        totalCount = successCount + diffCount
        successPercent = 1.0 * successCount / totalCount

        metricsSet = MetricComparator._GetMetricSet(successMap, diffMap)
        scenariosInTableHeader = MetricComparator._GenerateScenariosTableHeader(
            MetricComparator._GetScenariosOutputSequence(diffMap.keys()),
            MetricComparator._GetScenariosOutputSequence(successMap.keys()),
            yuid_to_scenario_map
        )
        tableRows = MetricComparator._GenerateStatsRows(metricsSet, diffMap, successMap)

        return """\
    <html>
        <head>
            <meta charset="UTF-8">
            <title>FrontMetricsReport</title>
        </head>
        <body>
            <div>успешно: {successCount}/{totalCount} ({successPercent:.2%})</div>
            <div>добавленные сценарии в тестинге: {nit} {nitlist}</div>
            <div>удаленные сценарии в тестинге: {rit} {ritlist}</div>
            <table  border='1'>
                <tr><th>метрика\сценарий</th>{metricsInTableHeader}</tr>
                {tableRows}
            </table>
        </body>
    </html>\
        """.format(
            successCount=successCount,
            totalCount=totalCount,
            successPercent=successPercent,
            nit=len(addInTesting), nitlist="( {} )".format(", ".join(addInTesting)) if len(addInTesting) else "",
            rit=len(rmInTesting), ritlist="( {} )".format(", ".join(rmInTesting)) if len(rmInTesting) else "",
            metricsInTableHeader=scenariosInTableHeader,
            tableRows=tableRows
        )
