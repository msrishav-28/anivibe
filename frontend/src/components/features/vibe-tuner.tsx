'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, Image as ImageIcon, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useImageSearch } from '@/hooks/use-queries';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export function VibeTuner() {
    const [query, setQuery] = useState('');
    const [moodColor, setMoodColor] = useState('rgba(139,92,246,0.3)'); // Default Spirit Purple

    const router = useRouter();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { mutate: searchImage, isPending: isUploading } = useImageSearch();

    // Dynamic Mood Logic
    useEffect(() => {
        const lower = query.toLowerCase();
        if (lower.includes('sad') || lower.includes('lonely') || lower.includes('rain')) {
            setMoodColor('rgba(59,130,246,0.6)'); // Blue
        } else if (lower.includes('hype') || lower.includes('action') || lower.includes('fight')) {
            setMoodColor('rgba(239,68,68,0.6)'); // Red
        } else if (lower.includes('chill') || lower.includes('healing') || lower.includes('nature')) {
            setMoodColor('rgba(16,185,129,0.6)'); // Green
        } else if (lower.includes('dark') || lower.includes('horror')) {
            setMoodColor('rgba(0,0,0,0.8)'); // Void
        } else {
            setMoodColor('rgba(139,92,246,0.3)'); // Default
        }
    }, [query]);

    const handleSearch = () => {
        if (query) {
            router.push(`/search?q=${encodeURIComponent(query)}`);
        }
    };

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        searchImage(file, {
            onSuccess: (data: any) => {
                toast.success(`Visual Search Complete! Found ${data.length} matches.`);
                // For demo/audit, we just redirect or show results.
                // Redirecting to search with a flag
                router.push('/search?q=Visual%20Search%20Result');
            },
            onError: (err: any) => {
                toast.error('Visual Search Failed');
                console.error(err);
            }
        });
    };

    return (
        <div className="mx-auto max-w-3xl relative z-20">
            <motion.div
                className="relative group"
                animate={{
                    boxShadow: `0 0 20px ${moodColor}`,
                }}
                transition={{ duration: 0.5 }}
            >
                {/* Pulse Effect */}
                <motion.div
                    className="absolute -inset-1 rounded-full opacity-20 blur-lg transition duration-500 pointer-events-none"
                    animate={{
                        backgroundColor: moodColor,
                        scale: [1, 1.02, 1],
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />

                <Input
                    placeholder="Type a feeling... 'cyberpunk rain', 'healing slice of life'"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    leftIcon={<Search className="h-5 w-5" />}
                    className="h-16 text-lg bg-black/40 backdrop-blur-xl border-white/10 rounded-full pl-12 pr-32 focus-visible:ring-0 focus-visible:border-white/20 transition-all placeholder:text-muted-foreground/50"
                />

                <div className="absolute right-2 top-2 flex gap-2">
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleImageUpload}
                    />
                    <Button
                        size="icon"
                        variant="ghost"
                        className="h-12 w-12 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        title="Search by Image"
                    >
                        {isUploading ? (
                            <Loader2 className="h-5 w-5 text-white animate-spin" />
                        ) : (
                            <ImageIcon className="h-5 w-5 text-white" />
                        )}
                    </Button>
                    <Button
                        size="icon"
                        variant="ghost"
                        className="h-12 w-12 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                        onClick={handleSearch}
                        style={{
                            boxShadow: `0 0 10px ${moodColor}`
                        }}
                    >
                        <Search className="h-5 w-5 text-white" />
                    </Button>
                </div>
            </motion.div>

            {/* Neural Status Indicators */}
            <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm text-muted-foreground/60 font-mono">
                <span className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse"></span>
                    CLIP Vision Model Active
                </span>
                <span className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
                    BERT Semantic Analysis Ready
                </span>
            </div>
        </div>
    );
}
