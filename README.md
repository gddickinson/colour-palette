# Color Palette Generator

A Python-based creative color palette generator that creates harmonious color combinations using established color theory principles. The generator produces both visual representations and detailed color data, perfect for designers, artists, and developers.

## Features

- **Multiple Harmony Types**:
  - Complementary (two colors opposite each other)
  - Triadic (three colors equally spaced)
  - Analogous (colors adjacent to each other)
  - Split-complementary (base color and two colors adjacent to its complement)
  - Tetradic (four colors forming a rectangle)
  - Monochromatic (variations in saturation and brightness)

- **Advanced Color Analysis**:
  - Color temperature calculation
  - Brightness analysis
  - Contrast ratio measurement
  - Harmony level assessment

- **Rich Visualizations**:
  - Color blocks with RGB/Hex information
  - Smooth gradient transitions
  - Comprehensive color data display

- **Multiple Output Formats**:
  - PNG visualizations
  - JSON data export
  - RGB/HSV/Hex color codes

## Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd color-palette-generator
```

2. Install required dependencies:
```bash
pip install numpy matplotlib
```

## Usage

### Basic Usage

Generate palettes for all harmony types:

```python
python color_palette_generator.py
```

This will:
1. Create visualization files for each harmony type (`palette_*.png`)
2. Save complete palette data (`palette_data.json`)
3. Print progress information

### Programmatic Usage

```python
from color_palette_generator import ColorPaletteGenerator, HarmonyType

# Create generator with optional seed
generator = ColorPaletteGenerator(seed=42)

# Generate a specific palette
palette_data = generator.generate_palette(
    temperature="neutral",
    harmony_type=HarmonyType.COMPLEMENTARY,
    num_colors=5
)

# Create visualization
colors = [Color.from_rgb(r/255, g/255, b/255) 
         for r, g, b in palette_data["rgb_values"]]
generator.visualize_palette(
    colors,
    title="Custom Palette",
    filename="custom_palette.png"
)
```

## Output Files

### PNG Visualizations
- Separate files for each harmony type
- Shows color blocks with RGB/Hex values
- Includes gradient transitions
- Names format: `palette_[harmony_type].png`

### JSON Data
- Complete palette information in `palette_data.json`
- Includes for each palette:
  - Hex color codes
  - RGB values
  - HSV values
  - Color analysis
  - Harmony type
  - Temperature characteristics

## Color Theory Implementation

### Temperature Control
- Warm colors: Reds, oranges, yellows
- Cool colors: Blues, greens, purples
- Neutral: Full spectrum available

### Harmony Rules
- **Complementary**: Maximum contrast, high energy
- **Triadic**: Balanced, vibrant
- **Analogous**: Harmonious, comfortable
- **Split-complementary**: High contrast, less tension
- **Tetradic**: Rich, complex combinations
- **Monochromatic**: Subtle, sophisticated

## Customization

### Modifying Color Generation

```python
# Custom temperature preference
palette = generator.generate_palette(temperature="warm")

# Specific number of colors
palette = generator.generate_palette(num_colors=3)

# Custom harmony type
palette = generator.generate_palette(
    harmony_type=HarmonyType.TRIADIC
)
```

### Adjusting Visualization

```python
generator.visualize_palette(
    colors,
    title="Custom Title",
    filename="custom_name.png"
)
```

## Analysis Features

The generator provides detailed analysis of each palette:

- **Brightness**: Average luminosity of the palette
- **Temperature**: Overall warm/cool classification
- **Contrast**: Range of light to dark values
- **Harmony**: Calculated harmony metric

## Contributing

Areas for potential enhancement:

- Additional harmony types
- More color theory metrics
- Enhanced visualization options
- Color accessibility analysis
- Pattern generation
- UI/Web interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using numpy and matplotlib
- Color theory principles from traditional art and design
- HSV color space calculations for intuitive color manipulation
