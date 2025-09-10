#!/usr/bin/env python3
"""
Icon Generator for System Resource Monitor Chrome App
Creates all required icon sizes from a base design.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import colorsys

def create_monitor_icon(size, output_path):
    """Create a system monitor icon at the specified size."""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions based on size
    padding = max(2, size // 16)
    monitor_width = size - (padding * 2)
    monitor_height = int(monitor_width * 0.75)
    
    # Monitor outline
    monitor_x = padding
    monitor_y = (size - monitor_height) // 2
    
    # Draw monitor screen (dark background)
    screen_rect = [monitor_x, monitor_y, monitor_x + monitor_width, monitor_y + monitor_height]
    draw.rectangle(screen_rect, fill=(26, 26, 26, 255), outline=(100, 100, 100, 255), width=max(1, size // 32))
    
    # Draw progress bars inside monitor
    bar_height = max(2, size // 16)
    bar_spacing = max(2, size // 20)
    bar_width = monitor_width - (padding * 2)
    bar_x = monitor_x + padding
    
    # Colors for different monitoring types
    colors = [
        (33, 150, 243),   # Blue - CPU
        (76, 175, 80),    # Green - Memory
        (255, 152, 0),    # Orange - Disk
        (156, 39, 176),   # Purple - GPU
    ]
    
    # Draw 4 small progress bars
    for i, color in enumerate(colors):
        bar_y = monitor_y + padding + (i * (bar_height + bar_spacing))
        if bar_y + bar_height < monitor_y + monitor_height - padding:
            # Background bar
            draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                         fill=(60, 60, 60, 255))
            
            # Progress fill (random percentage for visual effect)
            fill_width = int(bar_width * (0.3 + (i * 0.2)))
            draw.rectangle([bar_x, bar_y, bar_x + fill_width, bar_y + bar_height], 
                         fill=color)
    
    # Add small indicator dot for "active monitoring"
    dot_size = max(2, size // 20)
    dot_x = monitor_x + monitor_width - dot_size - padding
    dot_y = monitor_y + padding
    draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], 
                fill=(76, 175, 80, 255))  # Green active indicator
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f"Created icon: {output_path} ({size}x{size})")

def generate_all_icons():
    """Generate all required icon sizes for Chrome app."""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = script_dir
    
    # Required icon sizes for Chrome apps
    sizes = [16, 32, 48, 128, 256]
    
    print("Generating System Resource Monitor icons...")
    
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon-{size}.png')
        create_monitor_icon(size, output_path)
    
    print(f"\n✅ Generated {len(sizes)} icon files in {icons_dir}")
    print("\nIcon files created:")
    for size in sizes:
        print(f"  - icon-{size}.png")

if __name__ == "__main__":
    try:
        generate_all_icons()
    except ImportError as e:
        print("❌ Error: Missing required dependency")
        print("Please install Pillow: pip install Pillow")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating icons: {e}")
        sys.exit(1)
