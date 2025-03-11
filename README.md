# 🌊 FloodRiskSwatPlus – QGIS Plugin for Flood Risk Assessment

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green.svg)](https://qgis.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/your-repo)](https://github.com/your-repo/issues)

FloodRiskSwatPlus is a **QGIS plugin** designed to assess **flood risk impacts in economic terms** using **SWAT+ model scenarios**. It allows users to analyze potential **land management changes** and **climate change projections**, helping with **flood risk management and adaptation planning**.

---

## 🚀 Features
✔️ Estimates **Expected Annual Damage (EAD)** at different administrative levels  
✔️ Uses **flood damage maps (currency/m²)** for up to five return periods  
✔️ Supports multiple **SWAT+ scenarios** for comparative analysis  
✔️ Provides **economic impact assessment** for flood risk adaptation strategies  

---

## 👥 Installation
1. Open **QGIS** (version **3.0** or later required).
2. Download this repository or clone it:
   ```bash
   git clone https://github.com/your-repo/FloodRiskSwatPlus.git
   ```
3. Copy the plugin folder to your **QGIS plugins directory**:
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux/macOS: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
4. Restart **QGIS**, go to **Plugins > Manage and Install Plugins**, and enable `FloodRiskSwatPlus`.

---

## 🛠 Usage
1. Load your **watershed layers** and **daily flow rate output data** from SWAT+.
2. Use the **damage unit layer tool** to generate flood damage maps.
3. Run the **Flood Risk Impact Model** to calculate:
   - Expected Annual Damage (EAD)  
   - Percentage change in flood probabilities  
4. Visualize and analyze results in QGIS.

---

## 💡 Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-new-feature`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to your branch (`git push origin feature-new-feature`).
5. Open a **Pull Request**.

For issues or feature requests, please check the [Issues](https://github.com/your-repo/issues) section.

---

## 🐝 License
This plugin is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 📷 Contact
For any inquiries, please contact **Xavier Garcia, Oliu Llorente, Laia Estrada, Vicenç Acuña - ICRA** at **ollorente@icra.cat**.

---

🌍 **Developed by ICRA – Catalan Institute for Water Research**  
🔗 [Website](http://icra.cat) | [QGIS Plugins](https://plugins.qgis.org/) | [SWAT+ Model](https://swat.tamu.edu/)

