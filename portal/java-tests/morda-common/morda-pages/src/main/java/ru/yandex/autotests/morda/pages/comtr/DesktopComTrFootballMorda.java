package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopComTrFootballMorda extends ComTrMorda<DesktopComTrFootballMorda>
        implements AbstractDesktopMorda<DesktopComTrFootballMorda> {

    private FootballClub club;

    private DesktopComTrFootballMorda(FootballClub club, String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        this.club = club;
    }

    public static DesktopComTrFootballMorda desktopComTrFoot(FootballClub club) {
        return desktopComTrFoot(club, "production");
    }

    public static DesktopComTrFootballMorda desktopComTrFoot(FootballClub club, String environment) {
        return desktopComTrFoot(club, "https", environment);
    }

    public static DesktopComTrFootballMorda desktopComTrFoot(FootballClub club, String scheme, String environment) {
        return new DesktopComTrFootballMorda(club, scheme, "www", environment);
    }

    public static List<DesktopComTrFootballMorda> getDefaultList(String environment) {
        return Stream.of(FootballClub.values())
                .map(e -> desktopComTrFoot(e, environment))
                .collect(Collectors.toList());
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).path(club.getValue()).build();
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_COMTR_FOOTBALL;
    }

    @Override
    public DesktopComTrFootballMorda me() {
        return this;
    }

    public enum FootballClub {
        BJK("bjk"),
        GS("gs");

        private String value;

        FootballClub(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }
}
