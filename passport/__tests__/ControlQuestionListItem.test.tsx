import { MockedProvider } from '@apollo/client/testing';
import {
  act,
  createClientRender,
  fireEvent,
  installPointerEvent,
  screen,
  waitFor,
} from '@client/shared/libs/testing';

import { ControlQuestionListItem } from '../ControlQuestionListItem';
import * as model from '../model';

jest.mock('next/router', () => require('@client/shared/libs/testing/router'));

describe('ControlQuestionListItem', () => {
  installPointerEvent();

  const render = createClientRender();

  test('should call dialog show after press on item', async () => {
    render(
      <MockedProvider>
        <ControlQuestionListItem />
      </MockedProvider>,
    );

    const onShow = jest.fn();
    const element = await waitFor(() => screen.getByTestId('kvko-list-item'));

    model.dialog.show.watch(onShow);

    act(() => {
      fireEvent.pointerDown(element);
      fireEvent.pointerUp(element);
    });

    expect(onShow).toBeCalled();
  });

  test('should set data-log for metric', async () => {
    render(
      <MockedProvider>
        <ControlQuestionListItem />
      </MockedProvider>,
    );

    const element = await waitFor(() => screen.getByTestId('kvko-list-item'));

    expect(element.dataset.log).toBe('{"type":"listitem.control-question","value":true}');
  });
});
