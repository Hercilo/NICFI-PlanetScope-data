'''
#######################################################
eepypr
Functions returning predefined spectral-temporal metrics
for Landsat C1, Sentinel-2, and PlanetScope image collections

startDate / endDate must be provided as datetime object
mark start and end of aggregation period.
#######################################################
'''

import ee
import csv
import ogr
import src.lnd
import src.sen
import src.psm

# todo: allow band selection and multiple aggregation windows and reducers
def LND_STM(startDate, endDate):

    collection = src.lnd.LND(startDate, endDate)
    coll = collection.select('blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'evi')

    median = coll.reduce(ee.Reducer.percentile([50]))\
        .rename('blue_med', 'green_med', 'red_med', 'nir_med', 'swir1_med', 'swir2_med', 'evi_med')

    sd = coll.reduce(ee.Reducer.stdDev())\
        .rename('blue_sd', 'green_sd', 'red_sd', 'nir_sd', 'swir1_sd', 'swir2_sd', 'evi_sd')

    p25 = coll.reduce(ee.Reducer.percentile([25]))\
        .rename('blue_p25', 'green_p25', 'red_p25', 'nir_p25', 'swir1_p25', 'swir2_p25', 'evi_p25')

    p75 = coll.reduce(ee.Reducer.percentile([75]))\
        .rename('blue_p75', 'green_p75', 'red_p75', 'nir_p75', 'swir1_p75', 'swir2_p75', 'evi_p75')

    iqr = p75.subtract(p25)\
        .rename('blue_iqr', 'green_iqr', 'red_iqr', 'nir_iqr', 'swir1_iqr', 'swir2_iqr', 'evi_iqr')

    return ee.Image([median, sd, p25, p75, iqr])


def SEN_STM(startDate, endDate):

    collection = src.sen.SEN(startDate, endDate)
    coll = collection.select('blue', 'green', 'red','rededge1', 'rededge2', 'rededge3', 'nir', 'broadnir', 'swir1', 'swir2', 'ndvi')

    median = coll.reduce(ee.Reducer.percentile([50]))\
        .rename('blue_med', 'green_med', 'red_med', 'rededge1_med', 'rededge2_med', 'rededge3_med', 'nir_med', 'broadnir_med', 'swir1_med', 'swir2_med', 'ndvi_med')

    sd = coll.reduce(ee.Reducer.stdDev())\
        .rename('blue_sd', 'green_sd', 'red_sd', 'rededge1_sd', 'rededge2_sd', 'rededge3_sd', 'nir_sd', 'broadnir_sd', 'swir1_sd', 'swir2_sd', 'ndvi_sd')

    p25 = coll.reduce(ee.Reducer.percentile([25]))\
        .rename('blue_p25', 'green_p25', 'red_p25', 'rededge1_p25', 'rededge2_p25', 'rededge3_p25', 'nir_p25', 'broadnir_p25', 'swir1_p25', 'swir2_p25', 'ndvi_p25')

    p75 = coll.reduce(ee.Reducer.percentile([75]))\
        .rename('blue_p75', 'green_p75', 'red_p75', 'rededge1_p75', 'rededge2_p75', 'rededge3_p75', 'nir_p75', 'broadnir_p75', 'swir1_p75', 'swir2_p75', 'ndvi_p75')

    iqr = p75.subtract(p25)\
        .rename('blue_iqr', 'green_iqr', 'red_iqr', 'rededge1_iqr', 'rededge2_iqr', 'rededge3_iqr', 'nir_iqr', 'broadnir_iqr', 'swir1_iqr', 'swir2_iqr', 'ndvi_iqr')

    imean = coll.reduce(ee.Reducer.intervalMean(25, 75))\
        .rename('blue_imn', 'green_imn', 'red_imn', 'rededge1_imn', 'rededge2_imn', 'rededge3_imn', 'nir_imn', 'broadnir_imn', 'swir1_imn', 'swir2_imn', 'ndvi_imn')

    return ee.Image([median, sd, p25, p75, iqr, imean])


def PSM_STM(startDate, endDate, roi_path, register=False):
    if register==False:
        collection = src.psm.PSM(startDate, endDate)

    if register==True:
        collection = src.psm.PSM_COREG(startDate, endDate, roi_path, property='system:index', reference_id='planet_medres_normalized_analytic_2021-05_mosaic')

    coll = collection.select('blue', 'green', 'red', 'nir', 'ndvi')

    median = coll.reduce(ee.Reducer.percentile([50]))\
        .rename('blue_med', 'green_med', 'red_med', 'nir_med', 'ndvi_med')

    sd = coll.reduce(ee.Reducer.stdDev())\
        .rename('blue_sd', 'green_sd', 'red_sd', 'nir_sd', 'ndvi_sd')

    p25 = coll.reduce(ee.Reducer.percentile([25]))\
        .rename('blue_p25', 'green_p25', 'red_p25', 'nir_p25', 'ndvi_p25')

    p75 = coll.reduce(ee.Reducer.percentile([75]))\
        .rename('blue_p75', 'green_p75', 'red_p75', 'nir_p75', 'ndvi_p75')

    iqr = p75.subtract(p25)\
        .rename('blue_iqr', 'green_iqr', 'red_iqr', 'nir_iqr', 'ndvi_iqr')

    return ee.Image([median, sd, p25, p75, iqr])


def LND_NUM(startDate, endDate, roi=None):

    # calculate cfmask from pixel_qa
    def cfmask(image):
        pixel_qa = image.select('pixel_qa')
        cfmask_layer = ee.Image(255)\
        .where(pixel_qa.bitwiseAnd(2).neq(0), 0)\
        .where(pixel_qa.bitwiseAnd(4).neq(0), 1)\
        .where(pixel_qa.bitwiseAnd(8).neq(0), 2)\
        .where(pixel_qa.bitwiseAnd(16).neq(0), 3)\
        .where(pixel_qa.bitwiseAnd(32).neq(0), 4)\
        .updateMask(pixel_qa.bitwiseAnd(1).eq(0))

        return image.addBands(cfmask_layer.rename('cfmask'))

    lnd = src.lnd.LND(startDate, endDate).map(cfmask)

    # calculate clear observation counts
    def dailymosaic(delta):
        return lnd.filterDate(ee.Date(startDate.strftime("%Y-%m-%d"))\
                              .advance(delta, 'day'), ee.Date(startDate.strftime("%Y-%m-%d"))\
                              .advance(ee.Number(delta)\
                              .add(1), 'day'))\
                              .mosaic()\
                              .toInt16()

    # reclass
    def lte_1(image):
        return image.lte(1)

    lnd_cnt = ee.ImageCollection(ee.List.sequence(0, ee.Date(endDate.strftime("%Y-%m-%d"))
                                                  .difference(ee.Date(startDate.strftime("%Y-%m-%d")), 'day')\
                                                  .subtract(1))\
                                                  .map(dailymosaic))

    if roi != None:
        lnd_cnt = lnd_cnt.filterBounds(roi)

    return lnd_cnt.select(['cfmask'])\
                  .map(lte_1)\
                  .sum()\
                  .rename('cso')\
                  .toInt16()