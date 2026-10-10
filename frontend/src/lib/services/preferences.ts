import { browser } from '$app/environment';

export interface DashboardPreferences {
	recentAlertLimit: number;
	showTechnicalDetails: boolean;
	autoAnalyseOnOpen: boolean;
}

const STORAGE_KEY = 'acoustic-monitoring-preferences';

export const defaultDashboardPreferences: DashboardPreferences = {
	recentAlertLimit: 3,
	showTechnicalDetails: false,
	autoAnalyseOnOpen: true
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
				: defaultDashboardPreferences.recentAlertLimit,
			showTechnicalDetails:
				typeof parsed.showTechnicalDetails === 'boolean'
					? parsed.showTechnicalDetails
					: defaultDashboardPreferences.showTechnicalDetails,
			autoAnalyseOnOpen:
				typeof parsed.autoAnalyseOnOpen === 'boolean'
					? parsed.autoAnalyseOnOpen
					: defaultDashboardPreferences.autoAnalyseOnOpen
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
