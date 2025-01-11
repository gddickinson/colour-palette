import numpy as np
import matplotlib.pyplot as plt
import colorsys
from typing import List, Tuple, Dict
from dataclasses import dataclass
import random
from enum import Enum
import json

class HarmonyType(Enum):
    COMPLEMENTARY = "complementary"
    TRIADIC = "triadic"
    ANALOGOUS = "analogous"
    SPLIT_COMPLEMENTARY = "split_complementary"
    TETRADIC = "tetradic"
    MONOCHROMATIC = "monochromatic"

@dataclass
class Color:
    h: float  # Hue (0-1)
    s: float  # Saturation (0-1)
    v: float  # Value/Brightness (0-1)
    
    def to_rgb(self) -> Tuple[float, float, float]:
        """Convert HSV to RGB"""
        return colorsys.hsv_to_rgb(self.h, self.s, self.v)
    
    def to_hex(self) -> str:
        """Convert to hex color code"""
        rgb = self.to_rgb()
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
    
    @classmethod
    def from_rgb(cls, r: float, g: float, b: float) -> 'Color':
        """Create Color from RGB values"""
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return cls(h, s, v)

class ColorPaletteGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.color_meanings = {
            "red": "energy, passion, excitement",
            "blue": "trust, peace, stability",
            "green": "growth, harmony, freshness",
            "yellow": "happiness, optimism, creativity",
            "purple": "royalty, luxury, mystery",
            "orange": "enthusiasm, adventure, confidence"
        }
    
    def generate_base_color(self, temperature: str = "neutral") -> Color:
        """Generate a base color with given temperature preference"""
        if temperature == "warm":
            h = random.uniform(0.95, 0.15)  # Red to Yellow
        elif temperature == "cool":
            h = random.uniform(0.45, 0.65)  # Green to Blue
        else:
            h = random.random()
        
        s = random.uniform(0.6, 0.9)  # Medium to high saturation
        v = random.uniform(0.7, 0.9)  # Medium to high value
        
        return Color(h, s, v)
    
    def adjust_color(self, color: Color, 
                    hue_shift: float = 0.0,
                    sat_adjust: float = 0.0,
                    val_adjust: float = 0.0) -> Color:
        """Adjust a color's HSV values"""
        new_h = (color.h + hue_shift) % 1.0
        new_s = np.clip(color.s + sat_adjust, 0, 1)
        new_v = np.clip(color.v + val_adjust, 0, 1)
        return Color(new_h, new_s, new_v)
    
    def generate_harmony(self, base_color: Color, 
                        harmony_type: HarmonyType,
                        num_colors: int = 5) -> List[Color]:
        """Generate a color harmony based on the specified type"""
        colors = [base_color]
        
        if harmony_type == HarmonyType.COMPLEMENTARY:
            colors.append(self.adjust_color(base_color, hue_shift=0.5))
            
        elif harmony_type == HarmonyType.TRIADIC:
            colors.extend([
                self.adjust_color(base_color, hue_shift=1/3),
                self.adjust_color(base_color, hue_shift=2/3)
            ])
            
        elif harmony_type == HarmonyType.ANALOGOUS:
            for i in range(1, num_colors):
                shift = 0.05 * i
                colors.append(self.adjust_color(base_color, hue_shift=shift))
                
        elif harmony_type == HarmonyType.SPLIT_COMPLEMENTARY:
            complement = (base_color.h + 0.5) % 1.0
            colors.extend([
                Color(complement - 0.05, base_color.s, base_color.v),
                Color(complement + 0.05, base_color.s, base_color.v)
            ])
            
        elif harmony_type == HarmonyType.TETRADIC:
            colors.extend([
                self.adjust_color(base_color, hue_shift=0.25),
                self.adjust_color(base_color, hue_shift=0.5),
                self.adjust_color(base_color, hue_shift=0.75)
            ])
            
        elif harmony_type == HarmonyType.MONOCHROMATIC:
            for i in range(1, num_colors):
                sat_adjust = -0.15 * i
                val_adjust = 0.1 * i
                colors.append(self.adjust_color(base_color, 
                                             sat_adjust=sat_adjust,
                                             val_adjust=val_adjust))
        
        return colors[:num_colors]
    
    def analyze_palette(self, colors: List[Color]) -> Dict:
        """Analyze the characteristics of a color palette"""
        rgb_colors = [c.to_rgb() for c in colors]
        
        # Calculate average brightness
        brightness = np.mean([sum(rgb) / 3 for rgb in rgb_colors])
        
        # Calculate color temperature
        warmth = np.mean([rgb[0] - rgb[2] for rgb in rgb_colors])
        
        # Calculate contrast
        brightnesses = [sum(rgb) / 3 for rgb in rgb_colors]
        contrast = max(brightnesses) - min(brightnesses)
        
        return {
            "brightness": brightness,
            "temperature": "warm" if warmth > 0 else "cool",
            "contrast": contrast,
            "harmony_level": min(1.0, contrast * 2)  # Simple harmony metric
        }
    
    def visualize_palette(self, colors: List[Color], 
                         title: str = "Color Palette",
                         filename: str = "palette.png"):
        """Create a visual representation of the color palette"""
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                      gridspec_kw={'height_ratios': [3, 1]})
        
        # Main color blocks
        for i, color in enumerate(colors):
            ax1.add_patch(plt.Rectangle((i, 0), 1, 1, color=color.to_rgb()))
        
        # Add color information
        for i, color in enumerate(colors):
            rgb = color.to_rgb()
            ax1.text(i + 0.5, 0.5, f"RGB: {tuple(int(x*255) for x in rgb)}\nHex: {color.to_hex()}",
                    ha='center', va='center',
                    color='white' if sum(rgb) < 1.5 else 'black')
        
        ax1.set_xlim(0, len(colors))
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        # Create gradient blend
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, gradient))
        
        # Blend between colors
        blended = np.zeros((2, 256, 3))
        for i in range(len(colors) - 1):
            start_color = np.array(colors[i].to_rgb())
            end_color = np.array(colors[i + 1].to_rgb())
            segment = np.linspace(start_color, end_color, 256 // (len(colors) - 1))
            start_idx = i * (256 // (len(colors) - 1))
            end_idx = (i + 1) * (256 // (len(colors) - 1))
            blended[:, start_idx:end_idx] = segment.T.reshape(3, -1).reshape(3, 1, -1).transpose(1, 2, 0)
        
        ax2.imshow(blended, extent=[0, len(colors), 0, 0.1])
        ax2.axis('off')
        
        plt.suptitle(title, fontsize=16, y=0.95)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
    def generate_palette(self, 
                        temperature: str = "neutral",
                        harmony_type: HarmonyType = HarmonyType.COMPLEMENTARY,
                        num_colors: int = 5) -> Dict:
        """Generate a complete color palette with analysis"""
        base_color = self.generate_base_color(temperature)
        colors = self.generate_harmony(base_color, harmony_type, num_colors)
        
        analysis = self.analyze_palette(colors)
        
        # Create output data
        palette_data = {
            "colors": [color.to_hex() for color in colors],
            "rgb_values": [tuple(int(x*255) for x in color.to_rgb()) for color in colors],
            "hsv_values": [(color.h, color.s, color.v) for color in colors],
            "analysis": analysis,
            "harmony_type": harmony_type.value,
            "temperature": temperature
        }
        
        return palette_data

def generate_and_save_palettes(num_palettes: int = 5, seed: int = None):
    """Generate multiple palettes with different harmonies"""
    generator = ColorPaletteGenerator(seed)
    
    all_palettes = {}
    for harmony in HarmonyType:
        print(f"\nGenerating {harmony.value} palette...")
        
        palette_data = generator.generate_palette(
            harmony_type=harmony,
            num_colors=5
        )
        
        # Visualize the palette
        colors = [Color.from_rgb(r/255, g/255, b/255) 
                 for r, g, b in palette_data["rgb_values"]]
        generator.visualize_palette(
            colors,
            title=f"{harmony.value.title()} Color Harmony",
            filename=f"palette_{harmony.value}.png"
        )
        
        all_palettes[harmony.value] = palette_data
    
    # Save all palette data
    with open("palette_data.json", "w") as f:
        json.dump(all_palettes, f, indent=2)
    
    print("\nGenerated palettes for all harmony types!")
    print("Check the PNG files for visualizations and palette_data.json for complete data.")

if __name__ == "__main__":
    generate_and_save_palettes(seed=42)  # Use seed for reproducibility