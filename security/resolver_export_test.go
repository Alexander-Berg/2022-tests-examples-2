package podresolver

func (r *Resolver) CachedPods() []PodInfo {
	r.mu.RLock()
	defer r.mu.RUnlock()

	out := make([]PodInfo, len(r.pods))
	i := 0
	for _, p := range r.pods {
		out[i] = p
		i++
	}

	return out
}
