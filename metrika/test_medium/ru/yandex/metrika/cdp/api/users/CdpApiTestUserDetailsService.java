package ru.yandex.metrika.cdp.api.users;

import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;

import ru.yandex.metrika.rbac.metrika.MetrikaRbac;

public class CdpApiTestUserDetailsService implements UserDetailsService {

    private final MetrikaRbac metrikaRbac;

    public CdpApiTestUserDetailsService(MetrikaRbac metrikaRbac) {
        this.metrikaRbac = metrikaRbac;
    }


    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        var details = TestUsers.usersByUsername.get(username);
        if (details == null) {
            throw new UsernameNotFoundException(username);
        }
        metrikaRbac.checkUsers(details.getUid());
        return details;
    }
}
