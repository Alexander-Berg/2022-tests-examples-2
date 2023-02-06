import { execView } from '@lib/views/execView';
import { HomeLink } from '@block/home-link/home-link.view';

export function simple() {
    return (
        <div class="root" style="display: inline-block">
            <div>
                {execView(HomeLink, {
                    mix: 'home-link_blue_yes',
                    content: 'link'
                })}
            </div>
            <div>
                {execView(HomeLink, {
                    mix: 'home-link_black_yes',
                    content: 'link'
                })}
            </div>
            <div>
                {execView(HomeLink, {
                    mix: 'home-link_gray_yes',
                    content: 'link'
                })}
            </div>
            <div>
                {execView(HomeLink, {
                    mix: 'home-link_light-blue_yes',
                    content: 'link'
                })}
            </div>
            <div>
                {execView(HomeLink, {
                    mix: 'home-link_blue_yes home-link_bold_yes',
                    content: 'link'
                })}
            </div>
        </div>
    );
}
