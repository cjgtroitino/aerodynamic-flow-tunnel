import math
import sys


def scale_pitch_mechanism(
    plane_weight, unit_weight="g", tunnel_width=None, unit_len="in"
):
  """Parametrically scales all mechanical linkage components based on aircraft weight.

  Parameters:
  - plane_weight: float, mass/weight of the model
  - unit_weight: 'g' (grams), 'kg', 'oz', 'lb'
  - tunnel_width: float, wind tunnel test section width (optional, auto-derives
  if None)
  - unit_len: 'in' or 'mm'
  """
  G_TO_KG = 0.001
  OZ_TO_KG = 0.0283495
  LB_TO_KG = 0.453592
  IN_TO_MM = 25.4

  u_w = str(unit_weight).strip().lower()
  if u_w in ["g", "grams"]:
    m_kg = plane_weight * G_TO_KG
  elif u_w in ["oz", "ounces"]:
    m_kg = plane_weight * OZ_TO_KG
  elif u_w in ["lb", "lbs", "pound", "pounds"]:
    m_kg = plane_weight * LB_TO_KG
  elif u_w in ["kg", "kilograms"]:
    m_kg = plane_weight
  else:
    m_kg = plane_weight * G_TO_KG

  # PLA Material Properties (conservative design values for 3D-printed parts)
  E_pla_mpa = 2500.0  # Modulus of Elasticity (MPa)
  sigma_yield_mpa = 35.0  # Yield strength along layer lines (MPa)
  safety_factor = 3.5  # Safety factor for visitor fatigue & dynamic loads
  sigma_allow_mpa = sigma_yield_mpa / safety_factor  # 10.0 MPa
  max_allowable_deflection_mm = 0.75  # Limit tip sag to keep model centered

  # 1. TUNNEL GEOMETRY & CANTILEVER OVERHANG
  if tunnel_width is None:
    if m_kg <= 0.120:  # Desktop prototype scale (<= 120 g)
      W_tunnel_in = 4.75
    elif m_kg <= 0.350:  # Mid-scale console (120 g - 350 g)
      W_tunnel_in = 8.25
    else:  # Large museum exhibit (> 350 g)
      W_tunnel_in = 12.0
  else:
    if str(unit_len).lower() in ["mm", "2"]:
      W_tunnel_in = tunnel_width / IN_TO_MM
    else:
      W_tunnel_in = tunnel_width

  W_tunnel_mm = W_tunnel_in * IN_TO_MM
  L_cantilever_mm = (
      W_tunnel_mm / 2.0
  )  # Overhang from back wall to tunnel center

  # Gravitational & Dynamic Design Loads
  F_weight_N = m_kg * 9.80665
  F_design_N = max(F_weight_N * 2.5, F_weight_N + 3.5)

  # 2. CANTILEVER '+' CROSS-AXLE SIZING
  # Cruciform (+) cross: I = (29 / 972) * w^4, Z = (29 / 486) * w^3
  M_bending_Nmm = F_design_N * L_cantilever_mm

  # Constraint A: Bending stress limit
  w_stress_mm = (
      M_bending_Nmm / (sigma_allow_mpa * (29.0 / 486.0))
  ) ** (1.0 / 3.0)

  # Constraint B: Tip deflection limit
  I_req_mm4 = (F_weight_N * (L_cantilever_mm**3)) / (
      3.0 * E_pla_mpa * max_allowable_deflection_mm
  )
  w_deflect_mm = (I_req_mm4 / (29.0 / 972.0)) ** (1.0 / 4.0)

  w_axle_calc = max(w_stress_mm, w_deflect_mm)
  w_axle_mm = math.ceil(max(8.0, w_axle_calc) * 2.0) / 2.0
  t_web_mm = round(w_axle_mm / 3.0, 1)

  I_actual_mm4 = (29.0 / 972.0) * (w_axle_mm**4)
  actual_stress_mpa = M_bending_Nmm / ((29.0 / 486.0) * (w_axle_mm**3))
  actual_deflection_mm = (F_weight_N * (L_cantilever_mm**3)) / (
      3.0 * E_pla_mpa * I_actual_mm4
  )

  # Female broach socket (gears, knob, clamp): +0.35 mm clearance
  socket_w_mm = w_axle_mm + 0.35
  socket_t_mm = t_web_mm + 0.35

  # 3. CONNECTING STICKS (DUAL FLAT LINKS) SIZING
  L_stick_mm = max(65.0, round(W_tunnel_in * 10.0, 0))

  T_visitor_Nmm = 400.0 + (F_weight_N * 25.0)
  R_crank_mm = max(15.0, round(w_axle_mm * 1.6, 0))
  F_stick_load_N = T_visitor_Nmm / R_crank_mm

  # Euler Buckling on Flat Stick: P_cr = (pi^2 * E * I_min) / L_stick^2
  P_cr_req_N = 3.0 * F_stick_load_N
  h_stick_calc = (
      (P_cr_req_N * (L_stick_mm**2) * 12.0) / ((math.pi**2) * E_pla_mpa * 2.5)
  ) ** 0.25
  h_stick_mm = math.ceil(max(3.0, h_stick_calc) * 2.0) / 2.0
  b_stick_mm = math.ceil(h_stick_mm * 2.5)

  I_stick_actual = (b_stick_mm * (h_stick_mm**3)) / 12.0
  P_cr_actual_N = ((math.pi**2) * E_pla_mpa * I_stick_actual) / (L_stick_mm**2)
  buckling_safety_factor = P_cr_actual_N / F_stick_load_N

  # 4. CRANK PINS & GEAR WHEEL SIZING
  d_pin_mm = math.ceil(max(5.0, h_stick_mm * 1.3, w_axle_mm * 0.55))
  gear_dia_mm = round((R_crank_mm * 2.0) + d_pin_mm + 14.0, 0)
  gear_thickness_mm = max(6.0, round(h_stick_mm * 1.5, 0))

  # PRINT COMPREHENSIVE REPORT
  print("=" * 72)
  print("      SPONDER LABS: PARAMETRIC STRUCTURAL MECHANISM SCALER      ")
  print("=" * 72)
  print(
      f"INPUT MODEL WEIGHT       : {m_kg*1000:.1f} g ({m_kg:.3f} kg /"
      f" {m_kg*35.274:.1f} oz / {m_kg*2.2046:.2f} lb)"
  )
  print(f'WIND TUNNEL WIDTH (W)    : {W_tunnel_in:.2f}" ({W_tunnel_mm:.1f} mm)')
  print(
      f"CANTILEVER OVERHANG (L)  : {L_cantilever_mm:.1f} mm"
      f' ({L_cantilever_mm/25.4:.2f}" to tunnel center)'
  )
  print("-" * 72)

  print("[1] '+' CANTILEVER CROSS-AXLE (Holds Airplane):")
  print(f"    * Outer Cross Width (w)  : {w_axle_mm:.1f} mm")
  print(f"    * Arm Web Thickness (t)  : {t_web_mm:.1f} mm")
  print(
      f"    * Female Broach Socket   : {socket_w_mm:.2f} mm x {socket_t_mm:.2f}"
      " mm (+0.35 mm clearance)"
  )
  print(
      f"    * Predicted Static Sag   : {actual_deflection_mm:.3f} mm (Limit <="
      f" {max_allowable_deflection_mm} mm -> PASS)"
  )
  print(
      f"    * Peak Bending Stress    : {actual_stress_mpa:.2f} MPa (Allowable <="
      f" {sigma_allow_mpa:.1f} MPa -> PASS)"
  )
  print(
      "    * Critical Print Rule    : PRINT HORIZONTALLY (layer lines"
      " parallel to length)"
  )

  print("\n[2] DUAL CONNECTING STICKS (Transmits Pitch Between Gears):")
  print(f"    * Stick Width (b)        : {b_stick_mm:.1f} mm")
  print(f"    * Stick Thickness (h)    : {h_stick_mm:.1f} mm")
  print(f"    * Center-to-Center Length: {L_stick_mm:.1f} mm")
  print(
      f"    * Pivot Eyelet Hole Dia  : {d_pin_mm + 0.35:.2f} mm (Snaps onto"
      f" Ø{d_pin_mm} mm pins)"
  )
  print(
      f"    * Buckling Threshold     : {P_cr_actual_N:.1f} N compressive load"
      f" (Safety Factor: {buckling_safety_factor:.1f}x)"
  )

  print("\n[3] GEAR DISCS & CRANK PINS:")
  print(f"    * Crank Pin Diameter     : Ø{d_pin_mm:.1f} mm")
  print(f"    * Crank Pin Pitch Radius : {R_crank_mm:.1f} mm from gear center")
  print(f"    * Gear Disc Outer Dia    : Ø{gear_dia_mm:.1f} mm")
  print(f"    * Gear Disc Thickness    : {gear_thickness_mm:.1f} mm")

  print("\n[4] SLICER & PRINTING RECOMMENDATIONS:")
  print(
      "    * Wall Perimeters (Shell): >= 4 perimeters (solid teeth & solid pin"
      " walls)"
  )
  print("    * Infill Percentage      : >= 40% Gyroid or Rectilinear")
  print("    * Material Selection     : Standard PLA / PLA+ / PETG")
  print("=" * 72)


def interactive_runner():
  print("=" * 72)
  print("    SPONDER LABS: MECHANISM SCALER FOR 3D-PRINTED STING MOUNT   ")
  print("=" * 72)
  try:
    w_str = input(
        "Enter aircraft weight/mass (e.g. 75, 150, 400): "
    ).strip()
    weight = float(w_str) if w_str else 85.0
    unit_w = input(
        "Units? (1: grams [g], 2: oz, 3: lb) [default: g]: "
    ).strip()
    unit_w_map = {
        "1": "g",
        "2": "oz",
        "3": "lb",
        "g": "g",
        "oz": "oz",
        "lb": "lb",
    }
    u_w = unit_w_map.get(unit_w.lower(), "g")

    tw_str = input(
        "Tunnel width in inches? (Press ENTER to auto-size): "
    ).strip()
    t_w = float(tw_str) if tw_str else None
  except (EOFError, ValueError):
    weight = 85.0
    u_w = "g"
    t_w = None

  scale_pitch_mechanism(weight, unit_weight=u_w, tunnel_width=t_w)


if __name__ == "__main__":
  args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

  if len(args) > 0:
    try:
      wt = float(args[0])
      uw = args[1] if len(args) > 1 else "g"
      tw = float(args[2]) if len(args) > 2 else None
      scale_pitch_mechanism(wt, unit_weight=uw, tunnel_width=tw)
    except ValueError:
      interactive_runner()
  else:
    interactive_runner()
