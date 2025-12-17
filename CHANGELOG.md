# Changelog

All notable changes to the Thermoelement Converter project.

## [Unreleased] - 2025-12-18

### Added
- **Dear PyGui Migration**: Complete migration from PySimpleGUI to Dear PyGui
  - GPU-accelerated rendering
  - Built-in plotting (no external matplotlib windows)
  - Modern, responsive UI

- **Custom Thermocouple Library** (`thermocouples.py`)
  - NIST ITS-90 polynomial coefficients for all standard types (K, J, T, E, N, S, R, B)
  - Replaced dependency on `thermocouples_reference` library
  - NumPy 2.x compatible
  - Voltage range validation with `get_voltage_range()` method

- **Plot Enhancement Features**
  - Data point markers on plots (scatter series)
  - "Keep previous plots" toggle for comparing multiple configurations
  - "Clear All Plots" button
  - Plot legend shows Type, Tref, and voltage range
  - Each plot shows both lines (trends) and markers (actual data points)

- **Automatic Boundary Correction**
  - Out-of-range values automatically adjusted to valid limits
  - Reference temperature compensation in range validation
  - Information dialogs explain what was adjusted and why
  - Prevents errors from invalid voltage inputs

- **Development Environment**
  - Virtual environment setup with `uv` package manager
  - `requirements.txt` with pinned dependencies
  - `.gitignore` for Python and IDE files

- **Documentation**
  - Comprehensive README.md with usage examples
  - Troubleshooting section
  - Known behaviors documentation
  - Disclaimer about Claude Code's contributions

### Fixed
- **Security Issues**
  - Resource leaks: All file operations now use context managers
  - Bare `except:` clauses replaced with specific exception types
  - File existence validation before opening
  - Proper error handling with user-friendly messages

- **Code Quality**
  - Cross-platform path handling with `os.path.join()`
  - Removed deprecated PySimpleGUI API calls
  - Fixed typos in user-facing text
  - Removed commented-out code

- **Thermocouple Conversion Bugs**
  - Fixed voltage range selection bug causing temperature drops between 2-4 mV
  - Added `inv_voltage_ranges` parameter to properly select inverse polynomials
  - Reference temperature offset now accounted for in range validation
  - Floating-point precision handling at voltage boundaries

### Changed
- Main application file: `th_converter_0.2.py` → `th_converter_dpg.py`
- UI framework: PySimpleGUI → Dear PyGui
- Thermocouple library: `thermocouples_reference` → custom `thermocouples.py`
- NumPy requirement: `<2.0` → `>=1.20.0` (supports NumPy 2.x)
- Package manager: pip → uv (recommended)

### Removed
- Dependency on `thermocouples_reference` (outdated, NumPy 1.x only)
- Dependency on specific NumPy version constraint
- Deprecated PySimpleGUI API usage

## [0.2] - 2018

### Initial Release by Alexander Kononov
- PySimpleGUI-based interface
- mV to °C and °C to mV conversion
- Support for standard thermocouple types
- Reference temperature adjustment
- Basic matplotlib plotting
- Custom calibration data support

---

## Version Naming

- **0.2**: Original PySimpleGUI version (2018)
- **Unreleased**: Dear PyGui migration with major improvements (2025)
