# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FloodRiskSwatPlus
                                 A QGIS plugin
 FloodRiskSwatPlus
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-01-30
        copyright            : (C) 2025 by ICRA - Oliu Llorente
        email                : ollorente@icra.cat
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'ICRA - Oliu Llorente'
__date__ = '2025-01-30'
__copyright__ = '(C) 2025 by ICRA - Oliu Llorente'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FloodRiskSwatPlus class from file FloodRiskSwatPlus.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .FloodRiskSwatPlus import FloodRiskSwatPlusPlugin
    return FloodRiskSwatPlusPlugin(iface)
