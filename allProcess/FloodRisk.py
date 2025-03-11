"""
Model exported as python.
Name : Flood risk mitigation
Group : FloodRiskS+
With QGIS : 32213
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
import processing


class FloodRiskMitigation(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString('admid', 'Adm_id', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterFile('administrativeunits', 'Administrative units', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('damageunitsmap', 'Damage units map', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('returnperioda', 'Return period A', type=QgsProcessingParameterNumber.Integer, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('returnperiodb', 'Return period B', type=QgsProcessingParameterNumber.Integer, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('returnperiodc', 'Return period C', type=QgsProcessingParameterNumber.Integer, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('returnperiodd', 'Return period D', optional=True, type=QgsProcessingParameterNumber.Integer, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('returnperiode', 'Return period E', optional=True, type=QgsProcessingParameterNumber.Integer, defaultValue=None))
        # Capa de rius de SWAT model baseline (20 anys)
        self.addParameter(QgsProcessingParameterFile('rivs1SWATPBC', 'rivs1_SWATP_BC', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=''))
        # Capa de rius de SWAT model scenario (amb canvis a la conca)
        self.addParameter(QgsProcessingParameterFile('rivs1SWATPSC', 'rivs1_SWATP_SC', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=''))
        self.addParameter(QgsProcessingParameterFile('sqliteoutputBC', 'sqlite_output_BC', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=''))
        self.addParameter(QgsProcessingParameterFile('sqliteoutputSC', 'sqlite_output_SC', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('Eadd5', 'EADD5', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eadd4', 'EADD4', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Eadd3', 'EADD3', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(60, model_feedback)
        results = {}
        outputs = {}

        has_return_d = parameters['returnperiodd'] is not None
        has_return_e = parameters['returnperiode'] is not None

        # String concatenation - SC
        alg_params = {
            'INPUT_1': parameters['sqliteoutputSC'],
            'INPUT_2': '|layername=channel_sd_day'
        }
        outputs['StringConcatenationSc'] = processing.run('native:stringconcatenation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - max flo_out SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['yr','gis_id'],
            'INPUT': outputs['StringConcatenationSc']['CONCATENATION'],
            'VALUES_FIELD_NAME': 'flo_out',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMaxFlo_outSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Conditional branch
        alg_params = {
        }
        outputs['ConditionalBranch'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - avg sd SC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['gis_id'],
            'INPUT': outputs['StatisticsByCategoriesMaxFlo_outSc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'max',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesAvgSdSc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # String concatenation - BC
        alg_params = {
            'INPUT_1': parameters['sqliteoutputBC'],
            'INPUT_2': '|layername=channel_sd_day'
        }
        outputs['StringConcatenationBc'] = processing.run('native:stringconcatenation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - max flo_out BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['yr','gis_id'],
            'INPUT': outputs['StringConcatenationBc']['CONCATENATION'],
            'VALUES_FIELD_NAME': 'flo_out',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesMaxFlo_outBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - avg sd BC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['gis_id'],
            'INPUT': outputs['StatisticsByCategoriesMaxFlo_outBc']['OUTPUT'],
            'VALUES_FIELD_NAME': 'max',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesAvgSdBc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Field calculator - ABC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'ABC',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"stddev" / 1.0628',
            'INPUT': outputs['StatisticsByCategoriesAvgSdBc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAbc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator - ASC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'ASC',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"stddev" / 1.0628',
            'INPUT': outputs['StatisticsByCategoriesAvgSdSc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorAsc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Field calculator - USC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'USC',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"mean"-0.5236*"ASC"',
            'INPUT': outputs['FieldCalculatorAsc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUsc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - ASC and USC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Channel',
            'FIELDS_TO_COPY': ['ASC','USC'],
            'FIELD_2': 'gis_id',
            'INPUT': parameters['rivs1SWATPSC'],
            'INPUT_2': outputs['FieldCalculatorUsc']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueAscAndUsc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Field calculator - UBC
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'UBC',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '"mean"-0.5236*"ABC"',
            'INPUT': outputs['FieldCalculatorAbc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorUbc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - ABC and UBC
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Channel',
            'FIELDS_TO_COPY': ['ABC','UBC'],
            'FIELD_2': 'gis_id',
            'INPUT': parameters['rivs1SWATPBC'],
            'INPUT_2': outputs['FieldCalculatorUbc']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueAbcAndUbc'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Field calculator - MDFTb
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'MDFTb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'UBC + ABC * ln(1/(1 - exp(-1 * 1/ {} )))'.format(parameters['returnperiodb']),
            'INPUT': outputs['JoinAttributesByFieldValueAbcAndUbc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMdftb'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Points along geometry - rivs1 BC to points
        alg_params = {
            'DISTANCE': 100,
            'END_OFFSET': 0,
            'INPUT': outputs['FieldCalculatorMdftb']['OUTPUT'],
            'START_OFFSET': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongGeometryRivs1BcToPoints'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - bChannel
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['Channel'],
            'INPUT': outputs['PointsAlongGeometryRivs1BcToPoints']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByFieldValueAscAndUsc']['OUTPUT'],
            'MAX_DISTANCE': 50,
            'NEIGHBORS': 1,
            'PREFIX': 'b',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestBchannel'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Extract by expression - bChannel
        alg_params = {
            'EXPRESSION': 'n = 1',
            'INPUT': outputs['JoinAttributesByNearestBchannel']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionBchannel'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - ABC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['bChannel'],
            'INPUT': outputs['ExtractByExpressionBchannel']['OUTPUT'],
            'VALUES_FIELD_NAME': 'ABC',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesAbc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - ABC_mean
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Channel',
            'FIELDS_TO_COPY': ['mean'],
            'FIELD_2': 'bChannel',
            'INPUT': outputs['JoinAttributesByFieldValueAscAndUsc']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesAbc']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'ABC_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueAbc_mean'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - UBC
        alg_params = {
            'CATEGORIES_FIELD_NAME': ['bChannel'],
            'INPUT': outputs['ExtractByExpressionBchannel']['OUTPUT'],
            'VALUES_FIELD_NAME': 'UBC',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesUbc'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - UBC_mean
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'Channel',
            'FIELDS_TO_COPY': ['mean'],
            'FIELD_2': 'bChannel',
            'INPUT': outputs['JoinAttributesByFieldValueAbc_mean']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesUbc']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'UBC_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueUbc_mean'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Field calculator - MDFTd
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'MDFTd',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'UBC_mean + ABC_mean * ln(1/(1 - exp(-1 * 1/  {} )))'.format(parameters['returnperiodd']),
            'INPUT': outputs['JoinAttributesByFieldValueUbc_mean']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMdftd'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Field calculator - MDFTa
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'MDFTa',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'UBC_mean + ABC_mean * ln(1/(1 - exp(-1 * 1/  {} )))'.format(parameters['returnperioda']),
            'INPUT': outputs['JoinAttributesByFieldValueUbc_mean']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMdfta'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Field calculator - MDFTe
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'MDFTe',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'UBC_mean + ABC_mean * ln(1/(1 - exp(-1 * 1/  {} )))'.format(parameters['returnperiode']),
            'INPUT': outputs['JoinAttributesByFieldValueUbc_mean']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMdfte'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Field calculator - MDFTb
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'MDFTb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'UBC_mean + ABC_mean * ln(1/(1 - exp(-1 * 1/  {} )))'.format(parameters['returnperiodb']),
            'INPUT': outputs['FieldCalculatorMdfta']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMdftb'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Field calculator - MDFTc
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'MDFTc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': 'UBC_mean + ABC_mean * ln(1/(1 - exp(-1 * 1/ {} )))'.format(parameters['returnperiodc']),
            'INPUT': outputs['FieldCalculatorMdftb']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorMdftc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Merge vector layers- MDFTd
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['FieldCalculatorMdftd']['OUTPUT'],outputs['FieldCalculatorMdftc']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersMdftd'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIa
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIa',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTa - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorMdftc']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPia'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Merge vector layers- MDFTe
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['FieldCalculatorMdftd']['OUTPUT'],outputs['FieldCalculatorMdftc']['OUTPUT'],outputs['FieldCalculatorMdfte']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayersMdfte'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIb
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTb - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPia']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPib'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIc
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTc - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPib']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPic'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - MDFT PI 3
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['MDFTa','MDFTb','MDFTc','PIa','PIb','PIc'],
            'INPUT': parameters['damageunitsmap'],
            'INPUT_2': outputs['FieldCalculatorPic']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestMdftPi3'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Aggregate - 4
        alg_params = {
            'AGGREGATES': [{'aggregate': 'mean','delimiter': ',','input': 'Channel','length': 10,'name': 'Channel','precision': 0,'type': 2},{'aggregate': 'mean','delimiter': ',','input': 'ASC','length': 13,'name': 'ASC','precision': 3,'type': 6},{'aggregate': 'mean','delimiter': ',','input': 'USC','length': 13,'name': 'USC','precision': 3,'type': 6},{'aggregate': 'mean','delimiter': ',','input': 'ABC_mean','length': 13,'name': 'ABC_mean','precision': 3,'type': 6},{'aggregate': 'mean','delimiter': ',','input': 'UBC_mean','length': 13,'name': 'UBC_mean','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTa','length': 13,'name': 'MDFTa','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTb','length': 13,'name': 'MDFTb','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTc','length': 13,'name': 'MDFTc','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTd','length': 13,'name': 'MDFTd','precision': 3,'type': 6}],
            'GROUP_BY': 'Channel',
            'INPUT': outputs['MergeVectorLayersMdftd']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Aggregate4'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Aggregate - 5
        alg_params = {
            'AGGREGATES': [{'aggregate': 'mean','delimiter': ',','input': 'Channel','length': 10,'name': 'Channel','precision': 0,'type': 2},{'aggregate': 'mean','delimiter': ',','input': 'ASC','length': 13,'name': 'ASC','precision': 3,'type': 6},{'aggregate': 'mean','delimiter': ',','input': 'USC','length': 13,'name': 'USC','precision': 3,'type': 6},{'aggregate': 'mean','delimiter': ',','input': 'ABC_mean','length': 13,'name': 'ABC_mean','precision': 3,'type': 6},{'aggregate': 'mean','delimiter': ',','input': 'UBC_mean','length': 13,'name': 'UBC_mean','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTa','length': 13,'name': 'MDFTa','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTb','length': 13,'name': 'MDFTb','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTc','length': 13,'name': 'MDFTc','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTd','length': 13,'name': 'MDFTd','precision': 3,'type': 6},{'aggregate': 'sum','delimiter': ',','input': 'MDFTe','length': 13,'name': 'MDFTe','precision': 3,'type': 6}],
            'GROUP_BY': 'Channel',
            'INPUT': outputs['MergeVectorLayersMdfte']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Aggregate5'] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Extract by expression - MDFT PI 3
        alg_params = {
            'EXPRESSION': 'n = 1',
            'INPUT': outputs['JoinAttributesByNearestMdftPi3']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionMdftPi3'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIa4
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIa',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTa - USC)/ ASC))))',
            'INPUT': outputs['Aggregate4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPia4'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIb4
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTb - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPia4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPib4'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(37)
        if feedback.isCanceled():
            return {}

        # Field calculator - EADD 3
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EADD',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '((((1/{0} - 1/{1}) * (totdamc + totdamb)) + ((1/{1} - 1/{2}) * (totdamb + totdama))) - (((PIc - PIb) * (totdamc + totdamb)) + ((PIb - PIa) * (totdamb + totdama)))) * 0.5'.format(parameters['returnperiodc'], parameters['returnperiodb'], parameters['returnperioda']),
            'INPUT': outputs['ExtractByExpressionMdftPi3']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEadd3'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(38)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIc4
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTc - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPib4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPic4'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(39)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIa5
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIa',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTa - USC)/ ASC))))',
            'INPUT': outputs['Aggregate5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPia5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(40)
        if feedback.isCanceled():
            return {}

        # Field calculator - PId4
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PId',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTd - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPic4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPid4'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(41)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - Adm_id 3
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalculatorEadd3']['OUTPUT'],
            'JOIN': parameters['administrativeunits'],
            'JOIN_FIELDS': parameters['admid'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationAdm_id3'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(42)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EADD by Adm_id 3
        alg_params = {
            'CATEGORIES_FIELD_NAME': parameters['admid'],
            'INPUT': outputs['JoinAttributesByLocationAdm_id3']['OUTPUT'],
            'VALUES_FIELD_NAME': 'EADD',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEaddByAdm_id3'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(43)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - MDFT PI 4
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['MDFTa','MDFTb','MDFTc','MDFTd','PIa','PIb','PIc','PId'],
            'INPUT': parameters['damageunitsmap'],
            'INPUT_2': outputs['FieldCalculatorPid4']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestMdftPi4'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(44)
        if feedback.isCanceled():
            return {}

        # Extract by expression - MDFT PI 4
        alg_params = {
            'EXPRESSION': 'n = 1',
            'INPUT': outputs['JoinAttributesByNearestMdftPi4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionMdftPi4'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(45)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EADD by Adm_id 3
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['admid'],
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': parameters['admid'],
            'INPUT': parameters['administrativeunits'],
            'INPUT_2': outputs['StatisticsByCategoriesEaddByAdm_id3']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'EADD_',
            'OUTPUT': parameters['Eadd3']
        }
        outputs['JoinAttributesByFieldValueEaddByAdm_id3'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Eadd3'] = outputs['JoinAttributesByFieldValueEaddByAdm_id3']['OUTPUT']

        feedback.setCurrentStep(46)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIb5
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIb',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTb - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPia5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPib5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(47)
        if feedback.isCanceled():
            return {}

        # Field calculator - EADD 4
        return_period_a = parameters['returnperioda'] if parameters['returnperioda'] and parameters['returnperioda'] > 0 else 1
        return_period_b = parameters['returnperiodb'] if parameters['returnperiodb'] and parameters['returnperiodb'] > 0 else 1
        return_period_c = parameters['returnperiodc'] if parameters['returnperiodc'] and parameters['returnperiodc'] > 0 else 1
        return_period_d = parameters['returnperiodd'] if parameters['returnperiodd'] and parameters['returnperiodd'] > 0 else 1

        formula = f"((((1/{return_period_d} - 1/{return_period_c}) * (totdamd + totdamc)) + \
            ((1/{return_period_c} - 1/{return_period_b}) * (totdamc + totdamb)) + \
            ((1/{return_period_b} - 1/{return_period_a}) * (totdamb + totdama))) - \
            (((PId - PIc) * (totdamd + totdamc)) + ((PIc - PIb) * (totdamc + totdamb)) + \
            ((PIb - PIa) * (totdamb + totdama))))*0.5"

        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EADD',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': formula,#'((((1/@returnperiodd - 1/@returnperiodc) * (totdamd + totdamc)) + ((1/@returnperiodc - 1/@returnperiodb) * (totdamc + totdamb)) + ((1/@returnperiodb - 1/@returnperioda) * (totdamb + totdama))) - (((PId - PIc) * (totdamd + totdamc)) + ((PIc - PIb) * (totdamc + totdamb)) + ((PIb - PIa) * (totdamb + totdama))))*0.5',
            'INPUT': outputs['ExtractByExpressionMdftPi4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEadd4'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(48)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - Adm_id 4
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalculatorEadd4']['OUTPUT'],
            'JOIN': parameters['administrativeunits'],
            'JOIN_FIELDS': parameters['admid'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationAdm_id4'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(49)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIc5
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTc - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPib5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPic5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(50)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EADD by Adm_id 4
        alg_params = {
            'CATEGORIES_FIELD_NAME': parameters['admid'],
            'INPUT': outputs['JoinAttributesByLocationAdm_id4']['OUTPUT'],
            'VALUES_FIELD_NAME': 'EADD',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEaddByAdm_id4'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(51)
        if feedback.isCanceled():
            return {}

        # Field calculator - PId5
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PId',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTd - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPic5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPid5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(52)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EADD by Adm_id 4
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['admid'],
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': parameters['admid'],
            'INPUT': parameters['administrativeunits'],
            'INPUT_2': outputs['StatisticsByCategoriesEaddByAdm_id4']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'EADD_',
            'OUTPUT': parameters['Eadd4']
        }
        if has_return_d: 
            outputs['JoinAttributesByFieldValueEaddByAdm_id4'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Eadd4'] = outputs['JoinAttributesByFieldValueEaddByAdm_id4']['OUTPUT']

        feedback.setCurrentStep(53)
        if feedback.isCanceled():
            return {}

        # Field calculator - PIe5
        alg_params = {
            'FIELD_LENGTH': 13,
            'FIELD_NAME': 'PIe',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '(1-1*exp(-1*exp(-1*((MDFTe - USC)/ ASC))))',
            'INPUT': outputs['FieldCalculatorPid5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorPie5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(54)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest - MDFT PI 5
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['MDFTa','MDFTb','MDFTc','MDFTd','MDFTe','PIa','PIb','PIc','PId','PIe'],
            'INPUT': parameters['damageunitsmap'],
            'INPUT_2': outputs['FieldCalculatorPie5']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearestMdftPi5'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(55)
        if feedback.isCanceled():
            return {}

        # Extract by expression - MDFT PI 5
        alg_params = {
            'EXPRESSION': 'n = 1',
            'INPUT': outputs['JoinAttributesByNearestMdftPi5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionMdftPi5'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(56)
        if feedback.isCanceled():
            return {}

        # Field calculator - EADD 5

        return_period_a = parameters['returnperioda'] if parameters['returnperioda'] and parameters['returnperioda'] > 0 else 1
        return_period_b = parameters['returnperiodb'] if parameters['returnperiodb'] and parameters['returnperiodb'] > 0 else 1
        return_period_c = parameters['returnperiodc'] if parameters['returnperiodc'] and parameters['returnperiodc'] > 0 else 1
        return_period_d = parameters['returnperiodd'] if parameters['returnperiodd'] and parameters['returnperiodd'] > 0 else 1
        return_period_e = parameters['returnperiode'] if parameters['returnperiode'] and parameters['returnperiode'] > 0 else 1


        # Construir la fórmula en Python antes de usarla en la expresión de QGIS
        formula = f"((((1/{return_period_e} - 1/{return_period_d}) * (totdame + totdamd)) + \
            ((1/{return_period_d} - 1/{return_period_c}) * (totdamd + totdamc)) + \
            ((1/{return_period_c} - 1/{return_period_b}) * (totdamc + totdamb)) + \
            ((1/{return_period_b} - 1/{return_period_a}) * (totdamb + totdama))) - \
            (((PIe - PId) * (totdame + totdamd)) + ((PId - PIc) * (totdamd + totdamc)) + \
            ((PIc - PIb) * (totdamc + totdamb)) + ((PIb - PIa) * (totdamb + totdama))))*0.5"


        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'EADD',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': formula,#'((((1/@returnperiode - 1/@returnperiodd) * (totdame + totdamd)) + ((1/@returnperiodd - 1/@returnperiodc) * (totdamd + totdamc)) + ((1/@returnperiodc - 1/@returnperiodb) * (totdamc + totdamb)) + ((1/@returnperiodb - 1/@returnperioda) * (totdamb + totdama))) - (((PIe - PId) * (totdame + totdamd)) + ((PId - PIc) * (totdamd + totdamc)) + ((PIc - PIb) * (totdamc + totdamb)) + ((PIb - PIa) * (totdamb + totdama))))*0.5',
            'INPUT': outputs['ExtractByExpressionMdftPi5']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculatorEadd5'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(57)
        if feedback.isCanceled():
            return {}

        # Join attributes by location - Adm_id 5
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FieldCalculatorEadd5']['OUTPUT'],
            'JOIN': parameters['administrativeunits'],
            'JOIN_FIELDS': parameters['admid'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREDICATE': [0],  # intersects
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationAdm_id5'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(58)
        if feedback.isCanceled():
            return {}

        # Statistics by categories - EADD by Adm_id 5
        alg_params = {
            'CATEGORIES_FIELD_NAME': parameters['admid'],
            'INPUT': outputs['JoinAttributesByLocationAdm_id5']['OUTPUT'],
            'VALUES_FIELD_NAME': 'EADD',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesEaddByAdm_id5'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(59)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value - EADD by Adm_id 5
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['admid'],
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': parameters['admid'],
            'INPUT': parameters['administrativeunits'],
            'INPUT_2': outputs['StatisticsByCategoriesEaddByAdm_id5']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'EADD_',
            'OUTPUT': parameters['Eadd5']
        }
        if has_return_e:
            outputs['JoinAttributesByFieldValueEaddByAdm_id5'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Eadd5'] = outputs['JoinAttributesByFieldValueEaddByAdm_id5']['OUTPUT']

        print(results)
        return results

    def name(self):
        return 'Flood risk mitigation'

    def displayName(self):
        return 'Flood risk mitigation'

    def group(self):
        return 'FloodRiskS+'

    def groupId(self):
        return 'SWAT'

    def shortHelpString(self):
        return """<html><body><p></p>
<br></body></html>"""

    def createInstance(self):
        return FloodRiskMitigation()
