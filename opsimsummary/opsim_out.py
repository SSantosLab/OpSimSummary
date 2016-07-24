#!/usr/bin/env python 
from __future__ import absolute_import, division, print_function
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

__all__ = ['OpSimOutput']

class OpSimOutput(object):
    def __init__(self, summary=None, propIDDict=None, proposalTable=None):
	self.summary = summary
	self.propIDDict = propIDDict
        self.proposalTable = proposalTable
	self.allowed_subsets = self.get_allowed_subsets()

    @classmethod
    def fromOpSimDB(cls, dbname, subset='combined'):
	"""
	Class Method to instantiate this from an OpSim sqlite
	database output

	Parameters
	----------
	dbname :
	subset :
	"""
	allowed_subsets = cls.get_allowed_subsets()
	subset = subset.lower()
	if subset not in allowed_subsets:
	    raise NotImplementedError('subset {} not implemented'.\
				      format(subset))
        if not dbname.startswith('sqlite'):
            dbname =  'sqlite:///' + dbname
        print(' reading from database {}'.format(dbname))
        engine = create_engine(dbname, echo=False)
	# Read the proposal table to find out which propID corresponds to
        proposals = pd.read_sql_table('Proposal', con=engine)
        propDict = cls.get_propIDDict(proposals)

        # Do the actual sql queries or table reads
        if subset in ['_all', 'unique_all']:
            # In this case read everything (ie. table read)
	    summary = pd.read_sql_table('Summary', con=engine)
            # _all will be used only to write out other serialized versions
            # of OpSim. Do not drop duplicates, so that different subsets can
            # be constructed from the same hdf file
	    if subset == 'unique_all':
	       summary.drop_duplicates(subset='obsHistID', inplace=True)	
            summary.set_index('obsHistID', inplace=True)
	    return cls(propIDDict=propDict, summary=summary,
                       proposalTable=proposals)
	else:
	    sql_query = 'SELECT * FROM Summary WHERE PROPID'
	    if subset == 'ddf':
		sql_query += ' == {0}'.format(propDict['ddf'])
	    if subset == 'wfd':
		sql_query += ' == {0}'.format(propDict['wfd'])
	    if subset == 'combined':
		sql_query += ' in [{0}, {1}]'.format(propDict['wfd'],
                                                     propDict['ddf'])
        # Read the summary table 
        summary = pd.read_sql_query(sql_query, con=engine)
	summary.drop_duplicates(subset='obsHistID', inplace=True)
	summary.set_index('obsHistID', inplace=True)
        return cls(propIDDict=propDict, summary=summary,
                   proposalTable=proposals)

    @staticmethod
    def get_allowed_subsets():
	return ('_all', 'ddf', 'wfd', 'combined', 'unique_all')
    @staticmethod
    def get_propIDDict(proposalDF):
	"""
	"""
	df = proposalDF
	mydict = dict()
	for i, vals in enumerate(df.propConf.values):
	    if 'universal' in vals.lower():
		if 'wfd' in mydict:
		    raise ValueError('Multiple propIDs for WFD found')
		mydict['wfd']  = df.propID.iloc[i]
	    elif 'ddcosmology' in vals.lower():
		if 'ddf' in mydict:
		    raise ValueError('Multiple propIDs for DDF found')
		mydict['ddf']  = df.propID.iloc[i] 
	if len(mydict.items()) != 2:
	    raise ValueError('Unexpected length of dictionary')
	return mydict



def OpSimDfFromFile(fname, ftype='hdf', subset='Combined'):
    """
    read a serialized form of the OpSim output into `pd.DataFrame`
    and return a subset of interest

    Parameters
    ----------
    fname : string, mandatory
        absolute path to serialized form of the OpSim database
    ftype : {'sqliteDB', 'ASCII', 'hdf'}
        The kind of serialized version being read from.
            'sqliteDB' : `LSST` project supplied OpSim output format for
                baseline cadences (eg. enigma_1189, minion_1016, etc.) 
            'ASCII' : `LSST` project supplied OpSim output format used in
                older OpSim outputs eg. OpSim v 2.168 output
            'hdf' : `hdf` files written out by `OpSimSummary`
    subset : {'Combined', 'DDF', 'WFD' , 'All'}, defaults to 'Combined' 
        Type of OpSim output desired in the dataframe
        'Combined' : unique pointings in WFD + DDF 
        'WFD' : Unique pointings in WFD
        'DDF' : Unique pointings in DDF Cosmology
        'All' : Entire Summary Table From OpSim
    """
    if ftype == 'sqlite':
        dbname = 'sqlite:///' + fname
        engine = create_engine(dbname, echo=False)
        proposalTable =  pd.read_sql_table('Proposal', con=engine)

        if subset == 'DDF':
            sql


    elif ftype == 'hdf' :
        pass
    elif ftype == 'ASCII':
        pass
    else:
        raise NotImplementedError('ftype {} not implemented'.format(ftype))

