import React, {
  FC, useCallback, useEffect, useMemo,
} from 'react';

import { shallowEqual, useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';

import * as actions from '../../../../redux/graphChat/actions';
import * as dialogActions from '../../../../redux/dialogs/actions';
import { AppState } from '../../../../redux/reducers';

import { MessageAuthor } from '../../../../types/models/Message';

import { ChatMessage, ChatOptions } from '../../../../components-new/chat/types';
import Chat from '../../../../components-new/chat';

import StartPage from './startPage';
import ChatDisabledMessage from './chatDisabledMessage';

import { UserMessageAndNodeMatch } from '../../../../redux/graphChat/reducers';
import { getGraphChatButtons } from '../../../../redux/graphChat/selectors';

import './styles.scss';

const TestingChat: FC<{}> = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  const dialogs = useSelector(
    (state: AppState) => state.dialogs,
    shallowEqual,
  );

  const graphChat = useSelector(
    (state: AppState) => state.graphChat,
    shallowEqual,
  );

  const buttons = useSelector(
    getGraphChatButtons,
    shallowEqual,
  );

  const options: ChatOptions = useMemo(
    () => {
      const suggestions = graphChat.activeRequestedFeature?.suggestions;
      if (!suggestions) return null;

      return suggestions.map(
        (str) => ({
          label: str,
          value: str,
        }),
      );
    },
    [graphChat],
  );

  const dialog: ChatMessage[] = useMemo(
    () => {
      const messages = dialogs?.liveDialog?.messages || [];
      const { userMessageAndNodeMatches } = graphChat;

      const checkIfClearable = (messageId?: string) => {
        if (!messageId) return false;

        return userMessageAndNodeMatches?.some(
          (match: UserMessageAndNodeMatch) => match.userMessageId === messageId,
        );
      };

      return messages.map(
        (message) => ({
          ...message,
          clearable: checkIfClearable(message.id),
          text: message.author === MessageAuthor.Ai && !message.text
            ? t('GRAPH.TESTING_CHAT.FALLBACK_MESSAGE') as string
            : message.text || '',
        }),
      );
    },
    [dialogs, graphChat, t],
  );

  const {
    isEmptyDialog, isLoading, showChat, disableInput,
  } = useMemo(
    () => ({
      isEmptyDialog: !dialog.length,
      isLoading: !!dialogs?.liveSending,
      showChat: !!graphChat?.show,
      disableInput: !!graphChat?.disabledOnGraphEdit,
    }),
    [dialog, dialogs.liveSending, graphChat],
  );

  const handleCloseChat = useCallback(() => {
    dispatch(actions.closeGraphTestingChat());
    dispatch(dialogActions.clearLiveChat());
  }, [dispatch]);

  const handleResetChat = useCallback(() => {
    dispatch(dialogActions.clearLiveChat());
  }, [dispatch]);

  const handlePostMessage = useCallback(
    (text: string) => {
      dispatch(actions.postMessage(text));
    },
    [dispatch],
  );

  const handleDeleteMessage = useCallback(
    (id: string) => {
      dispatch(actions.deleteMessage(id));
    },
    [dispatch],
  );

  const handleButtonClick = useCallback(
    (clickedButtonId: string) => {
      const text = buttons?.find(({ id }) => clickedButtonId === id)?.text;

      if (!text) return;

      dispatch(actions.setButtonsBlock(undefined));
      dispatch(actions.postMessage(text));
    },
    [buttons, dispatch],
  );

  useEffect(
    () => {
      return () => {
        dispatch(actions.closeGraphTestingChat());
        dispatch(dialogActions.clearLiveChat());
      }
    },
    [],
  );

  if (!showChat) return null;

  return (
    <Chat
      slim
      hideOverlay
      title={t('GRAPH.TESTING_CHAT.TITLE')}
      showResetButton={!isEmptyDialog}
      dialog={dialog}
      isLoading={isLoading}
      inputAutoFocus
      options={options}
      footerContent={disableInput
        ? <ChatDisabledMessage />
        : undefined}
      buttons={buttons || undefined}
      onButtonClick={handleButtonClick}
      onReset={handleResetChat}
      onClose={handleCloseChat}
      onPost={handlePostMessage}
      onDelete={handleDeleteMessage}
    >
      {isEmptyDialog ? <StartPage /> : null}
    </Chat>
  );
};

export default TestingChat;
