'use client';

import { Toast } from '@/components/ui/toast';
import { useToast } from '@/hooks/use-toast';
import { AnimatePresence, motion } from 'framer-motion';

export function Toaster() {
  const { toasts } = useToast();

  return (
    <div className="fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]">
      <AnimatePresence>
        {toasts.map((t) => {
          const { id, title, description, ...props } = t as any;
          return (
            <motion.div
              key={id}
              initial={{ opacity: 0, x: 20, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
              layout
              className="mb-2"
            >
              <Toast
                title={title || ''}
                description={description || ''}
                variant={props.type || 'default'}
                {...props}
              />
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
