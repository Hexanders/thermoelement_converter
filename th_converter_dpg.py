import dearpygui.dearpygui as dpg
from thermocouples import thermocouples
import configparser
import os
from _pickle import load
from scipy.optimize import newton
from numpy import arange

# Load configuration
config = configparser.ConfigParser()
config_path = 'config/default.cfg'
with open(config_path, 'r') as config_file:
    config.read_file(config_file)

default_thType = config.get('DEFAULT', 'default_type')
types = config.get('DEFAULT', 'types').split(',')

# Global state
current_th_type = None
external_data_trigger = False
plot_counter = 0


def load_external_data(mv_value, data_name, inverse=False):
    """Load and process external thermocouple calibration data."""
    path = os.path.join(
        config.get('DEFAULT', 'externalDataPath'),
        f'{data_name}.pkl'
    )

    if not os.path.exists(path):
        raise FileNotFoundError(f"Calibration file not found: {path}")

    with open(path, "rb") as f:
        data = load(f)

    if inverse:
        find_x = lambda x: data[1](x) - mv_value
        th_info, th_data = data[0], newton(find_x, 0.04)
    else:
        th_info, th_data = data[0], data[1](mv_value)

    return th_info, th_data


def update_th_type():
    """Update the current thermocouple type based on user selection."""
    global current_th_type, external_data_trigger

    selected = dpg.get_value("th_type_combo")

    try:
        current_th_type = thermocouples[selected]
        external_data_trigger = False
    except KeyError:
        # External data type
        current_th_type = selected
        external_data_trigger = True


def convert_mv_to_celsius(sender, app_data, user_data):
    """Convert millivolts to Celsius."""
    try:
        update_th_type()
        mv_value = float(dpg.get_value("input_mv"))
        tref = float(dpg.get_value("input_tref"))

        if external_data_trigger:
            celsius = load_external_data(mv_value, current_th_type)[1]
        else:
            celsius = current_th_type.inverse_CmV(mv_value, Tref=tref)

        dpg.set_value("input_celsius", f"{celsius:.2f}")

    except ValueError as e:
        show_error("Please enter valid numeric values.")
    except FileNotFoundError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Conversion error: {str(e)}")


def convert_celsius_to_mv(sender, app_data, user_data):
    """Convert Celsius to millivolts."""
    try:
        update_th_type()
        celsius_value = float(dpg.get_value("input_celsius"))
        tref = float(dpg.get_value("input_tref"))

        if external_data_trigger:
            mv = load_external_data(celsius_value, current_th_type, inverse=True)[1]
        else:
            mv = current_th_type.emf_mVC(celsius_value, Tref=tref)

        dpg.set_value("input_mv", f"{mv:.4f}")

    except ValueError as e:
        show_error("Please enter valid numeric values.")
    except FileNotFoundError as e:
        show_error(str(e))
    except Exception as e:
        show_error(f"Conversion error: {str(e)}")


def plot_mv_vs_celsius(sender, app_data, user_data):
    """Generate and display mV vs Celsius plot."""
    global plot_counter

    try:
        update_th_type()

        # Read input values
        try:
            mv_min_str = dpg.get_value("input_mv_min")
            mv_max_str = dpg.get_value("input_mv_max")
            step_str = dpg.get_value("input_step")
            tref_str = dpg.get_value("input_tref")

            print(f"DEBUG: Read values - Min: '{mv_min_str}', Max: '{mv_max_str}', Step: '{step_str}', Tref: '{tref_str}'")

            mv_min = float(mv_min_str)
            mv_max = float(mv_max_str)
            step = float(step_str)
            tref = float(tref_str)

            print(f"DEBUG: Converted to - Min: {mv_min}, Max: {mv_max}, Step: {step}, Tref: {tref}")
        except (ValueError, TypeError) as e:
            print(f"DEBUG: Conversion error: {e}")
            show_error(f"Please enter valid numeric values in all fields.\nError: {str(e)}")
            return

        if mv_min >= mv_max:
            show_error("Min mV must be less than Max mV")
            return

        if step <= 0:
            show_error("Step must be positive")
            return

        # Get valid voltage range for the thermocouple type
        try:
            if not external_data_trigger:
                valid_min, valid_max = current_th_type.get_voltage_range()
                print(f"DEBUG: Valid range for {dpg.get_value('th_type_combo')}: {valid_min} to {valid_max} mV")

                # Account for reference temperature offset
                emf_ref = current_th_type._temp_to_emf(tref)
                print(f"DEBUG: Reference EMF at {tref}°C: {emf_ref} mV")

                # Adjust valid range to account for reference junction
                valid_min_adjusted = valid_min - emf_ref
                valid_max_adjusted = valid_max - emf_ref
                print(f"DEBUG: Adjusted range (accounting for Tref): {valid_min_adjusted} to {valid_max_adjusted} mV")
            else:
                # For external data, use wide range (could be improved with metadata)
                valid_min_adjusted, valid_max_adjusted = -10.0, 80.0
                print(f"DEBUG: Using external data range: {valid_min_adjusted} to {valid_max_adjusted} mV")
        except (AttributeError, TypeError) as e:
            # If we can't get the range, use a wide default
            print(f"DEBUG: Error getting range: {e}, using default")
            valid_min_adjusted, valid_max_adjusted = -10.0, 80.0

        # Clamp values to valid range
        original_min = mv_min
        original_max = mv_max
        mv_min = max(mv_min, valid_min_adjusted)
        mv_max = min(mv_max, valid_max_adjusted)

        print(f"DEBUG: After clamping - Min: {mv_min}, Max: {mv_max}")

        # Update input fields with corrected values
        values_adjusted = False
        if original_min != mv_min:
            print(f"DEBUG: Updating Min field from {original_min} to {mv_min}")
            dpg.set_value("input_mv_min", str(round(mv_min, 3)))
            values_adjusted = True
        if original_max != mv_max:
            print(f"DEBUG: Updating Max field from {original_max} to {mv_max}")
            dpg.set_value("input_mv_max", str(round(mv_max, 3)))
            values_adjusted = True

        # Notify user if values were adjusted
        if values_adjusted:
            print(f"DEBUG: Showing info dialog")
            adjusted_msg = f"Values adjusted to valid range for Type {dpg.get_value('th_type_combo')}:\n\n"
            if original_min != mv_min:
                adjusted_msg += f"Min mV: {original_min:.3f} → {mv_min:.3f} mV\n"
            if original_max != mv_max:
                adjusted_msg += f"Max mV: {original_max:.3f} → {mv_max:.3f} mV\n"
            if not external_data_trigger:
                adjusted_msg += f"\nValid input range (with Tref={tref}°C): {valid_min_adjusted:.3f} to {valid_max_adjusted:.3f} mV"
            else:
                adjusted_msg += f"\nValid range: {valid_min_adjusted:.3f} to {valid_max_adjusted:.3f} mV"
            show_info(adjusted_msg)

        # Final check after adjustment
        if mv_min >= mv_max:
            print(f"DEBUG: Final check failed - Min {mv_min} >= Max {mv_max}")
            if not external_data_trigger:
                show_error(f"Invalid range. Valid input range for Type {dpg.get_value('th_type_combo')} with Tref={tref}°C: {valid_min_adjusted:.3f} to {valid_max_adjusted:.3f} mV")
            else:
                show_error(f"Invalid range. Valid range: {valid_min_adjusted:.3f} to {valid_max_adjusted:.3f} mV")
            return

        print(f"DEBUG: Starting plot generation with range {mv_min} to {mv_max}")

        # Calculate data points
        x_data = []
        y_data = []

        print(f"DEBUG: Calculating data points from {mv_min} to {mv_max} with step {step}")

        # Use a small epsilon to avoid boundary issues
        epsilon = 1e-6
        effective_max = mv_max - epsilon

        for i in arange(mv_min, effective_max + step, step):
            # Ensure we don't exceed the actual max
            if i > effective_max:
                i = mv_max - epsilon

            # Skip if we've gone past the limit
            if i > mv_max:
                break

            # Skip duplicates
            if x_data and abs(x_data[-1] - i) < step * 0.01:
                continue

            print(f"DEBUG: Processing point {len(x_data)+1}: i={i:.10f}, mv_max={mv_max:.10f}")
            x_data.append(i)

            try:
                if external_data_trigger:
                    y_data.append(load_external_data(i, current_th_type)[1])
                else:
                    y_data.append(current_th_type.inverse_CmV(i, Tref=tref))
            except Exception as e:
                print(f"DEBUG: Error at point i={i}: {e}")
                raise

        print(f"DEBUG: Calculated {len(x_data)} data points")

        # Check if we should keep previous plots
        keep_plots = dpg.get_value("keep_plots_checkbox")

        if not keep_plots:
            # Clear all previous plots
            clear_all_plots()
            print(f"DEBUG: Cleared previous plots")

        # Add new plot series with unique tag
        plot_counter += 1
        series_tag = f"plot_series_{plot_counter}"
        scatter_tag = f"plot_scatter_{plot_counter}"
        label_text = f"Tref: {tref}°C | Type: {dpg.get_value('th_type_combo')} | Range: {mv_min:.1f}-{mv_max:.1f}mV"

        print(f"DEBUG: Adding plot series {plot_counter}")

        # Add line series
        dpg.add_line_series(
            x_data,
            y_data,
            label=label_text,
            parent="y_axis",
            tag=series_tag
        )

        # Add scatter series (data points) - no label to avoid duplicate in legend
        dpg.add_scatter_series(
            x_data,
            y_data,
            parent="y_axis",
            tag=scatter_tag
        )

        dpg.fit_axis_data("x_axis")
        dpg.fit_axis_data("y_axis")

        print(f"DEBUG: Plot generation completed successfully!")

    except ValueError as e:
        print(f"DEBUG: ValueError in plot generation: {e}")
        show_error(f"Please enter valid numeric values for plot parameters.\nError: {str(e)}")
    except FileNotFoundError as e:
        print(f"DEBUG: FileNotFoundError: {e}")
        show_error(str(e))
    except Exception as e:
        print(f"DEBUG: Exception in plot generation: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        show_error(f"Plot error: {str(e)}")


def clear_all_plots(sender=None, app_data=None, user_data=None):
    """Clear all plot series from the graph."""
    global plot_counter

    # Delete all plot series (both lines and scatter points)
    for i in range(1, plot_counter + 1):
        series_tag = f"plot_series_{i}"
        scatter_tag = f"plot_scatter_{i}"
        if dpg.does_item_exist(series_tag):
            dpg.delete_item(series_tag)
        if dpg.does_item_exist(scatter_tag):
            dpg.delete_item(scatter_tag)

    plot_counter = 0


def show_error(message):
    """Display error dialog."""
    if dpg.does_item_exist("error_modal"):
        dpg.delete_item("error_modal")

    with dpg.window(label="Error", modal=True, show=True, tag="error_modal",
                    no_resize=True, pos=[300, 200]):
        dpg.add_text(message)
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("error_modal"))


def show_info(message):
    """Display information dialog."""
    if dpg.does_item_exist("info_modal"):
        dpg.delete_item("info_modal")

    with dpg.window(label="Information", modal=False, show=True, tag="info_modal",
                    no_resize=True, pos=[300, 200], autosize=True):
        dpg.add_text(message, wrap=400)
        dpg.add_separator()
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("info_modal"))


def show_about(sender, app_data, user_data):
    """Display about dialog."""
    if dpg.does_item_exist("about_modal"):
        dpg.delete_item("about_modal")

    with dpg.window(label="About", modal=True, show=True, tag="about_modal",
                    no_resize=True, pos=[250, 150], width=500):
        dpg.add_text("Simple GUI for Thermoelement Converter\n")
        dpg.add_text("GUI Author: Alexander Kononov")
        dpg.add_text("Year: 2018")
        dpg.add_text("Updated to Dear PyGui: 2025\n")
        dpg.add_text("The real work was done by User:Nanite @ wikipedia")
        dpg.add_text("in thermocouples_reference.py")
        dpg.add_text("https://pypi.python.org/pypi/thermocouples_reference")
        dpg.add_separator()
        dpg.add_button(label="OK", width=75, callback=lambda: dpg.delete_item("about_modal"))


def main():
    """Initialize and run the application."""
    dpg.create_context()
    dpg.create_viewport(title="Thermoelement Converter - mV <-> °C", width=900, height=700)

    with dpg.window(label="Thermoelement Converter", tag="primary_window"):

        # Menu bar
        with dpg.menu_bar():
            with dpg.menu(label="Help"):
                dpg.add_menu_item(label="About", callback=show_about)

        # Thermocouple type and reference temperature
        with dpg.group(horizontal=True):
            dpg.add_text("Type:")
            dpg.add_combo(
                types,
                default_value=default_thType,
                tag="th_type_combo",
                width=150
            )
            dpg.add_text("  Reference T [°C]:")
            dpg.add_input_text(
                tag="input_tref",
                default_value="23",
                width=100
            )

        dpg.add_separator()

        # Conversion section
        with dpg.group():
            dpg.add_text("Conversion", color=(100, 200, 255))

            with dpg.group(horizontal=True):
                dpg.add_text("mV:")
                dpg.add_input_text(
                    tag="input_mv",
                    default_value="1",
                    width=200
                )
                dpg.add_button(
                    label="Convert mV -> °C",
                    callback=convert_mv_to_celsius
                )

            with dpg.group(horizontal=True):
                dpg.add_text("°C:")
                dpg.add_input_text(
                    tag="input_celsius",
                    default_value="47",
                    width=200
                )
                dpg.add_button(
                    label="Convert °C -> mV",
                    callback=convert_celsius_to_mv
                )

        dpg.add_separator()

        # Plot section
        with dpg.collapsing_header(label="Graph: mV vs °C", default_open=True):

            with dpg.group(horizontal=True):
                dpg.add_text("Min mV:")
                dpg.add_input_text(
                    tag="input_mv_min",
                    default_value="1",
                    width=100
                )
                dpg.add_text("  Max mV:")
                dpg.add_input_text(
                    tag="input_mv_max",
                    default_value="5",
                    width=100
                )
                dpg.add_text("  Step [mV]:")
                dpg.add_input_text(
                    tag="input_step",
                    default_value="1",
                    width=100
                )

            with dpg.group(horizontal=True):
                dpg.add_button(label="Generate Plot", callback=plot_mv_vs_celsius)
                dpg.add_checkbox(
                    label="Keep previous plots",
                    tag="keep_plots_checkbox",
                    default_value=False
                )
                dpg.add_button(label="Clear All Plots", callback=clear_all_plots)

            # Plot window
            with dpg.plot(label="mV vs °C", height=350, width=-1):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="mV", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="°C", tag="y_axis")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
