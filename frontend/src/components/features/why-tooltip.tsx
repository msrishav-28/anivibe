'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WhyTooltipProps {
    score: number;
    reason: string;
    trigger?: React.ReactNode;
}

export function WhyTooltip({ score, reason, trigger }: WhyTooltipProps) {
    const [isOpen, setIsOpen] = useState(false);

    // Holographic scanline animation variants
    const scanlineVariants = {
        initial: { y: "0%" },
        animate: {
            y: ["0%", "100%"],
            transition: {
                duration: 3,
                repeat: Infinity,
                ease: "linear"
            }
        }
    };

    return (
        <>
            <div onClick={() => setIsOpen(true)} className="cursor-pointer group">
                {trigger || (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 hover:bg-primary/20 transition-colors">
                        <Sparkles className="w-3.5 h-3.5 text-primary animate-pulse" />
                        <span className="text-xs font-medium text-primary-300">Why this?</span>
                    </div>
                )}
            </div>

            <AnimatePresence>
                {isOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsOpen(false)}
                            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                        />

                        {/* Holographic Card */}
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 10 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 10 }}
                            className="relative w-full max-w-sm overflow-hidden rounded-xl border border-primary/30 bg-black/90 shadow-[0_0_40px_rgba(139,92,246,0.3)]"
                        >
                            {/* Decorative Hologram Lines */}
                            <div className="absolute inset-0 pointer-events-none opacity-20 bg-[linear-gradient(0deg,transparent_24%,rgba(139,92,246,0.3)_25%,rgba(139,92,246,0.3)_26%,transparent_27%,transparent_74%,rgba(139,92,246,0.3)_75%,rgba(139,92,246,0.3)_76%,transparent_77%,transparent),linear-gradient(90deg,transparent_24%,rgba(139,92,246,0.3)_25%,rgba(139,92,246,0.3)_26%,transparent_27%,transparent_74%,rgba(139,92,246,0.3)_75%,rgba(139,92,246,0.3)_76%,transparent_77%,transparent)] bg-[length:4px_4px]" />

                            <div className="relative p-6 z-10">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2 text-primary">
                                        <Sparkles className="w-5 h-5" />
                                        <span className="text-sm font-bold tracking-widest uppercase">Explainability Node</span>
                                    </div>
                                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setIsOpen(false)}>
                                        <X className="w-4 h-4" />
                                    </Button>
                                </div>

                                <div className="mb-6">
                                    <div className="flex items-end gap-2 mb-2">
                                        <span className="text-4xl font-bold text-white tracking-tighter">{score}%</span>
                                        <span className="text-sm text-primary-300 font-mono mb-1.5">MATCH PROBABILITY</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${score}%` }}
                                            transition={{ duration: 1, ease: 'circOut' }}
                                            className="h-full bg-gradient-to-r from-primary to-secondary shadow-[0_0_10px_rgba(139,92,246,0.5)]"
                                        />
                                    </div>
                                </div>

                                <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                                    <p className="text-sm leading-relaxed text-white/90">
                                        {reason}
                                    </p>
                                </div>

                                <div className="mt-4 flex justify-between items-center text-[10px] text-white/30 font-mono">
                                    <span>MODEL: NEURAL_CF_V2</span>
                                    <span>CONFIDENCE: HIGH</span>
                                </div>
                            </div>

                            {/* Scanline Overlay */}
                            <motion.div
                                variants={scanlineVariants}
                                initial="initial"
                                animate="animate"
                                className="absolute top-0 left-0 w-full h-[20%] bg-gradient-to-b from-transparent via-primary/10 to-transparent pointer-events-none z-20"
                            />
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </>
    );
}
