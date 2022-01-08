#!/usr/bin/env python
# coding: utf-8

# read_mruihtml.py
# 
# Read an HTML results file produced by jMRUI/AMARES with the publish/publish all command in the fit result window of jMRUI
# The HTML format output preserves the link between fitted data and spectrum file names and is therefore the method of 
# choice for series of files.
#
# This version is designed for series of muscle 1H-MRS spectra
#
# Ronald Ouwerkerk NIDDK 2021

# The basics
import sys
import os

# regedit for finding strings in text
import re

# math stuff
import numpy as np
import array

# For interpreting HTML
import codecs
# For interpreting HTML tables
import pandas as pd

def main():

    htmlfile = ''
    nargins = len(sys.argv)

    if nargins > 1:
        htmlfile = sys.argv[1]
        print("The filepath argument = ", htmlfile )
    else:
        # No file path given as argument
        # Set up file browser
        from tkinter import Tk 	# for Python 3.x
        from tkinter.filedialog import askopenfilename

        # we don't want a full GUI, so keep the root window from appearing
        root = Tk()
        root.withdraw() 

        # show an "Open" dialog box and return the path to the selected file
        # Look for HISTO.cvs LCmodel output files
        htmlfile = askopenfilename( initialdir = '~/', title = "Select the jMRUI HTML file" ,filetypes = (("result tables" , "*.html"),("all files","*.*")))
        print( 'Selected {FILE} '.format( FILE = htmlfile ))
        root.update()
        root.destroy()    
    # Split the path, so we can use the path to the folder with the HTML file as output path
    filepath = os.path.split(htmlfile)[0]
    filename = os.path.split(htmlfile)[1]
    print( 'Processing {FILE} in folder {DIR}'.format( FILE = filename, DIR = filepath ))
    mrui_infos, mrui_results = read_mrui_html( htmlfile)
    
    # set up an empty panda dataframe with column headers for the data we want to export to Excel
    dfout = pd.DataFrame(columns =['File', 'CH3e', 'CH2e', 'EMCL','CH3i', 'CH2i', 'IMCL', 'H2O', 'Cr', 'TMA' , 'SNR'])
    # Now collect peak aplitudes for EMCL. IMCL and H2O from each table
    for idx, mrui_result in enumerate(mrui_results):
        # Select info table of interest
        thisfilename = mrui_infos[idx].filename
        # Collect the data from the mrui_result data frame.
        # Add mrui_info to link the data to the spectrum filename
        dfout = exctract_muscle_data( mrui_result , mrui_infos[idx], dfout= dfout , idx = idx )
    
    # Print the resulting table
    print(dfout)
    # Save to an Excel file, named for the firts spectrum of the series + mrui.xlsx
    xlsxfilepath = os.path.join( filepath, '{FILE}_mrui.xlsx'.format( FILE = mrui_infos[0].filename ) )
    dfout.to_excel( xlsxfilepath )  
    # end main
    return

# Define a class to collect the MRUI html header for each spectrum
class mrui_hdr: 
    def __init__(self, filename= '', date = '', algor = '', tstep=0.0, ph0=0.0, tbeg=0.0, niter=0, 
                 npeaks=0, nfound=0, npoints=0, nfit=0, trunc = 0, noisestd=0, snr = 0, ppmscale=0 ): 
        self.filename = filename 
        self.date = date
        self.algor = algor
        self.tstep = tstep
        self.ph0 = ph0
        self.tbeg=tbeg, 
        self.algor=algor 
        self.niter=niter 
        self.npeaks=npeaks
        self.nfound=nfound
        self.npoints=npoints
        self.nfit=nfit
        self.trunc = trunc
        self.noisestd=noisestd 
        self.snr=snr 
        self.ppmscale=ppmscale      


def exctract_muscle_data( mrui_result , mrui_info, dfout , idx ):
    filename = mrui_info.filename
    snr = mrui_info.snr

    # Now collect peak aplitudes for EMCL. IMCL
    ch3e = get_metab_apml( mrui_result, srchstr = 'CH3e',  freq = 0.89, sdfreq= 0.15 )
    #print( 'Amplitude for CH3e = {A: 5g}'.format( A= ch3e))
    # Note that CH2 IMCL and EMCL sometimes get swapped by AMARES
    # frequency boudaries are used to pick the right peak
    ch2e = get_metab_apml( mrui_result, srchstr = 'CH2',  freq = 1.28, sdfreq= 0.15 )
    #print( 'Amplitude for CH2e = {A: 5g}'.format( A= ch2e))
    # IMCL
    ch3i = get_metab_apml( mrui_result, srchstr = 'CH3i',  freq = 1.02, sdfreq= 0.15 )
    #print( 'ASmplitude for CH3i = {A: 5g}'.format( A= ch3i))
    # get CH2 for IMCL based on higher frequency
    ch2i = get_metab_apml( mrui_result, srchstr = 'CH2',  freq = 1.47, sdfreq= 0.15 )
    #print( 'Amplitude for CH2i= {A: 5g}'.format( A= ch2i))

    # H2O
    h2o = get_metab_apml( mrui_result, srchstr = 'H2O',  freq = 4.67, sdfreq= 0.25 )
    #print( 'ASmplitude for H2O = {A: 5g}'.format( A= h2o))
    # Creatine
    cr = get_metab_apml( mrui_result, srchstr = 'Cr',  freq = 3.01, sdfreq= 0.25 )
    #print( 'ASmplitude for creatine = {A: 5g}'.format( A= cr))

    # Cho
    cho = get_metab_apml( mrui_result, srchstr = 'Cho',  freq = 3.20, sdfreq= 0.25 )
    #print( 'ASmplitude for choline = {A: 5g}'.format( A= cho))

    imcl = ch3i+ch2i
    emcl = ch3e+ch2e

    print( 'Total amplitude for IMCL = {AI: 5g} and EMCL = {AE: 5g}'.format( 
        AI= imcl, AE = emcl ))
    print( 'Total amplitude for water = {AI: 5g} '.format( AI= h2o ))

    data = {'File': filename, 'CH3e':ch3e, 'CH2e':ch2e, 'EMCL':emcl,
            'CH3i':ch3i, 'CH2i':ch2i, 'IMCL': imcl, 'H2O': h2o, 'Cr': cr, 'TMA': cho, 'SNR': snr }
    dfout = dfout.append( data , ignore_index=True )

    return dfout

def get_metab_apml( dataframe, srchstr = '',  freq = 0.0, sdfreq = 0.25 ):
    # get the (summed) peak amplitudes of one (or more) peaks, identified by label or freq
    totamp = 0

    for idx, label in enumerate( dataframe.Name ):
        if srchstr in label:
            thisampl = dataframe.iat[idx, 3]
            # Check if the amplitude is not a '*Not found*'
            if not type( thisampl ) == str:
                thisfreq = dataframe.iat[idx, 1]
                if (thisfreq > freq-sdfreq) and (thisfreq < freq+sdfreq):
                    print('Found {SRCH} in : {LBL} with amplitude {A: 5g} at freq {F: .3f}'.format(
                                SRCH = srchstr, LBL =label ,  A = thisampl , F = thisfreq ))            
                    totamp = totamp+thisampl

    return totamp
    # end get_metab_apml


def find_html_cell( textline, SearchStr):
# Appears to work!
    tabsep = '</th><td>'
    tabstop = '</td>'
    tseplen = len(tabsep)
    sstrlen = len(SearchStr)

    strpos1 = textline.find( SearchStr )+sstrlen+tseplen
    templine = textline[strpos1:-1]
    tabstppos = templine.find( tabstop )
    if tabstppos > 0:
        valuestr = templine[ 0:(tabstppos)]
    else:
        valuestr = ''

    #Where are we now in the inputsring?    
    endpos = strpos1 + len(valuestr) + len( tabstop)
    # Return the value string and the position after the closing tab
    return valuestr, endpos
    # end find_html_cell

def read_mruihtml_header( htmltext ):
    # Create and instance of the mrui_hdr class
    mrui_info = mrui_hdr()
    # Fill the values
    mrui_info.date, pos  = find_html_cell( htmltext, 'Date')
    mrui_info.filename, pos   = find_html_cell(  htmltext, 'Current file' )
    numvalstr, pos = find_html_cell( htmltext , 'Sampling Int. (ms)')
    mrui_info.tstep = float( numvalstr )

    numvalstr, pos = find_html_cell( htmltext , 'Zero Order (deg)' )
    # This string is either 'ph0 +/- sdph0' or 'ph0 fixed'
    parts = numvalstr.split()
    mrui_info.ph0 = float( parts[0])
    
    mrui_info.algor, pos = find_html_cell( htmltext,'Algorithm used' )

    numvalstr, pos = find_html_cell( htmltext, 'Points Signal/Quant.')
    parts = re.split('\/', numvalstr)
    mrui_info.npoints   = int(parts[0])
    mrui_info.nfit      = int(parts[1])
    
    numvalstr, pos = find_html_cell( htmltext,  'Truncated Points')
    mrui_info.nfit       = int(numvalstr)

    numvalstr, pos = find_html_cell( htmltext,  'Asked/found')
    parts = re.split('\/', numvalstr)
    mrui_info.npeaks   = int(parts[0])
    mrui_info.nfound   = int(parts[1])

    numvalstr, pos = find_html_cell( htmltext,  'Residue St.D.' )
    mrui_info.noisestd = float( numvalstr )

    numvalstr, lastpos = find_html_cell( htmltext,  'S/N' )
    mrui_info.snr = float( numvalstr )

    return mrui_info, lastpos
    # end read_mruihtml_header

def read_mrui_html( htmlfile):
    with open(htmlfile, "r", encoding='utf-8') as f:
        text= f.read()
    
    # Search for the title. This is the start of a single spectrum MRUI HTML result
    SearchStr = '<title>MRUI Quantitation Results</title>'
    titles = []
    result_texts = []
    # Empty list of mrui headers       
    mrui_infos = []
    # Empty list of mrui result dataframe tables 
    mrui_results = []
    # First check if this is a jMRUI HTML (publish/publ;ish all) results file
    if not text.find(SearchStr):
        print( 'Error in {FILE}: the input file {HTML} does not appear to be a result file created by jMRUI '.format(
            FILE = __file__, HTML = htmlfile ))
        return 
    
    for m in re.finditer(SearchStr, text):
        #print('title found', m.start(), m.end())
        titles.append( m )
        begin_idx =  m.end()
        # See if there is another title (i.e. spectrum result) following the current title
        next_title_index = text.find(SearchStr, begin_idx)
        # If there is one, take all text between the titles and add it to the list
        if next_title_index > 0:
            end_idx = next_title_index +1
            result_texts.append(text[ begin_idx:end_idx ])  
        else: # if there is not another title ahead, take all the remaining html text
            result_texts.append(text[ begin_idx:-1 ])  

    # Create a list of mrui headers, one for each fitted spectrum       
    # mrui_infos = [] = output arg 1, already defined
    # Create a list of mrui result tables, one for each fitted spectrum 
    # mrui_results = [] = output arg 2, already defined
    for thisresult in result_texts:
        this_mrui_hdr, lastpos = read_mruihtml_header(thisresult) 
        #print( 'This result HTML is {LEN} chars long. We now chop off the first {LPOS}'.format(LEN = len( thisresult), LPOS = lastpos ))
        # Now interpret the rest of the tables
        found_result_tables = pd.read_html(thisresult[ lastpos:-1] )
        #print('\nFound this table:')
        #print(found_result_tables )
        mrui_results.append( found_result_tables[0] )
        # find out what the frequency scale is
        freqhdr =  found_result_tables[0].columns.values[1]
        if 'ppm' in freqhdr: 
            this_mrui_hdr.ppmscle = 1
        # Add this mrui header to the list
        mrui_infos.append( this_mrui_hdr )

    return mrui_infos, mrui_results
    # end read_mrui_html

if __name__ == "__main__":
    main()
