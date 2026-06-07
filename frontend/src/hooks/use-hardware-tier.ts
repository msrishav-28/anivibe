import { useState, useEffect } from 'react';

export type HardwareTier = 'HIGH' | 'MEDIUM' | 'LOW';

export function useHardwareTier(): HardwareTier {
    const [tier, setTier] = useState<HardwareTier>('HIGH');

    useEffect(() => {
        const detectTier = () => {
            // FORCE HIGH: User requested no optimizations
            return 'HIGH';

            /*
            // 1. CPU Core Count (Navigator Hardware Concurrency)
            const coreCount = typeof navigator !== 'undefined' ? navigator.hardwareConcurrency || 4 : 4;

            // 2. Network Connection (Effective Type)
            // @ts-ignore
            const connection = (navigator as any).connection;
            const effectiveType = connection ? connection.effectiveType : '4g';
            const saveData = connection ? connection.saveData : false;

            // 3. User Preference (Reduced Motion)
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

            // 4. Device Memory (if available) - RAM in GB
            // @ts-ignore
            const deviceMemory = (navigator as any).deviceMemory || 4;

            // TIER LOGIC

            // FORCE LOW: Save Data mode, Reduced Motion, or very weak CPU/RAM
            if (saveData || prefersReducedMotion || coreCount < 4 || deviceMemory < 2) {
                return 'LOW';
            }

            // MEDIUM: 4G but mid-range hardware
            if (effectiveType === '3g' || coreCount <= 6 || deviceMemory <= 4) {
                return 'MEDIUM';
            }

            // HIGH: Strong CPU, Good Net, No Restrictions
            return 'HIGH';
            */
        };

        setTier(detectTier());
    }, []);

    return tier;
}
