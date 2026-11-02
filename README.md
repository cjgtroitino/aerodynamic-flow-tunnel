# Interactive Flow-Visualization Wind Tunnel
**From Rapid Desktop Prototyping to Full-Scale Aerospace Museum Exhibits**

![Status: Active Development](https://img.shields.io/badge/Status-Active_Development-blue)
![Focus: Aerodynamics & STEM](https://img.shields.io/badge/Focus-Aerodynamics_%7C_STEM-success)
![Hardware: 3D Printed / Laser Cut](https://img.shields.io/badge/Hardware-3D_Printed_%7C_Acrylic-orange)

## 📌 Project Overview
This repository documents the complete engineering lifecycle of a low-speed, flow-visualization wind tunnel platform. Designed to convert passive museum visitors into active flight-test engineers, this system uses ultrasonic cold-mist aerosol and dark-field LED lighting to visualize boundary layer behavior, stall characteristics, and fluid dynamics principles. 

The project is structured in two distinct development tracks:
1. **Phase 1: Desktop Prototype & STEM Kit** – A compact $5'' \times 5''$ test section utilizing 3D-printed chassis components, a 12V high-static PC fan, and a modular electronic basement with tool-less WAGO wiring. 
2. **Phase 2: Museum Exhibit Console** – Scaled parametric hardware designed for standard 120V AC mixed-flow duct blowers, commercial multi-head fog generators, and optical non-bowing acrylic analysis for permanent installation at the **War Eagles Air Museum**.

## ⚙️ Core Engineering Subsystems

* **Flow Conditioning (Anti-Swirl):** Utilizes an ultra-thin cell-wall honeycomb matrix ($L/D \approx 7:1$) paired with intake settling screens to suppress fan-induced vorticity and maintain steady, low-turbulence laminar core flow.
* **Isokinetic Flow Visualization:** Features a sub-floor multi-port manifold ("fog comb") that pulls concentrated vapor from an isolated 12V ultrasonic piezoelectric mist tank. This prevents water droplet splashing while generating crisp, parallel tracer streamlines.
* **Dark-Field Optics:** Integrates recessed 12V 6500K COB LED slit-lighting to trigger Mie scattering against a matte-black background, rendering high-contrast visible streamlines.
* **Mechanical Angle of Attack (AoA):** Designed a zero-height, side-wall thumb dial mechanism and a four-bar kinematic linkage system for adjusting model pitch without dead-center lockup or flow obstruction.
* **Tool-Less Electrical Architecture:** A unified 12V DC system combining PWM motor speed control, independent toggle switches, and WAGO 221 distribution hubs, eliminating the need for soldering during kit assembly.

## 🧪 Educational Test Modules
The tunnel acts as a testing console for four swappable, tool-free experiment cartridges:
1. **Reynolds Number & Sphere Wake:** Compares smooth vs. dimpled spheres to demonstrate boundary-layer separation, "drag crisis," and wake collapse.
2. **Nose Geometry & Form Drag:** Contrasts blunt, parabolic, and conical profiles to visualize attached flow vs. massive stagnation separation.
3. **Biplane Interference Drag:** Features an adjustable vertical gap ($G/c$ ratio) and stagger to show pressure-field interference and airflow choking between dual wings.
4. **Tandem Wing Downwash:** Examines wake ingestion and horizontal stabilizer authority at varying separations.

## 📂 Repository Structure
* `/scripts` - Python computational engines for aerodynamic sizing.
  * `universal_tunnel_sizer.py`: Scales test sections, blowers, and acrylic thickness based on model blockage rules.
  * `sphere_reynolds_scaling.py`: Analyzes Re thresholds for laminar vs. turbulent boundary layer trips.
* `/cad` - *[Pending]* Fusion 360 models, STEP files, and laser-cutting DXFs for the chassis and airfoil profiles.
* `/hardware` - *[Pending]* Wiring schematics, Bill of Materials (BOM), and assembly diagrams.
* `/docs` - *[Pending]* Educational curriculum and fluid dynamics math derivations.

## 🚀 Getting Started (Sizing Engine)
To run the parametric sizing tool to calculate dimensions for a custom wind tunnel build:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/desktop-aerodynamic-flow-tunnel.git
   ```
2. Run the interactive sizer (no third-party dependencies required):
   ```bash
   cd desktop-aerodynamic-flow-tunnel/scripts
   python universal_tunnel_sizer.py
   ```

---
*Developed by Carlos Gonzalez in partnership with the War Eagles Air Museum and the UTEP Aerospace & Mechanical Engineering Capstone Initiative.*
