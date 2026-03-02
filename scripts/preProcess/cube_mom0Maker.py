# You MUST put this script on feifei,
# because of the hard-coded folder path
'''
make mom0 with different noise, 意外的很成功欸?
Tech ref:
- spectral axis unit convertion: https://spectral-cube.readthedocs.io/en/latest/moments.html#moment-maps
- noise masking on cubes:        https://spectral-cube.readthedocs.io/en/latest/masking.html#getting-started
- generate and show moment maps: https://learn.astropy.org/tutorials/FITS-cubes.html#display-the-moment-maps
'''

from astropy import units as u
import matplotlib.pyplot as plt
from spectral_cube import SpectralCube
import warnings

# 因為噴一堆東西有點煩煩的
warnings.filterwarnings('ignore', message='.*PV2.*')

# Path
projectRoot = '/Users/aqing/Documents/1004/line-modeling_Circinus'
dataPath = f'{projectRoot}/data/alma_cube/smoothed_cube'
mom0Path = f'{projectRoot}/data/mom0'

# (mole_fileName, band_fileName, restFrequency(GHz), spectralLine_freq(GHz), noise(Jy/beam))
moles_info = [('co-10',   '3b', 115.271, (115.041660, 115.172025), 0.00525), # [freq]:GHz !!
              ('13co-10', '3a', 110.201, (109.974831, 110.108133), 0.00366),
              ('c18o-10', '3a', 109.782, (109.561252, 109.665745), 0.00381),
              #('co-21',   '6a', 230.538, (), 0.00378), # 幹這個壞掉
              ('13co-21', '6a', 220.399, (219,936696, 220.215985), 0.00383),
              ('c18o-21', '6a', 219.560, (219.126176, 219.364939), 0.00407),
              ]
z = 0.001448 * u.dimensionless_unscaled # Circinus's redshift
Nsigma = [3.0, 3.5, 4.0, 4.5, 5.0]

# Main -- Making Moment Zero
for molename, band, f0, freqrange, noise in moles_info:
    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')

    # Extract Spefic Freq Range
    slab = cube.spectral_slab(freqrange[0]*u.GHz, freqrange[1]*u.GHz)

    # Unit Convert: Hz ---> km/s
    slab = slab.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=f0*u.GHz)

    # Making Moment Zero Maps  & Plot 
    for n in Nsigma:
        # Noise Masking
        noiseMask = slab > (n*noise) * (u.Jy/u.beam) 
        slab_masked = slab.with_mask(noiseMask)
        # Integrating
        mom0 = slab_masked.moment(order=0)
        # Save as FITS
        mom0.write(f'{mom0Path}/mom0_{molename}_smooth3.2as_{n}sigma.fits', overwrite=True)
        print(f"{molename}'s moment zero map (masked {n} sigma) was saved as FITS.")

# Show Spectral Figures
fig, ax2 = plt.subplots(3, 2, figsize=(12, 8))
ax = ax2.flatten()

for fig_idx, (molename, band, f0, freqrange, _) in enumerate(moles_info):
    f0 = f0 * u.GHz
    # Load the Cube Again ;)
    cube = SpectralCube.read(
        f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits'
        ).with_spectral_unit( 
        u.km/u.s, velocity_convention='radio', rest_value=f0 # velocity_axis
        )
    
    # Get Axes Info
    samplePix = int(cube.header['CRPIX1'])
    specData = cube[:, samplePix, samplePix]
    velo_axis = specData.spectral_axis

    # Plot the Spectrum
    ax[fig_idx].plot(velo_axis, specData, lw=1, color='k')
    ax[fig_idx].axhline(0, lw=0.5, linestyle='--', color='k')
    ax[fig_idx].set_title(f'{molename} spectrum pix({samplePix}, {samplePix})')
    if fig_idx > 3:
        ax[fig_idx].set_xlabel(f'Radio Velocity ({velo_axis.unit})')
    if (fig_idx % 2) == 0:
        ax[fig_idx].set_ylabel(f'Flux Density ({specData.unit})')

    # Mark the Spectral Line (shifted, in velocity unit) 
    f_s = f0 / (1+z)
    veloline = f_s.to(velo_axis.unit, equivalencies=u.doppler_radio(f0)).value
    ax[fig_idx].axvline(veloline, lw=0.7, color='r')
    ax[fig_idx].text(veloline, min(specData.value), f'{molename}',
                     rotation=90, color='r', fontsize=8, ha='right', va='bottom')

    # Mark the Intergral Range (in Velocityyyy)
    for f in freqrange:
        velorange = (f * u.GHz).to(u.km/u.s, equivalencies=u.doppler_radio(f0))
        velorange = velorange.value
        ax[fig_idx].axvline(velorange, lw=0.5, color='b')
        ax[fig_idx].text(velorange, max(specData.value)*0.5, f'{velorange:.2f} {velo_axis.unit}', 
                    rotation=90, color='b', fontsize=8, ha='right', va='bottom')
plt.tight_layout()
plt.show()    # Load the Cube
    cube = SpectralCube.read(f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits')
    print(f'cube_Band{band}_{molename}_smooth3.2as.fits was loaded.')

    # Extract Spefic Freq Range
    slab = cube.spectral_slab(freqrange[0]*u.GHz, freqrange[1]*u.GHz)

    # Unit Convert: Hz ---> km/s
    slab = slab.with_spectral_unit(u.km/u.s, velocity_convention='radio', rest_value=f0*u.GHz)

    # Making Moment Zero Maps  & Plot 
    for n in Nsigma:
        # Noise Masking
        noiseMask = slab > (n*noise) * (u.Jy/u.beam) 
        slab_masked = slab.with_mask(noiseMask)
        # Integrating
        mom0 = slab_masked.moment(order=0)
        # Save as FITS
        mom0.write(f'{mom0Path}/mom0_{molename}_smooth3.2as_{n}sigma.fits', overwrite=True)
        print(f"{molename}'s moment zero map (masked {n} sigma) was saved as FITS.")

print(':))')

# Spectral Figure
fig, ax2 = plt.subplots(3, 2, figsize=(12, 8))
ax = ax2.flatten()
for fig_idx, (molename, band, f0, freqrange, _) in enumerate(moles_info):
    f0 = f0 * u.GHz
    # Load the Cube Again ;)
    cube = SpectralCube.read(
        f'{dataPath}/cube_Band{band}_{molename}_smooth3.2as.fits'
        ).with_spectral_unit( 
        u.km/u.s, velocity_convention='radio', rest_value=f0 # velocity_axis
        )
    
    # Get Axes Info
    samplePix = int(cube.header['CRPIX1']) # 偷懶了
    specData = cube[:, samplePix, samplePix]
    velo_axis = specData.spectral_axis

    # Plot the Spectrum
    ax[fig_idx].plot(velo_axis, specData, lw=1, color='k')
    ax[fig_idx].axhline(0, lw=0.5, linestyle='--', color='k') # 零線
    ax[fig_idx].set_title(f'{molename} spectrum pix({samplePix}, {samplePix})')
    if fig_idx > 3:
        ax[fig_idx].set_xlabel(f'Radio Velocity ({velo_axis.unit})')
    if (fig_idx % 2) == 0:
        ax[fig_idx].set_ylabel(f'Flux Density ({specData.unit})')

    # Mark the Spectral Line (shifted, in velocity unit) 
    f_s = f0 / (1+z)
    veloline = f_s.to(velo_axis.unit, equivalencies=u.doppler_radio(f0)).value
    ax[fig_idx].axvline(veloline, lw=0.7, color='r')
    ax[fig_idx].text(veloline, 0, f'{molename}',
                     rotation=90, color='r', fontsize=8, ha='right', va='bottom') # 操了怎麼字放在哪裡都巨醜

    # Mark the Intergral Range (in Velocityyyy)
    for f in freqrange: # 'tuple' object has no attribute 'to'
        velorange = (f * u.GHz).to(u.km/u.s, equivalencies=u.doppler_radio(f0)) # 這邊用的就是 astropy.units 的技術了
        velorange = velorange.value # 之後要用到的地方都不能帶單位
        ax[fig_idx].axvline(velorange, lw=0.5, color='b') # vlines(), np.min() 裡面不能放有單位的東西
        ax[fig_idx].text(velorange, max(specData.value)*0.5, f'{velorange:.2f} {velo_axis.unit}', 
                    rotation=90, color='b', fontsize=8, ha='right', va='bottom')
plt.tight_layout()
plt.show()
