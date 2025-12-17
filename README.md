# Thermoelement Converter

A GUI application for converting thermocouple voltage (mV) to temperature (Celsius) and vice versa.


<img width="900" height="726" alt="image" src="/entity/examples/pictures/Screenshot_gui.png" />


## Disclaimer

This project was heavily developed with the assistance of **Claude Code** (Anthropic's AI coding assistant). Major contributions include:
- Migration from PySimpleGUI to Dear PyGui
- Implementation of custom thermocouple conversion library using NIST ITS-90 coefficients
- Security fixes and code quality improvements
- Virtual environment setup and dependency management
- Documentation and testing

Original GUI concept and implementation by Alexander Kononov (2018).

## Features

- **Bidirectional Conversion**: Convert mV to °C and °C to mV
- **Standard Thermocouple Support**: B, E, J, K, N, R, S, T (using NIST ITS-90 coefficients)
- **Custom Calibration Data**: Support for external calibration files
- **Adjustable Reference Temperature**: Compensate for non-ice-point reference junctions
- **Interactive Plotting**:
  - Real-time plot generation with both lines and data point markers
  - Multiple plot overlay (compare different types/settings simultaneously)
  - Clear individual or all plots
- **Smart Boundary Handling**:
  - Automatic adjustment of out-of-range values
  - Reference temperature compensation in range validation
  - User-friendly notifications when values are corrected
- **Modern GPU-Accelerated UI**: Built with Dear PyGui for smooth performance

## Installation

### Prerequisites

- Python 3.14 (or compatible version)
- `uv` package manager (recommended)

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

1. Clone or download this repository

2. Create a virtual environment:
```bash
uv venv
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

4. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

### Running the Application

With virtual environment activated:
```bash
python th_converter_dpg.py
```

### Basic Operations

1. **Select Thermocouple Type**: Choose from the dropdown (K, J, T, E, N, R, S, B, or custom)
2. **Set Reference Temperature**: Enter the reference junction temperature (default: 23°C)
3. **Convert Values**:
   - Enter mV value and click "Convert mV -> °C"
   - Enter °C value and click "Convert °C -> mV"
4. **Plot Data**:
   - Set Min mV, Max mV, and Step size
   - Click "Generate Plot" to see the mV vs °C curve with data points
   - Check "Keep previous plots" to overlay multiple plots for comparison
   - Click "Clear All Plots" to remove all plot lines

### Advanced Plotting Features

**Comparing Multiple Settings:**
1. Check the "Keep previous plots" checkbox
2. Generate a plot with your first settings (e.g., Type K, Tref=0°C)
3. Change settings (e.g., switch to Type J or change Tref to 23°C)
4. Click "Generate Plot" again
5. Repeat to overlay as many plots as needed

**Each plot shows:**
- Connected lines for trend visualization
- Individual data point markers showing calculation density
- Legend with Type, Reference Temperature, and voltage range

**Automatic Boundary Correction:**
- If you enter values outside the valid range for a thermocouple type, they are automatically adjusted
- An information dialog shows what was corrected and why
- The plot generates immediately with the corrected values
- Takes reference temperature into account for accurate range validation

### Supported Thermocouple Types

| Type | Temperature Range | Common Use |
|------|------------------|------------|
| K | -270°C to 1372°C | General purpose, most common |
| J | -210°C to 1200°C | Older, reduced atmospheres |
| T | -270°C to 400°C | Low temperature, high accuracy |
| E | -270°C to 1000°C | Highest EMF output |
| N | -270°C to 1300°C | High temperature, oxidation resistant |
| S | -50°C to 1768°C | High temperature, noble metal |
| R | -50°C to 1768°C | High temperature, noble metal |
| B | 0°C to 1820°C | Very high temperature |

## Custom Calibration Data

To use custom calibration data:

1. Place `.pkl` files in the `interpolated_data/` directory
2. Add the calibration name to `config/default.cfg` in the `types` field
3. Select your custom type from the dropdown

### Creating Custom Calibration Files

Use `import_th_data.py` as a template to create calibration data from CSV files.

## Project Structure

```
thermoelement_converter/
├── th_converter_dpg.py      # Main application (Dear PyGui)
├── thermocouples.py          # Thermocouple conversion library (NIST coefficients)
├── import_th_data.py         # Data import/interpolation script
├── requirements.txt          # Python dependencies
├── config/
│   └── default.cfg          # Configuration file
├── interpolated_data/       # Custom calibration data
└── .venv/                   # Virtual environment (created by uv)
```

## Technical Details

### Conversion Formulas

The application uses NIST ITS-90 polynomial coefficients for standard thermocouple types. Each type has specific polynomial coefficients for:
- Temperature to EMF (voltage) conversion
- EMF to temperature conversion

### Reference Junction Compensation

All conversions account for reference junction temperature using:
```
EMF_measured = EMF(T_hot, 0°C) - EMF(T_ref, 0°C)
```

Where:
- `T_hot` is the measuring junction temperature
- `T_ref` is the reference junction temperature
- Default reference is 0°C (ice point)

## Dependencies

- **dearpygui** - Modern GPU-accelerated GUI framework
- **numpy** - Numerical computations
- **scipy** - Optimization and interpolation
- **matplotlib** - Data visualization (for import script)
- **pandas** - Data handling (for import script)

## Migration from PySimpleGUI

This project was migrated from PySimpleGUI to Dear PyGui to avoid commercial licensing issues. The old version (`th_converter_0.2.py`) is still available but uses deprecated PySimpleGUI APIs.

### Key Improvements in New Version

**UI Framework:**
- Free, open-source Dear PyGui framework
- GPU-accelerated rendering for smooth performance
- Built-in plotting capabilities (no external matplotlib windows)
- Non-modal information dialogs for better UX

**Thermocouple Library:**
- Custom implementation using NIST ITS-90 polynomial coefficients
- No dependency on outdated `thermocouples_reference` library
- Full NumPy 2.x compatibility
- Voltage range validation with reference temperature compensation

**Code Quality & Security:**
- Fixed resource leaks (all file operations use context managers)
- Specific exception handling (no bare `except:` clauses)
- Cross-platform path handling with `os.path.join()`
- Input validation and automatic boundary correction

**Enhanced Features:**
- Plot overlay capability for comparing multiple configurations
- Both line and scatter plot visualization
- Automatic out-of-range value correction
- Reference temperature-aware range validation
- Better error messages with context

## Authors and Contributions

- **Original GUI Author**: Alexander Kononov (2018)
- **Major Refactoring and Modernization**: Claude Code (Anthropic AI Assistant, 2025)
  - Migration to Dear PyGui
  - Implementation of NIST-based thermocouple library
  - Security and code quality improvements
  - Documentation and testing
- **Thermocouple Coefficients**: NIST ITS-90 Standard (public domain)

## Troubleshooting

### Plot Range Issues

**Why are my max values being adjusted?**

When you set a reference temperature other than 0°C, the valid input range changes. For example:
- Type K valid absolute range: -5.891 to 54.886 mV
- At Tref = 23°C (adds ~0.886 mV offset)
- Valid input range becomes: -6.777 to 54.0 mV

The application automatically adjusts your values and shows an information dialog explaining the correction.

**Step size and data points**

- Smaller step sizes (e.g., 0.1 mV) create denser plots with more data points
- Larger step sizes (e.g., 1.0 mV) create sparser plots
- Data point markers clearly show where calculations were performed

### Virtual Environment

If you encounter import errors, ensure you're in the virtual environment:

```bash
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Debug Mode

The application outputs debug information to the terminal. Run from terminal to see:
- Value parsing and validation
- Range adjustments
- Plot generation progress
- Any errors with detailed stack traces

## Known Behaviors

- **Reference Temperature Impact**: Higher reference temperatures reduce the maximum measurable voltage for a given thermocouple type
- **Floating Point Precision**: Values are automatically clamped to avoid floating-point arithmetic errors at boundaries
- **Plot Overlay**: No limit on number of overlaid plots, but too many may affect readability
- **Type B Restriction**: Type B thermocouples have no negative voltage range (starts at 0.291 mV)

## License

This project uses standard NIST thermocouple coefficients which are in the public domain.

