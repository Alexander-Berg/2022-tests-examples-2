import React from 'react';

import { createClientRender, screen } from '../../libs/testing';
import { Button } from '../Button';
import { PromoContent } from './PromoContent';
import { PromoContentTestImage } from './PromoContentTestImage';

const render = createClientRender();

describe('Promo content', () => {
  it('should throw if required slots are missing', () => {
    expect(() => render(<PromoContent />)).toThrow(
      /Required slot PromoContentTitle was not found!/,
    );

    expect(() =>
      render(
        <PromoContent>
          <PromoContent.Button>
            <Button>Press me!</Button>
          </PromoContent.Button>
        </PromoContent>,
      ),
    ).toThrow(/Required slot PromoContentTitle was not found!/);
  });

  it('should render title and button', () => {
    render(
      <PromoContent>
        <PromoContent.Title data-testid="title">Title</PromoContent.Title>
        <PromoContent.Button data-testid="button">
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('title')).toBeTruthy();
    expect(screen.getByTestId('button')).toBeTruthy();
  });

  it('should render description', () => {
    render(
      <PromoContent>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Description data-testid="description">
          Some description
        </PromoContent.Description>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('description')).toBeTruthy();
  });

  it('should render image', () => {
    render(
      <PromoContent>
        <PromoContent.Image data-testid="image">
          <PromoContentTestImage />
        </PromoContent.Image>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('image')).toBeTruthy();
  });

  it('should render supertitle', () => {
    render(
      <PromoContent>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Supertitle data-testid="supertitle">
          Some kind of supertitle
        </PromoContent.Supertitle>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('supertitle')).toBeTruthy();
  });

  it('should render secondary button', () => {
    render(
      <PromoContent>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Supertitle>Some kind of supertitle</PromoContent.Supertitle>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
        <PromoContent.SecondaryButton data-testid="secondary-button">
          <Button size="l">Some secondary action</Button>
        </PromoContent.SecondaryButton>
      </PromoContent>,
    );

    expect(screen.getByTestId('secondary-button')).toBeTruthy();
  });

  it('should render control', () => {
    render(
      <PromoContent>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Supertitle>Some kind of supertitle</PromoContent.Supertitle>
        <PromoContent.Control data-testid="control">
          <Button size="l">Optional control</Button>
        </PromoContent.Control>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
        <PromoContent.SecondaryButton>
          <Button size="l">Some secondary action</Button>
        </PromoContent.SecondaryButton>
      </PromoContent>,
    );

    expect(screen.getByTestId('control')).toBeTruthy();
  });

  it('start alignment should set data attribute', () => {
    const { container } = render(
      <PromoContent align="start">
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(container.firstElementChild).toHaveAttribute('data-align', 'start');
  });

  it('should set custom margin', () => {
    render(
      <PromoContent>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Control marginTop={42} data-testid="control">
          <Button size="l">Optional control</Button>
        </PromoContent.Control>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('control')).toHaveStyle('margin-top: 42px');
  });

  it('should set custom control align', () => {
    render(
      <PromoContent>
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Control align="start" data-testid="control">
          <Button size="l">Optional control</Button>
        </PromoContent.Control>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('control')).toHaveAttribute('data-align', 'start');
  });

  it('control alignment should be inherited by default', () => {
    render(
      <PromoContent align="start">
        <PromoContent.Title>Title</PromoContent.Title>
        <PromoContent.Control data-testid="control">
          <Button size="l">Optional control</Button>
        </PromoContent.Control>
        <PromoContent.Button>
          <Button>Press me!</Button>
        </PromoContent.Button>
      </PromoContent>,
    );

    expect(screen.getByTestId('control')).toHaveAttribute('data-align', 'start');
  });
});
