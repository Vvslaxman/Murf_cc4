#!/usr/bin/env python3
"""
Create simple extension icons for SocialCast
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple microphone icon"""
    # Create a new image with a gradient background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(size):
        # Blue to purple gradient
        r = int(102 + (y / size) * 118)  # 102 to 220
        g = int(126 + (y / size) * 74)   # 126 to 200
        b = int(234 + (y / size) * 21)   # 234 to 255
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Draw microphone icon
    mic_width = int(size * 0.6)
    mic_height = int(size * 0.8)
    mic_x = (size - mic_width) // 2
    mic_y = (size - mic_height) // 2
    
    # Microphone body (rectangle with rounded corners)
    draw.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
        radius=int(size * 0.1),
        fill=(255, 255, 255, 255)
    )
    
    # Microphone stand
    stand_width = int(mic_width * 0.3)
    stand_height = int(mic_height * 0.2)
    stand_x = mic_x + (mic_width - stand_width) // 2
    stand_y = mic_y + mic_height
    draw.rectangle(
        [stand_x, stand_y, stand_x + stand_width, stand_y + stand_height],
        fill=(255, 255, 255, 255)
    )
    
    # Save the icon
    img.save(filename, 'PNG')
    print(f"Created icon: {filename}")

def main():
    """Create all required icons"""
    # Ensure icons directory exists
    os.makedirs('icons', exist_ok=True)
    
    # Create icons for different sizes
    sizes = [16, 48, 128]
    
    for size in sizes:
        filename = f'icons/icon{size}.png'
        create_icon(size, filename)
    
    print("All icons created successfully!")

if __name__ == "__main__":
    main()
