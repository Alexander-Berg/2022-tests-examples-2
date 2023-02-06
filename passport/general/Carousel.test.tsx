import React from 'react';

import { Carousel, CarouselItem } from '.';
import { createClientRender } from '../../libs/testing';

describe('Carousel', () => {
  const render = createClientRender();

  test('snapshot', () => {
    const result = render(
      <Carousel data-id="id" className="Test">
        <CarouselItem>item 1</CarouselItem>
        <CarouselItem className="Test">item 2</CarouselItem>
        <CarouselItem data-id="id">item 3</CarouselItem>
      </Carousel>,
    );

    expect(result.asFragment()).toMatchSnapshot();
  });
});
