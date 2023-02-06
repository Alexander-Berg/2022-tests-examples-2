export default function getEntityIdFromUrl(url: string) {
    return url.split('/').pop() ?? '';
}
