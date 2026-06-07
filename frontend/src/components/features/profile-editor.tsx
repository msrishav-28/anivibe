'use client';

import { useState, useEffect } from 'react';
import { useUpdateProfile } from '@/hooks/use-queries';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useAuthStore } from '@/store/auth-store';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Save } from 'lucide-react';

export function ProfileEditor() {
    const { user, updateUser: updateStoreUser } = useAuthStore();
    const { mutate: updateProfile, isPending } = useUpdateProfile();

    const [formData, setFormData] = useState({
        display_name: '',
        bio: '',
        avatar_url: '',
    });

    useEffect(() => {
        if (user) {
            setFormData({
                display_name: user.display_name || '',
                bio: user.bio || '',
                avatar_url: user.avatar_url || '',
            });
        }
    }, [user]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateProfile(formData, {
            onSuccess: (updatedUser) => {
                toast.success('Identity rewritten successfully.');
                updateStoreUser(formData); // Optimistically update store or use returned data
            },
            onError: () => {
                toast.error('Failed to rewrite identity.');
            }
        });
    };

    if (!user) return null;

    return (
        <Card className="max-w-xl mx-auto bg-black/40 border-white/10 backdrop-blur-md">
            <CardHeader>
                <CardTitle className="text-xl font-heading text-white">Neural Identity Settings</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <Label htmlFor="display_name" className="text-white/70">Display Name</Label>
                        <Input
                            id="display_name"
                            value={formData.display_name}
                            onChange={(e) => setFormData(prev => ({ ...prev, display_name: e.target.value }))}
                            className="bg-white/5 border-white/10 focus:border-primary/50"
                            placeholder="OtakuKing99"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="bio" className="text-white/70">Bio (Manifesto)</Label>
                        <Textarea
                            id="bio"
                            value={formData.bio}
                            onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
                            className="bg-white/5 border-white/10 focus:border-primary/50 min-h-[100px]"
                            placeholder="I search for the ultimate waifu..."
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="avatar_url" className="text-white/70">Avatar URL</Label>
                        <Input
                            id="avatar_url"
                            value={formData.avatar_url}
                            onChange={(e) => setFormData(prev => ({ ...prev, avatar_url: e.target.value }))}
                            className="bg-white/5 border-white/10 focus:border-primary/50"
                            placeholder="https://example.com/anime-pfp.jpg"
                        />
                    </div>

                    <div className="flex justify-end pt-4">
                        <Button type="submit" disabled={isPending} className="w-full sm:w-auto">
                            {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                            Save Changes
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
}
