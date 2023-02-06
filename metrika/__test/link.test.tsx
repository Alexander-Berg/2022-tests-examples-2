import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Link } from '../link';
import { LinkProps, LinkSize, LinkView } from '../link-props';
import { All } from '../link.stories';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';

const title = 'link';
const onClick = jest.fn();
const onFocus = jest.fn();
const onBlur = jest.fn();

function renderLink(props?: Partial<LinkProps>): void {
    render(
        <Link size={LinkSize.S20} view={LinkView.Base} onClick={onClick} {...props}>
            {title}
        </Link>
    );
}

describe('Link', () => {
    it('screenshot', async () => {
        await makeScreenshot(<All />);
    });

    describe('logic', () => {
        beforeEach(() => {
            onClick.mockClear();
            onFocus.mockClear();
            onBlur.mockClear();
        });

        it('should call onClick', () => {
            renderLink({ onClick });
            userEvent.click(screen.getByText(title));
            expect(onClick).toBeCalled();
        });

        it('should call onFocus', () => {
            renderLink({ onFocus });
            fireEvent.focus(screen.getByText(title));
            expect(onFocus).toBeCalled();
        });

        it('should call onBlur', () => {
            renderLink({ onBlur });
            const link = screen.getByText(title);
            fireEvent.focus(link);
            fireEvent.blur(link);
            expect(onBlur).toBeCalled();
        });
    });
});
