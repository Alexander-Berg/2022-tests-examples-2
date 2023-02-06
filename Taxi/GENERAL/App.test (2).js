import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createMemoryHistory } from 'history';
import configureStore from 'redux-mock-store';
import { ConnectedRouter } from 'connected-react-router';

import { uiInitialState } from 'modules/ui/uiReducer';
import { userInitialState } from 'modules/user/userReducer';
import { dataInitialState } from 'modules/data/dataReducer';
import { errorsInitialState } from 'modules/errors/errorsReducer';

import App from './App';

const getStoreWithHistory = (initialEntries) => {
  const history = createMemoryHistory({ initialEntries });

  const mockStore = configureStore();

  const store = mockStore({
    ui: uiInitialState,
    user: userInitialState,
    data: dataInitialState,
    errors: errorsInitialState,
    router: {
      action: history.action,
      location: history.location
    }
  });

  return { store, history };
};

it('renders home page', () => {
  const div = document.createElement('div');
  const { store, history } = getStoreWithHistory(['/']);

  ReactDOM.render(
    <Provider store={store}>
      <ConnectedRouter history={history}>
        <App />
      </ConnectedRouter>
    </Provider>,
    div
  );

  ReactDOM.unmountComponentAtNode(div);
});

it('renders about page', () => {
  const div = document.createElement('div');
  const { store, history } = getStoreWithHistory(['/about']);

  ReactDOM.render(
    <Provider store={store}>
      <ConnectedRouter history={history}>
        <App />
      </ConnectedRouter>
    </Provider>,
    div
  );

  ReactDOM.unmountComponentAtNode(div);
});
