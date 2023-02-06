export function newApplicationTemplate(appName: string): any {
    const applicationTemplate = {
        application: {
            name: `${appName}`,
            category: 88,
            time_zone_name: "Europe/Moscow",
            hide_address: false,
            gdpr_agreement_accepted: true,
        },
    };
    return applicationTemplate;
}
