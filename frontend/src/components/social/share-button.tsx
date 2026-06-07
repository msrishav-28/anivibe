"use client";

import { useState } from "react";
import { Copy, Check, Share2, Twitter, Facebook } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

interface ShareButtonProps {
    title: string;
    url?: string; // Optional, defaults to current page
    text?: string;
}

export function ShareButton({ title, url, text }: ShareButtonProps) {
    const [copied, setCopied] = useState(false);

    // Use current URL if not provided
    const shareUrl = typeof window !== "undefined" ? (url || window.location.href) : "";
    const shareText = text || `Check out ${title} on AniVibe!`;

    const handleCopy = () => {
        navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        toast.success("Link copied to clipboard!");
        setTimeout(() => setCopied(false), 2000);
    };

    const handleTwitter = () => {
        window.open(
            `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
            "_blank"
        );
    };

    const handleFacebook = () => {
        window.open(
            `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
            "_blank"
        );
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                    <Share2 className="h-4 w-4" />
                    Share
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-black/90 backdrop-blur-xl border-white/10">
                <DropdownMenuLabel>Share to...</DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-white/10" />

                <DropdownMenuItem onClick={handleCopy} className="cursor-pointer focus:bg-white/10">
                    {copied ? <Check className="mr-2 h-4 w-4 text-green-500" /> : <Copy className="mr-2 h-4 w-4" />}
                    Copy Link
                </DropdownMenuItem>

                <DropdownMenuItem onClick={handleTwitter} className="cursor-pointer focus:bg-white/10">
                    <Twitter className="mr-2 h-4 w-4 text-blue-400" />
                    Twitter
                </DropdownMenuItem>

                <DropdownMenuItem onClick={handleFacebook} className="cursor-pointer focus:bg-white/10">
                    <Facebook className="mr-2 h-4 w-4 text-blue-600" />
                    Facebook
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
