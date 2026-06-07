'use client';

import { motion } from 'framer-motion';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { useAnalytics } from '@/hooks/use-queries';

export function ActivityHeatmap() {
    const { data: analytics, isLoading } = useAnalytics();

    // Transform API data to heatmap format
    // Expected API format: [{ date: '2023-01-01', minutes: 120 }, ...]
    const heatmapData = (() => {
        if (!analytics) return [];

        // Fill last 365 days with 0
        const days = [];
        const today = new Date();
        const activityMap = new Map(analytics.map((a: any) => [a.date, a.minutes]));

        for (let i = 364; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            const minutes = activityMap.get(dateStr) || 0;

            // Calculate intensity (0-4) based on minutes
            // 0 = 0 mins
            // 1 = 1-20 mins (1 ep)
            // 2 = 21-60 mins (2-3 eps)
            // 3 = 61-120 mins (Movie/Bing)
            // 4 = 120+ mins (Hardcore)
            let intensity = 0;
            if (minutes > 0) intensity = 1;
            if (minutes > 20) intensity = 2;
            if (minutes > 60) intensity = 3;
            if (minutes > 120) intensity = 4;

            days.push({ date: dateStr, intensity, minutes });
        }
        return days;
    })();

    if (isLoading) {
        return <div className="h-[200px] w-full animate-pulse rounded-xl bg-white/5" />;
    }

    return (
        <Card variant="holo" className="w-full overflow-x-auto p-6 border-white/10">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold uppercase tracking-widest text-white/70">Sync Rate (365 Days)</h3>
                <div className="flex gap-2 items-center text-xs text-muted-foreground">
                    <span>Less</span>
                    <div className="flex gap-1">
                        <div className={`h-3 w-3 rounded-sm ${intensityColors[0]}`} />
                        <div className={`h-3 w-3 rounded-sm ${intensityColors[2]}`} />
                        <div className={`h-3 w-3 rounded-sm ${intensityColors[4]}`} />
                    </div>
                    <span>More</span>
                </div>
            </div>

            <div className="flex gap-1 min-w-max">
                {/* 53 Columns x 7 Rows */}
                {Array.from({ length: 53 }).map((_, colIndex) => (
                    <div key={colIndex} className="flex flex-col gap-1">
                        {Array.from({ length: 7 }).map((_, rowIndex) => {
                            const dayIndex = colIndex * 7 + rowIndex;
                            if (dayIndex >= heatmapData.length) return null;

                            const day = heatmapData[dayIndex];
                            if (!day) return null;

                            return (
                                <TooltipProvider key={day.date} delayDuration={0}>
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                transition={{ delay: dayIndex * 0.002, duration: 0.2 }}
                                                className={cn(
                                                    "h-3 w-3 rounded-sm transition-all duration-300 hover:scale-125 hover:z-10",
                                                    intensityColors[day.intensity as keyof typeof intensityColors],
                                                    day.intensity > 2 && "shadow-glow"
                                                )}
                                            />
                                        </TooltipTrigger>
                                        <TooltipContent side="top">
                                            <span className="font-mono">{day.date}</span>: <span className="text-primary-400 font-bold">{day.minutes} min</span>
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                            );
                        })}
                    </div>
                ))}
            </div>
        </Card>
    );
}
