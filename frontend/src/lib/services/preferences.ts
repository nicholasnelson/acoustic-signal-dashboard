import { browser } from '$app/environment';

export interface DashboardPreferences {
	recentAlertLimit: number;
}

const STORAGE_KEY = 'acoustic-monitoring-preferences-v2';

export const defaultDashboardPreferences: DashboardPreferences = {
	recentAlertLimit: 3
};

export function getDashboardPreferences(): DashboardPreferences {
	if (!browser) return { ...defaultDashboardPreferences };
	try {
		const raw = window.localStorage.getItem(STORAGE_KEY);
		if (!raw) return { ...defaultDashboardPreferences };
		const parsed = JSON.parse(raw) as Partial<DashboardPreferences>;
		return {
			recentAlertLimit: [3, 5, 10].includes(Number(parsed.recentAlertLimit))
				? Number(parsed.recentAlertLimit)
				: defaultDashboardPreferences.recentAlertLimit
		};
	} catch {
		return { ...defaultDashboardPreferences };
	}
}

export function saveDashboardPreferences(preferences: DashboardPreferences): void {
	if (!browser) return;
	window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
}

export function resetDashboardPreferences(): DashboardPreferences {
	if (browser) window.localStorage.removeItem(STORAGE_KEY);
	return { ...defaultDashboardPreferences };
}
