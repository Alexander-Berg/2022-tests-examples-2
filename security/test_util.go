package parsers

import (
	"gopkg.in/mcuadros/go-syslog.v2/format"

	"a.yandex-team.ru/security/osquery/osquery-sender/parser"
	"a.yandex-team.ru/security/osquery/osquery-sender/syslogparsing/util"
)

// Simulates more or less what we do in 'syslogparsing.go' to build the parser.ParsedEvent.
// Here we only call SyslogParser.FillEvent, which usually only sets event.Data,
// so in the tests we should only check the data set in that method (for each format).
func parseLog(logLine string, syslogParser SyslogParser, name string) *parser.ParsedEvent {
	logParts, err := parseLogLine(syslogParser.Format, logLine)
	if err != nil {
		panic(err)
	}
	logPartsWrapper := &util.LogPartsWrapper{LogParts: logParts}
	event := &parser.ParsedEvent{
		Data: map[string]interface{}{
			"name": name,
		},
	}
	syslogParser.FillEvent(logPartsWrapper, event)
	return event
}

func parseLogLine(f format.Format, logLine string) (logParts format.LogParts, err error) {
	logParser := f.GetParser([]byte(logLine))
	err = logParser.Parse()
	if err != nil {
		return
	}
	logParts = logParser.Dump()
	return
}
