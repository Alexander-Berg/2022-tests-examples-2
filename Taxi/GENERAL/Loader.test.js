import React from 'react';
import { shallow } from 'enzyme';
import toJson from 'enzyme-to-json';

import Loader from './Loader';

test('Modal does not crash', () => {
  const tree = shallow(
    <Loader />
  );

  expect(toJson(tree)).toMatchSnapshot();
});
