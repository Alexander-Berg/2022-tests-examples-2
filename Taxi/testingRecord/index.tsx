import React, { useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

import Column from '../../../../components/column';
import Container from '../../../../components/container';
import JsonEditor from '../../../../components/jsonEditor';
import Row from '../../../../components/row';
import Text from '../../../../components/text';
import Status from '../status';
import stylesConfig, { gaps } from '../../../../stylesConfig';

import { ConfigurationTestRecord } from '../../../../types/models/ConfigurationTestRecord';

import './styles.scss';

type TestingRecordProps = {
  record: ConfigurationTestRecord,
  historyUsed?: boolean
}

export default function TestingRecord({
  record,
  historyUsed = false,
}: TestingRecordProps) {
  const { t } = useTranslation(); 
  const { isEqual } = record;
  const draftEditorRef = useRef<any>(null); // TODO добавить интерфейс JSON editor'a
  const releaseEditorRef = useRef<any>(null);

  useEffect(() => {
    if (draftEditorRef.current && releaseEditorRef.current) {
      const draftScrollableContent = draftEditorRef.current.elem.jsonEditor.scrollableContent;
      const releaseScrollableContent = releaseEditorRef.current.elem.jsonEditor.scrollableContent;
      draftEditorRef.current.elem.jsonEditor.expandAll();
      releaseEditorRef.current.elem.jsonEditor.expandAll();

      const draftScrollHandler = () => {
        releaseScrollableContent.scrollTop = draftScrollableContent.scrollTop;
      }

      draftScrollableContent.addEventListener('scroll', draftScrollHandler, false);

      return () => {
        draftScrollableContent.removeEventListener('scroll', draftScrollHandler)
      };
    }
  }, []);

  return (
    <Column autosize className="testing-record">
      <Row autosize gap={gaps.listElements}>
        <Container flexGrow={1}>
          <Text color={stylesConfig.fontColorSecond}>{t("PAGE_TESTING.REQUESTED_TEXT")}: </Text><Text>{record.requestText}</Text>
        </Container>
        <Container className="status-container" flexShrink={0}>
          <Status value={isEqual} />
        </Container>
      </Row>
      { record.diff && (
        <Row className="diff-container" autosize gap={gaps.listElements}>
          <Container flexGrow={1}>
            <Text className="diff-label" color={stylesConfig.fontColorSecond}>{historyUsed ? t("PAGE_TESTING.HISTORICAL_ANSWER") : 'Draft'}</Text>
            <JsonEditor ref={draftEditorRef} value={record.diff.draft} mode="view" sortObjectKeys={true} />
          </Container>
          <Container flexGrow={1}>
            <Text className="diff-label" color={stylesConfig.fontColorSecond}>Release</Text>
            <JsonEditor ref={releaseEditorRef} value={record.diff.release} mode="view" sortObjectKeys={true} />
          </Container>
        </Row>
      )}
    </Column>
  )
}