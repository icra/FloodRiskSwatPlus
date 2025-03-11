"""
Model exported as python.
Name : Damage units layer
Group : FloodRiskS+
With QGIS : 32213
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
from qgis.core import QgsProcessingParameterCrs

import processing


class DamageUnitsLayer(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterCrs('selected_crs', 'Select Projection (CRS)', defaultValue='EPSG:3035'))
        self.addParameter(QgsProcessingParameterNumber('channeldistanceselection', 'Channel distance selection', type=QgsProcessingParameterNumber.Double, minValue=1, maxValue=1000, defaultValue=250))
        self.addParameter(QgsProcessingParameterNumber('damageunitsizem', 'Damage unit cell size (m)', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('pixelsizem', 'Pixel size (m)', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('swatchannelvector', 'SWAT+ channel vector', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('floodriskrastermap', 'Flood risk raster layer A', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('frrmb', 'Flood risk raster layer B', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('frrmc', 'Flood risk raster layer C', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('frrmd', 'Flood risk raster layer D', optional=True, behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('frrme', 'Flood risk raster layer E', optional=True, behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Damunit3', 'DamUnit3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Damunit5', 'DamUnit5', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Damunit4', 'DamUnit4', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(22, model_feedback)
        results = {}
        outputs = {}

        has_return_d = parameters['frrmd'] not in [None, '']
        has_return_e = parameters['frrme'] not in [None, '']

        # Warp - frm

        project_crs = parameters['selected_crs'].authid()

        context.project().setCrs(parameters['selected_crs'])

        alg_params = {
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': parameters['floodriskrastermap'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'RESAMPLING': 0,  # Nearest Neighbour
            'SOURCE_CRS': project_crs, #'ProjectCrs',
            'TARGET_CRS': project_crs, #'ProjectCrs',
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'TARGET_RESOLUTION': parameters['damageunitsizem'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WarpFrm'] = processing.run('gdal:warpreproject', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Conditional branch
        alg_params = {
        }
        outputs['ConditionalBranch'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Buffer - select
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['channeldistanceselection'],
            'END_CAP_STYLE': 0,  # Round
            'INPUT': parameters['swatchannelvector'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferSelect'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Raster pixels to polygons
        alg_params = {
            'FIELD_NAME': 'dam_em2',
            'INPUT_RASTER': outputs['WarpFrm']['OUTPUT'],
            'RASTER_BAND': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterPixelsToPolygons'] = processing.run('native:pixelstopolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by location - damunits
        alg_params = {
            'INPUT': outputs['RasterPixelsToPolygons']['OUTPUT'],
            'INTERSECT': outputs['BufferSelect']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocationDamunits'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator - damunitsid
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'duid',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': '$id',
            'INPUT': outputs['ExtractByLocationDamunits']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorDamunitsid'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}


        outputs['ZonalStatisticsDamd_sum'] = None

        if parameters['frrmd']:
            # Zonal statistics - damd_sum
            alg_params = {
                'COLUMN_PREFIX': 'damd_',
                'INPUT': outputs['FieldCalculatorDamunitsid']['OUTPUT'],
                'INPUT_RASTER': parameters['frrmd'],
                'RASTER_BAND': 1,
                'STATISTICS': [2,0,1],  # Mean,Count,Sum
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['ZonalStatisticsDamd_sum'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['FieldCalculatorTotdamd'] = None

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Zonal statistics - dama_sum
        alg_params = {
            'COLUMN_PREFIX': 'dama_',
            'INPUT': outputs['FieldCalculatorDamunitsid']['OUTPUT'],
            'INPUT_RASTER': parameters['floodriskrastermap'],
            'RASTER_BAND': 1,
            'STATISTICS': [2,0,1],  # Mean,Count,Sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZonalStatisticsDama_sum'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Zonal statistics - damb_sum
        alg_params = {
            'COLUMN_PREFIX': 'damb_',
            'INPUT': outputs['FieldCalculatorDamunitsid']['OUTPUT'],
            'INPUT_RASTER': parameters['frrmb'],
            'RASTER_BAND': 1,
            'STATISTICS': [2,0,1],  # Mean,Count,Sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZonalStatisticsDamb_sum'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Field calculator - totdamb
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'totdamb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': ' "damb_sum" * {}^2'.format(parameters['pixelsizem']),#'damb_sum *  @pixelsizem^2',
            'INPUT': outputs['ZonalStatisticsDamb_sum']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTotdamb'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Zonal statistics - damc_sum
        alg_params = {
            'COLUMN_PREFIX': 'damc_',
            'INPUT': outputs['FieldCalculatorDamunitsid']['OUTPUT'],
            'INPUT_RASTER': parameters['frrmc'],
            'RASTER_BAND': 1,
            'STATISTICS': [2,0,1],  # Mean,Count,Sum
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZonalStatisticsDamc_sum'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        outputs['ZonalStatisticsDame_sum'] = None

        if parameters['frrme']:
            # Zonal statistics - dame_sum
            alg_params = {
                'COLUMN_PREFIX': 'dame_',
                'INPUT': outputs['FieldCalculatorDamunitsid']['OUTPUT'],
                'INPUT_RASTER': parameters['frrme'],
                'RASTER_BAND': 1,
                'STATISTICS': [2,0,1],  # Mean,Count,Sum
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['ZonalStatisticsDame_sum'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        else:
            outputs['FieldCalculatorTotdame'] = None

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Field calculator - totdama
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'totdama',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"dama_sum" * {}^2'.format(parameters['pixelsizem']),#'dama_sum *  @pixelsizem^2',
            'INPUT': outputs['ZonalStatisticsDama_sum']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTotdama'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Field calculator - totdamd
        if outputs['ZonalStatisticsDamd_sum']:
            alg_params = {
                'FIELD_LENGTH': 13,
                'FIELD_NAME': 'totdamd',
                'FIELD_PRECISION': 3,
                'FIELD_TYPE': 0,  # Float
                'FORMULA': ' "damd_sum" * {}^2'.format(parameters['pixelsizem']),#'damd_sum *  @pixelsizem^2',
                'INPUT': outputs['ZonalStatisticsDamd_sum']['OUTPUT'],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['FieldCalculatorTotdamd'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['FieldCalculatorTotdamd'] = None  # Evita el error si la capa no existe

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Field calculator - totdamc
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'totdamc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': ' "damc_sum" * {}^2'.format(parameters['pixelsizem']),#'damc_sum *  @pixelsizem^2',
            'INPUT': outputs['ZonalStatisticsDamc_sum']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorTotdamc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Merge vector layers - totdam4

        layers_totdam4 = [outputs['FieldCalculatorTotdama']['OUTPUT'], 
                  outputs['FieldCalculatorTotdamb']['OUTPUT'], 
                  outputs['FieldCalculatorTotdamc']['OUTPUT']]
        
        if outputs['FieldCalculatorTotdamd']:
            layers_totdam4.append(outputs['FieldCalculatorTotdamd']['OUTPUT'])


        alg_params = {
            'CRS': project_crs, #'ProjectCrs',
            'LAYERS': layers_totdam4, #[outputs['FieldCalculatorTotdama']['OUTPUT'],outputs['FieldCalculatorTotdamb']['OUTPUT'],outputs['FieldCalculatorTotdamc']['OUTPUT'],outputs['FieldCalculatorTotdamd']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersTotdam4'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Field calculator - totdame
        if outputs['ZonalStatisticsDame_sum']:
            alg_params = {
                'FIELD_LENGTH': 13,
                'FIELD_NAME': 'totdame',
                'FIELD_PRECISION': 3,
                'FIELD_TYPE': 0,  # Float
                'FORMULA': ' "dame_sum" * {}^2'.format(parameters['pixelsizem']),#'dame_sum *  @pixelsizem^2',
                'INPUT': outputs['ZonalStatisticsDame_sum']['OUTPUT'],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            outputs['FieldCalculatorTotdame'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else: 
            outputs['FieldCalculatorTotdame'] = None

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Aggregate - 4

        aggregate_list = [
            {'aggregate': 'mean','delimiter': ',','input': 'duid','length': 10,'name': 'duid','precision': 0,'type': 2},
            {'aggregate': 'sum','delimiter': ',','input': 'totdama','length': 13,'name': 'totdama','precision': 3,'type': 6},
            {'aggregate': 'sum','delimiter': ',','input': 'totdamb','length': 13,'name': 'totdamb','precision': 3,'type': 6},
            {'aggregate': 'sum','delimiter': ',','input': 'totdamc','length': 13,'name': 'totdamc','precision': 3,'type': 6}
        ]

        if outputs['FieldCalculatorTotdamd']:
            aggregate_list.append({'aggregate': 'sum','delimiter': ',','input': 'totdamd','length': 13,'name': 'totdamd','precision': 3,'type': 6})

        alg_params = {
            'AGGREGATES': aggregate_list, #[{'aggregate': 'mean','delimiter': ',','input': 'duid','length': 10,'name': 'duid','precision': 0,'type': 2},{'aggregate': 'sum','delimiter': ',','input': 'totdama','length': 13,'name': 'totdama','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamb','length': 13,'name': 'totdamb','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamc','length': 13,'name': 'totdamc','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamd','length': 13,'name': 'totdamd','precision': 3,'type': 6}],
            'GROUP_BY': 'duid',
            'INPUT': outputs['MergeVectorLayersTotdam4']['OUTPUT'],
            'OUTPUT': parameters['Damunit4']
        }
        print(has_return_d)
        if has_return_d:
            outputs['Aggregate4'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Damunit4'] = outputs['Aggregate4']['OUTPUT']
        else:
            results.pop('Damunit5', None)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Merge vector layers - totdam5

        # Lista de capas disponibles para la fusión de totdam5
        layers_totdam5 = [outputs['FieldCalculatorTotdama']['OUTPUT'], 
                  outputs['FieldCalculatorTotdamb']['OUTPUT'], 
                  outputs['FieldCalculatorTotdamc']['OUTPUT']]

        if outputs['FieldCalculatorTotdamd']:
            layers_totdam5.append(outputs['FieldCalculatorTotdamd']['OUTPUT'])

        if outputs['FieldCalculatorTotdame']:
            layers_totdam5.append(outputs['FieldCalculatorTotdame']['OUTPUT'])

        alg_params = {
            'CRS': project_crs,#'ProjectCrs',
            'LAYERS': layers_totdam5, #[outputs['FieldCalculatorTotdama']['OUTPUT'],outputs['FieldCalculatorTotdamb']['OUTPUT'],outputs['FieldCalculatorTotdamc']['OUTPUT'],outputs['FieldCalculatorTotdamd']['OUTPUT'],outputs['FieldCalculatorTotdame']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersTotdam5'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Merge vector layers - totdam3
        alg_params = {
            'CRS': project_crs,#'ProjectCrs',
            'LAYERS': [outputs['FieldCalculatorTotdama']['OUTPUT'],outputs['FieldCalculatorTotdamb']['OUTPUT'],outputs['FieldCalculatorTotdamc']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersTotdam3'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Aggregate - 3
        alg_params = {
            'AGGREGATES': [{'aggregate': 'mean','delimiter': ',','input': 'duid','length': 10,'name': 'duid','precision': 0,'type': 2},{'aggregate': 'sum','delimiter': ',','input': 'totdama','length': 13,'name': 'totdama','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamb','length': 13,'name': 'totdamb','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamc','length': 13,'name': 'totdamc','precision': 3,'type': 6}],
            'GROUP_BY': 'duid',
            'INPUT': outputs['MergeVectorLayersTotdam3']['OUTPUT'],
            'OUTPUT': parameters['Damunit3']
        }
        outputs['Aggregate3'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Damunit3'] = outputs['Aggregate3']['OUTPUT']

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Aggregate - 5

        aggregate_list = [
            {'aggregate': 'mean','delimiter': ',','input': 'duid','length': 10,'name': 'duid','precision': 0,'type': 2},
            {'aggregate': 'sum','delimiter': ',','input': 'totdama','length': 13,'name': 'totdama','precision': 3,'type': 6},
            {'aggregate': 'sum','delimiter': ',','input': 'totdamb','length': 13,'name': 'totdamb','precision': 3,'type': 6},
            {'aggregate': 'sum','delimiter': ',','input': 'totdamc','length': 13,'name': 'totdamc','precision': 3,'type': 6}
        ]

        if outputs['FieldCalculatorTotdamd']:
            aggregate_list.append({'aggregate': 'sum','delimiter': ',','input': 'totdamd','length': 13,'name': 'totdamd','precision': 3,'type': 6})

        if outputs['FieldCalculatorTotdame']:
            aggregate_list.append({'aggregate': 'sum','delimiter': ',','input': 'totdame','length': 13,'name': 'totdame','precision': 3,'type': 6})

        alg_params = {
            'AGGREGATES': aggregate_list, #[{'aggregate': 'mean','delimiter': ',','input': 'duid','length': 10,'name': 'duid','precision': 0,'type': 2},{'aggregate': 'sum','delimiter': ',','input': 'totdama','length': 13,'name': 'totdama','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamb','length': 13,'name': 'totdamb','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamc','length': 13,'name': 'totdamc','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdamd','length': 13,'name': 'totdamd','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'totdame','length': 13,'name': 'totdame','precision': 3,'type': 6}],
            'GROUP_BY': 'duid',
            'INPUT': outputs['MergeVectorLayersTotdam5']['OUTPUT'],
            'OUTPUT': parameters['Damunit5']
        }
        if has_return_e:
            outputs['Aggregate5'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Damunit5'] = outputs['Aggregate5']['OUTPUT']
        else:
            results.pop('Damunit4', None)

        return results

    def name(self):
        return 'Damage units layer'

    def displayName(self):
        return 'Damage units layer'

    def group(self):
        return 'FloodRiskS+'

    def groupId(self):
        return 'prepcapinun'

    def createInstance(self):
        return DamageUnitsLayer()
