## Cost per image:

Gemini Flash 2.5 image gen (likely gemini-2.5-flash-image or gemini-2.5-flash-image-preview)
Gemini Flash 3.1 image gen (likely gemini-3.1-flash-image-preview, aka Nano Banana 2)
With Nano Banana Pro (Gemini 3 Pro Image Preview)

Pricing is from the official Gemini API docs (as of early March 2026), in paid tier (free tier generally doesn't support image generation or has heavy restrictions). Costs are in USD, pay-as-you-go.
Gemini 2.5 Flash Image Generation

Model: gemini-2.5-flash-image (or preview variants)
Cost per image: $0.039 (for standard up to 1024x1024px outputs)
Details: Output images consume a fixed 1290 tokens equivalent, priced at $30 per 1M output tokens → $0.039/image.
Input (text prompt or reference image): $0.30 per 1M tokens (negligible per request, e.g., ~$0.0003 for a short prompt).
Batch mode: Often 50% off → ~$0.0195 per image.
This is the most cost-effective Flash-tier image gen option.

Gemini 3.1 Flash Image Generation

Model: gemini-3.1-flash-image-preview (aka Nano Banana 2, the "Flash" speed version for efficient/high-volume use)
Cost per image — varies by resolution (output priced at $60 per 1M tokens for images; input is $0.50 per 1M tokens for text/image):
0.5K / 512px: ~$0.045 per image (747 tokens)
1K / ~1024x1024px: ~$0.067 per image (1120 tokens)
2K / 2048x2048px: ~$0.101 per image (1680 tokens)
4K / 4096x4096px: ~$0.151 per image (2520 tokens)

Notes: Some sources show slight discrepancies (e.g., input $0.25 in one doc view vs $0.50), but the latest/official leans toward the higher end for preview. This is more expensive than 2.5 Flash but supports higher resolutions and newer features (better text rendering, editing, etc.).

Nano Banana Pro (Gemini 3 Pro Image Preview)

Model: gemini-3-pro-image-preview (the "Pro" version for higher quality/creativity/studio-level control)
Cost per image — higher-end, priced at $120 per 1M tokens for image outputs (input $2.00 per 1M tokens for text/image):
1K–2K images (~1024x1024px to 2048x2048px): ~$0.134 per image (around 1120 tokens)
4K images (up to 4096x4096px): ~$0.24 per image (around 2000 tokens)

This is the premium tier for best quality (sharper details, better consistency, advanced editing), but significantly more expensive than the Flash variants.