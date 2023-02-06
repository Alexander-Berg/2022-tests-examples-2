import React from 'react';
import ReactDOM from 'react-dom';
import configureStore from 'redux-mock-store';
import { createMemoryHistory } from 'history';

import { uiInitialState } from 'modules/ui/reducer';
import { profileInitialState } from 'modules/profile/reducer';
import { offersInitialState } from 'sections/offers/reducer';

import App from './App';

it('renders without crashing', () => {
  const div = document.createElement('div');
  const history = createMemoryHistory();

  const mockStore = configureStore();

  const store = mockStore({
    ui: uiInitialState,
    profile: profileInitialState,
    router: {
      action: history.action,
      location: history.location
    },
    offers: offersInitialState
  });

  ReactDOM.render(<App history={history} store={store} />, div);
  ReactDOM.unmountComponentAtNode(div);
});
