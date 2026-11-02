import math

def size_wind_tunnel_from_ball(ball_dia, unit='in', ball_role='large'):
    """
    Computes all tunnel dimensions, optical acrylic thickness, blower architecture,
    streamlines, and honeycomb parameters based strictly on an input ball diameter.

    Parameters:
    - ball_dia: float, diameter of the test ball
    - unit: 'in' or 'mm'
    - ball_role: 'large' (max test ball at 10% blockage) or 'small' (min test ball hitting >= 3 lines)
    """
    IN_TO_M = 0.0254
    M_TO_IN = 1.0 / IN_TO_M
    M3S_TO_CFM = 2118.88

    # Air constants (20 C, nominal ~3700 ft El Paso elevation)
    rho = 1.184      # kg/m^3
    mu = 1.82e-5     # Pa*s
    nu = mu / rho    # m^2/s
    U_opt = 1.4      # m/s (ideal velocity for razor-sharp, non-diffusing mist)

    # Normalize input to inches and meters
    if unit.lower() in ['mm', '2']:
        d_in = ball_dia / 25.4
        d_m = ball_dia / 1000.0
        unit_str = "mm"
    else:
        d_in = ball_dia
        d_m = ball_dia * IN_TO_M
        unit_str = "in"

    # [1] AERODYNAMIC BLOCKAGE & CHAMBER SIZING
    if ball_role.lower() in ['large', '1', 'max']:
        D_large_in = d_in
        D_large_m = d_m

        # 10% Blockage Constraint: W = H >= D * sqrt(pi / 0.40)
        W_exact_in = D_large_in * math.sqrt(math.pi / 0.40)
        # Round up to nearest clean quarter-inch (0.25")
        W_in = math.ceil(W_exact_in * 4.0) / 4.0
        H_in = W_in

        # Paired Small Ball: Sized to show wake contrast while intercepting >= 3 lines
        # Target streamline pitch approx 12-16 mm (0.50 - 0.60 in)
        target_pitch_in = 0.55
        num_streamlines = max(7, int(round(H_in / target_pitch_in)) - 1)
        actual_pitch_in = H_in / (num_streamlines + 1)
        D_small_in = max(3.0 * actual_pitch_in, D_large_in * 0.70)
        D_small_m = D_small_in * IN_TO_M
    else:
        D_small_in = d_in
        D_small_m = d_m

        # Small ball must intercept >= 3 streamlines => pitch <= D_small / 3
        actual_pitch_in = D_small_in / 3.0
        # Paired large ball scaled ~1.45x
        D_large_in = D_small_in * 1.45
        D_large_m = D_large_in * IN_TO_M

        W_exact_in = D_large_in * math.sqrt(math.pi / 0.40)
        W_in = math.ceil(W_exact_in * 4.0) / 4.0
        H_in = W_in
        num_streamlines = max(7, int(round(H_in / actual_pitch_in)) - 1)
        actual_pitch_in = H_in / (num_streamlines + 1)

    W_m = W_in * IN_TO_M
    H_m = H_in * IN_TO_M
    A_tunnel_in2 = W_in * H_in
    A_tunnel_m2 = W_m * H_m

    # [2] DYNAMIC LENGTH SCALING
    # Test section length: 2.2x to 2.4x the width to allow full wake cavity development
    L_test_section_in = round(W_in * 2.2, 1)
    L_bell_in = round(0.5 * W_in, 1)
    L_honeycomb_in = 1.5 if W_in <= 7.0 else (2.0 if W_in <= 10.0 else 2.5)
    L_settle_in = 1.25 if W_in <= 7.0 else 1.75
    L_diffuser_in = round(1.2 * W_in, 1)
    L_fan_housing_in = 4.0 if W_in <= 6.0 else 7.5
    L_total_in = L_bell_in + L_honeycomb_in + L_settle_in + L_test_section_in + L_diffuser_in + L_fan_housing_in

    # [3] BLOCKAGE & REYNOLDS NUMBERS
    block_large = ((math.pi / 4.0) * (D_large_in ** 2)) / A_tunnel_in2 * 100.0
    block_small = ((math.pi / 4.0) * (D_small_in ** 2)) / A_tunnel_in2 * 100.0
    Re_large = (U_opt * D_large_m) / nu
    Re_small = (U_opt * D_small_m) / nu

    # [4] STRUCTURAL ACRYLIC SIZING (Plate deflection under negative pressure)
    # Suction pressure delta_P scales with tunnel size and honeycomb loss
    delta_p_pa = 35.0 if W_in <= 6.0 else (55.0 if W_in <= 10.0 else 80.0)
    E_acrylic_pa = 3.0e9  # 3.0 GPa for Cast Acrylic
    allowable_deflection_m = 0.0004  # 0.4 mm max deflection to avoid optical lens effect
    alpha = 0.044  # Roark's factor for ~1:2 plate aspect
    b_m = min(W_m, L_test_section_in * IN_TO_M)
    t_req_m = ((alpha * delta_p_pa * (b_m**4)) / (E_acrylic_pa * allowable_deflection_m)) ** (1.0/3.0)
    t_req_in = t_req_m * M_TO_IN

    if t_req_in <= 0.20:
        acrylic_stock = '1/4" (6.0 mm) Cast Acrylic'
    elif t_req_in <= 0.33:
        acrylic_stock = '3/8" (9.5 mm) Cast Acrylic'
    else:
        acrylic_stock = '1/2" (12.7 mm) Cast Acrylic'

    # [5] VOLUMETRIC AIRFLOW & BLOWER ARCHITECTURE
    Q_cfm = U_opt * A_tunnel_m2 * M3S_TO_CFM

    if Q_cfm <= 55.0:
        blower_rec = "Single 120mm High-Static Pressure Fan (e.g. Arctic P12 Max)"
        blower_power = "12V 2A DC Power Brick / Manual PWM Knob"
    elif Q_cfm <= 110.0:
        blower_rec = 'Dual 120mm/140mm Fans OR 4" Inline Duct Fan (AC Infinity Cloudline S4)'
        blower_power = "120V AC Direct Line / EC Variable Speed Dial"
    elif Q_cfm <= 260.0:
        blower_rec = '6" Inline Mixed-Flow Duct Fan (AC Infinity Cloudline S6 or Dayton Blower)'
        blower_power = "120V AC Direct Line / EC Motor Speed Controller"
    else:
        blower_rec = '8" Inline Mixed-Flow Duct Blower (AC Infinity Cloudline S8)'
        blower_power = "120V AC Direct Line / EC Motor Speed Controller"

    # [6] FLOW VISUALIZATION & FOG GENERATION
    comb_hole_dia_mm = 2.5
    actual_pitch_mm = actual_pitch_in * 25.4
    wall_offset_in = round(actual_pitch_in * 1.2, 2)

    if num_streamlines <= 11:
        fog_unit = "1x Single-Head 12V Ultrasonic Mist Puck (~400 mL/hr)"
        fog_tank = "1.5 to 2.0 Liters"
    elif num_streamlines <= 18:
        fog_unit = "1x 3-Head Commercial Ultrasonic Mist Generator (120V AC Transformer, ~1,200 mL/hr)"
        fog_tank = "3.5 to 5.0 Liters"
    else:
        fog_unit = "1x 5-Head or 6-Head Commercial Mist Generator (120V AC, ~2,500 mL/hr)"
        fog_tank = "6.0 to 8.0 Liters"

    # [7] FLOW CONDITIONING (HONEYCOMB)
    hc_dia_mm = 5.0 if W_in <= 7.0 else 6.5
    hc_depth_mm = hc_dia_mm * 7.0  # 7:1 L/D ratio
    hc_depth_in = hc_depth_mm / 25.4

    # PRINT COMPREHENSIVE 6-SECTION SPECIFICATION REPORT
    print("=" * 72)
    print("      SPONDER LABS: MASTER PARAMETRIC WIND TUNNEL SIZING ENGINE      ")
    print("=" * 72)
    print(f"INPUT SPECIFICATION: {ball_role.upper()} Sphere = {d_in:.3f}\" ({d_m*1000:.1f} mm)")
    print("-" * 72)

    print("[1] TEST SECTION & FOOTPRINT GEOMETRY:")
    print(f"    * Test Section Cross-Section : {W_in:.2f}\" W x {H_in:.2f}\" H ({W_m*1000:.0f} x {H_m*1000:.0f} mm)")
    print(f"    * Test Section Frontal Area  : {A_tunnel_in2:.1f} sq.in ({A_tunnel_m2*1e4:.0f} cm^2)")
    print(f"    * Test Section Length        : {L_test_section_in:.1f}\" ({L_test_section_in*25.4:.0f} mm)")
    print(f"    * Overall Machine Footprint  : {L_total_in:.1f}\" Length x {W_in + 4.0:.1f}\" Depth")
    print(f"      - Bellmouth Intake Length  : {L_bell_in:.1f}\"")
    print(f"      - Honeycomb Thickness      : {L_honeycomb_in:.2f}\"")
    print(f"      - Settling Buffer Gap      : {L_settle_in:.2f}\"")
    print(f"      - Diffuser Transition Duct : {L_diffuser_in:.1f}\"")
    print(f"      - Blower Housing Length    : {L_fan_housing_in:.1f}\"")

    print("\n[2] MODEL TESTING CAPABILITIES (10% AERODYNAMIC BLOCKAGE):")
    print(f"    * Maximum Sphere Diameter    : {D_large_in:.2f}\" ({D_large_m*1000:.1f} mm)")
    print(f"      - Blockage Ratio           : {block_large:.1f}% (Constraint <= 10.0% -> PASS)")
    print(f"      - Reynolds Number          : {Re_large:,.0f} @ {U_opt} m/s")
    print(f"    * Minimum Sphere Diameter    : {D_small_in:.2f}\" ({D_small_m*1000:.1f} mm) [>= 3 line hits]")
    print(f"      - Blockage Ratio           : {block_small:.1f}%")
    print(f"      - Reynolds Number          : {Re_small:,.0f} @ {U_opt} m/s")
    print(f"    * Max Scale Aircraft Wingspan: {W_in * 0.70:.1f}\" (Leaves 15% wall boundary margin)")
    print(f"    * Max Toy Vehicle Width      : {W_in * 0.40:.1f}\"")

    print("\n[3] OPTICAL & STRUCTURAL ACRYLIC SPECIFICATIONS:")
    print(f"    * Operating Negative Pressure: ~{delta_p_pa:.0f} Pa ({delta_p_pa/9.81:.1f} mmH2O)")
    print(f"    * Computed Minimum Thickness : {t_req_in:.3f}\" ({t_req_m*1000:.2f} mm)")
    print(f"    * RECOMMENDED MATERIAL       : {acrylic_stock}")
    print(f"      -> Reason: Prevents optical lens-bowing under continuous suction.")

    print("\n[4] POWER & BLOWER ARCHITECTURE:")
    print(f"    * Target Core Velocity       : {U_opt} m/s ({U_opt*2.237:.1f} mph) [Non-diffusing sweet spot]")
    print(f"    * Operating Airflow Required : {Q_cfm:.1f} CFM under load")
    print(f"    * RECOMMENDED BLOWER         : {blower_rec}")
    print(f"    * Power Supply Architecture  : {blower_power}")

    print("\n[5] FLOW VISUALIZATION (COMB & FOG GENERATOR):")
    print(f"    * Number of Streamlines      : {num_streamlines} distinct lines")
    print(f"    * Nozzle Pitch (Spacing)     : {actual_pitch_in:.2f}\" ({actual_pitch_mm:.1f} mm center-to-center)")
    print(f"    * Comb Hole Port Diameter    : {comb_hole_dia_mm:.1f} mm (0.10\")")
    print(f"    * Wall Clearance Offset      : {wall_offset_in:.2f}\" (Avoids glass boundary layer)")
    print(f"    * RECOMMENDED FOG SYSTEM     : {fog_unit}")
    print(f"    * Water Reservoir Tank Size  : {fog_tank}")

    print("\n[6] FLOW CONDITIONING (HONEYCOMB):")
    print(f"    * Honeycomb Cell Diameter    : {hc_dia_mm:.1f} mm (Hexagonal matrix)")
    print(f"    * Honeycomb Depth (L/D ~ 7:1): {hc_depth_mm:.1f} mm ({hc_depth_in:.2f}\")")
    print(f"    * Cell Wall Thickness        : 0.8 mm (2 printer nozzle passes)")
    print("=" * 72)

def interactive_runner():
    print("=" * 72)
    print("     SPONDER LABS: INTERACTIVE WIND TUNNEL SIZING ENGINE")
    print("=" * 72)
    try:
        val_str = input("Enter the diameter of your test sphere (e.g. 1.68 for golf ball, 2.5, 3.0): ").strip()
        ball_val = float(val_str) if val_str else 1.68
        unit_str = input("Units? (in or mm) [default: in]: ").strip().lower()
        unit = 'mm' if unit_str in ['mm', '2'] else 'in'
        role_str = input("Is this your (1) LARGE sphere or (2) SMALL sphere? [default: 1]: ").strip()
        role = 'small' if role_str in ['2', 'small'] else 'large'
    except (EOFError, ValueError):
        ball_val = 1.68
        unit = 'in'
        role = 'large'
    size_wind_tunnel_from_ball(ball_val, unit, role)

if __name__ == "__main__":
    import sys
    # Ignore Jupyter/Colab internal flags (like '-f')
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if len(args) > 0:
        try:
            dia = float(args[0])
            unit = args[1] if len(args) > 1 else "in"
            role = args[2] if len(args) > 2 else "large"
            size_wind_tunnel_from_ball(dia, unit, role)
        except ValueError:
            interactive_runner()
    else:
        interactive_runner()
