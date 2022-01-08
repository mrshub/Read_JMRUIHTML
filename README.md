# Read_MRUIHTML

This is the repository for the MRSHub submission "Read_MRUIHTML" (submitted by [Ronald Ouwerkerk, NIDDK/NIH, Bethesda MD, USA](ouwerkerkr@niddk.nih.gov)).

## Guidance

I used panda tools in Python to interpret the HTML code and produce the output table as an Excel file.
The output of the module is an Excel file with one row per spectrum, and the peak amplitudes (plus some summed peaks amplitudes e.g. CH3+CH2 for IMCL or EMCL) and the SNR estimates.
This module can easily be customized to other types of spectra.

Sample output:

Processing HISTO_TE14TR3000TE014.html in folder /Users/…/HISTO_TE1420_1

Found CH3e in : 1 - CH3e - G with amplitude 6.487e-06 at freq 0.837
Found CH2 in : 3 - CH2i - G with amplitude 0.0002168 at freq 1.287
Found CH3i in : 2 - CH3i - G with amplitude 1.945e-06 at freq 0.940
Found CH2 in : 4 - CH2e - G with amplitude 0.001116 at freq 1.526
Found H2O in : 7 - H2Og - G with amplitude 0.003779 at freq 4.645
Found H2O in : 8 - L H2Ol with amplitude 0.0609 at freq 4.681
Found Cr in : 5 - Cr - G with amplitude 0.0002037 at freq 3.018
Found Cho in : 6 - Cho - G with amplitude 0.0002216 at freq 3.300
Total amplitude for IMCL = 0.00111794 and EMCL = 0.000223287
Total amplitude for water = 0.064679
…etc,
for each spectrum…
Found Cr in : 5 - Cr - G with amplitude 5.493e-05 at freq 3.006
Found Cho in : 6 - Cho - G with amplitude 2.918e-05 at freq 3.180
Total amplitude for IMCL = 0.0007829 and EMCL = 0.00019337
Total amplitude for water = 0.0089116

https://forum.mrshub.org/t/processing-jmrui-publish-all-html-files-python-module/644

## Acknowledgement

If you would be so kind to acknowledge me as the source of this software when you use it for a publication it will be much appreciated.
