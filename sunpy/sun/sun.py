"""
This module provides Sun-related parameters.
"""
import numpy as np

import astropy.units as u
from astropy.coordinates import Angle, Latitude, Longitude, SkyCoord
# Versions of Astropy that do not have *MeanEcliptic frames have the same frames
# with the misleading names *TrueEcliptic
try:
    from astropy.coordinates import HeliocentricMeanEcliptic, GeocentricMeanEcliptic
except ImportError:
    from astropy.coordinates import HeliocentricTrueEcliptic as HeliocentricMeanEcliptic
    from astropy.coordinates import GeocentricTrueEcliptic as GeocentricMeanEcliptic
from astropy import _erfa as erfa
from astropy.coordinates.builtin_frames.utils import get_jd12

from sunpy.sun import constants
from sunpy.time import parse_time
from sunpy.time.time import _variables_for_parse_time_docstring
from sunpy.util.decorators import add_common_docstring

__all__ = [
    "solar_cycle_number", "solar_semidiameter_angular_size", "carrington_rotation_number",
    "position",
    "true_longitude", "apparent_longitude", "true_latitude", "apparent_latitude",
    "mean_obliquity_of_ecliptic", "true_rightascension", "true_declination",
    "true_obliquity_of_ecliptic", "apparent_rightascension", "apparent_declination",
    "print_params"
]


@add_common_docstring(**_variables_for_parse_time_docstring())
def solar_cycle_number(t='now'):
    """
    Return the solar cycle number.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    time = parse_time(t)
    result = (int(time.strftime('%Y')) + 8) % 28 + 1
    return result


@add_common_docstring(**_variables_for_parse_time_docstring())
def solar_semidiameter_angular_size(t='now'):
    """
    Return the angular size of the semi-diameter of the Sun as viewed from Earth.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    # Import here to avoid a circular import
    from sunpy.coordinates import get_sunearth_distance
    solar_semidiameter_rad = constants.radius / get_sunearth_distance(t)
    return Angle(solar_semidiameter_rad.to(u.arcsec, equivalencies=u.dimensionless_angles()))


@add_common_docstring(**_variables_for_parse_time_docstring())
def position(t='now', equinox_of_date=True):
    """
    Returns the apparent position of the Sun (right ascension and declination) on the
    celestial sphere using the equatorial coordinate system, referred to the true equinox of date
    (as default).  Corrections for nutation and aberration (for Earth motion) are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    equinox_of_date : `bool`
        If True, output is referred to the true equinox of date.  Otherwise, output is referred to
        the J2000.0 epoch.
    """
    ra = apparent_rightascension(t, equinox_of_date=equinox_of_date)
    dec = apparent_declination(t, equinox_of_date=equinox_of_date)
    return ra, dec


@add_common_docstring(**_variables_for_parse_time_docstring())
def carrington_rotation_number(t='now'):
    """
    Return the Carrington Rotation number.

    .. warning::
        The accuracy of this function is under investigation.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    jd = parse_time(t).jd
    result = (1. / 27.2753) * (jd - 2398167.0) + 1.0
    return result


@add_common_docstring(**_variables_for_parse_time_docstring())
def true_longitude(t='now'):
    """
    Returns the Sun's true geometric longitude, referred to the mean equinox of date.  No
    corrections for nutation or aberration are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    time = parse_time(t)

    # Calculate Earth's true geometric longitude and add 180 degrees for the Sun's longitude.
    # This approach is used because Astropy's GeocentricMeanEcliptic includes aberration.
    earth = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='gcrs', obstime=time)
    coord = earth.transform_to(HeliocentricMeanEcliptic(equinox=time))
    lon = coord.lon + 180*u.deg

    return Longitude(lon)


@add_common_docstring(**_variables_for_parse_time_docstring())
def apparent_longitude(t='now'):
    """
    Returns the Sun's apparent longitude, referred to the true equinox of date.  Corrections for
    nutation and aberration (for Earth motion) are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    Notes
    -----
    The nutation model is IAU 2000A nutation with adjustments to match IAU 2006 precession.
    """
    time = parse_time(t)
    sun = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='hcrs', obstime=time)
    coord = sun.transform_to(GeocentricMeanEcliptic(equinox=time))

    # Astropy's GeocentricMeanEcliptic already includes aberration, so only add nutation
    jd1, jd2 = get_jd12(time, 'tt')
    nut_lon, _ = erfa.nut06a(jd1, jd2)*u.radian
    lon = coord.lon + nut_lon

    return Longitude(lon)


@add_common_docstring(**_variables_for_parse_time_docstring())
def true_latitude(t='now'):
    """
    Returns the Sun's true geometric latitude, referred to the mean equinox of date.  No
    corrections for nutation or aberration are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    time = parse_time(t)
    sun = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='hcrs', obstime=time)
    coord = sun.transform_to(GeocentricMeanEcliptic(equinox=time))

    # Astropy's GeocentricMeanEcliptic includes aberration from Earth motion, but the contribution
    # is negligible
    lat = coord.lat

    return Latitude(lat)


@add_common_docstring(**_variables_for_parse_time_docstring())
def apparent_latitude(t='now'):
    """
    Returns the Sun's apparent latitude, referred to the true equinox of date.  Corrections for
    nutation and aberration (for Earth motion) are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    time = parse_time(t)
    sun = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='hcrs', obstime=time)
    coord = sun.transform_to(GeocentricMeanEcliptic(equinox=time))

    # Astropy's GeocentricMeanEcliptic does not include nutation, but the contribution is negligible
    lat = coord.lat

    return Latitude(lat)


@add_common_docstring(**_variables_for_parse_time_docstring())
def mean_obliquity_of_ecliptic(t='now'):
    """
    Returns the mean obliquity of the ecliptic, using the IAU 2006 definition.  No correction for
    nutation is included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    time = parse_time(t)
    jd1, jd2 = get_jd12(time, 'tt')
    obl = erfa.obl06(jd1, jd2)*u.radian
    return Angle(obl, u.arcsec)


@add_common_docstring(**_variables_for_parse_time_docstring())
def true_rightascension(t='now', equinox_of_date=True):
    """
    Returns the Sun's true geometric right ascension relative to Earth, referred to the mean equinox
    of date (as default).  No corrections for nutation or aberration are included.  The correction
    due to light travel time would be negligible, so the output is also the astrometric right
    ascension.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    equinox_of_date : `bool`
        If True, output is referred to the mean equinox of date.  Otherwise, output is referred to
        the J2000.0 epoch.
    """
    if equinox_of_date:
        # Mean equinox of date
        obl = mean_obliquity_of_ecliptic(t)  # excludes nutation
        lon = true_longitude(t)
        lat = true_latitude(t)

        # See Astronomical Algorithms (Meeus 1998 p.93)
        y = np.sin(lon) * np.cos(obl) - np.tan(lat) * np.sin(obl)
        x = np.cos(lon)
        result = np.arctan2(y, x)
    else:
        # J2000.0 epoch
        # Calculate Earth's true geometric right ascension relative to the Sun and add 180 degrees.
        # This approach is used because Astropy's GCRS includes aberration.
        earth = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='gcrs', obstime=parse_time(t))
        result = earth.hcrs.ra + 180*u.deg

    return Longitude(result, u.hourangle)


@add_common_docstring(**_variables_for_parse_time_docstring())
def true_declination(t='now', equinox_of_date=True):
    """
    Returns the Sun's true geometric declination relative to Earth, referred to the mean equinox
    of date (as default).  No corrections for nutation or aberration are included.  The correction
    due to light travel time would be negligible, so the output is also the astrometric declination.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    equinox_of_date : `bool`
        If True, output is referred to the mean equinox of date.  Otherwise, output is referred to
        the J2000.0 epoch.
    """
    if equinox_of_date:
        # Mean equinox of date
        obl = mean_obliquity_of_ecliptic(t)  # excludes nutation
        lon = true_longitude(t)
        lat = true_latitude(t)

        # See Astronomical Algorithms (Meeus 1998 p.93)
        result = np.arcsin(np.sin(lat) * np.cos(obl) + np.cos(lat) * np.sin(obl) * np.sin(lon))
    else:
        # J2000.0 epoch
        # Calculate Earth's true geometric declination relative to the Sun and multipy by -1.
        # This approach is used because Astropy's GCRS includes aberration.
        earth = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='gcrs', obstime=parse_time(t))
        result = -earth.hcrs.dec

    return Latitude(result, u.deg)


@add_common_docstring(**_variables_for_parse_time_docstring())
def true_obliquity_of_ecliptic(t='now'):
    """
    Returns the true obliquity of the ecliptic, using the IAU 2006 definition.  Correction for
    nutation is included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    Notes
    -----
    The nutation model is IAU 2000A nutation with adjustments to match IAU 2006 precession.
    """
    time = parse_time(t)
    jd1, jd2 = get_jd12(time, 'tt')
    obl = erfa.obl06(jd1, jd2)*u.radian
    _, nut_obl = erfa.nut06a(jd1, jd2)*u.radian
    obl += nut_obl
    return Angle(obl, u.arcsec)


@add_common_docstring(**_variables_for_parse_time_docstring())
def apparent_rightascension(t='now', equinox_of_date=True):
    """
    Returns the Sun's apparent right ascension relative to Earth, referred to the true equinox
    of date (as default).  Corrections for nutation or aberration (for Earth motion) are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    equinox_of_date : `bool`
        If True, output is referred to the true equinox of date.  Otherwise, output is referred to
        the J2000.0 epoch.
    """
    if equinox_of_date:
        # True equinox of date
        obl = true_obliquity_of_ecliptic(t)  # includes nutation
        lon = apparent_longitude(t)
        lat = apparent_latitude(t)

        # See Astronomical Algorithms (Meeus 1998 p.93)
        y = np.sin(lon) * np.cos(obl) - np.tan(lat) * np.sin(obl)
        x = np.cos(lon)
        result = np.arctan2(y, x)
    else:
        # J2000.0 epoch
        sun = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='hcrs', obstime=parse_time(t))
        result = sun.gcrs.ra

    return Longitude(result, u.hourangle)


@add_common_docstring(**_variables_for_parse_time_docstring())
def apparent_declination(t='now', equinox_of_date=True):
    """
    Returns the Sun's apparent declination relative to Earth, referred to the true equinox
    of date (as default).  Corrections for nutation or aberration (for Earth motion) are included.

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.

    equinox_of_date : `bool`
        If True, output is referred to the true equinox of date.  Otherwise, output is referred to
        the J2000.0 epoch.
    """
    if equinox_of_date:
        # True equinox of date
        obl = true_obliquity_of_ecliptic(t)  # includes nutation
        lon = apparent_longitude(t)
        lat = apparent_latitude(t)

        # See Astronomical Algorithms (Meeus 1998 p.93)
        result = np.arcsin(np.sin(lat) * np.cos(obl) + np.cos(lat) * np.sin(obl) * np.sin(lon))
    else:
        # J2000.0 epoch
        sun = SkyCoord(0*u.deg, 0*u.deg, 0*u.AU, frame='hcrs', obstime=parse_time(t))
        result = sun.gcrs.dec

    return Latitude(result, u.deg)


@add_common_docstring(**_variables_for_parse_time_docstring())
def print_params(t='now'):
    """
    Print out a summary of solar ephemeris. 'True' values are true geometric values referred to the
    mean equinox of date, with no corrections for nutation or aberration.  'Apparent' values are
    referred to the true equinox of date, with corrections for nutation and aberration (for Earth
    motion).

    Parameters
    ----------
    t : {parse_time_types}
        A time (usually the start time) specified as a parse_time-compatible
        time string, number, or a datetime object.
    """
    # Import here to avoid circular import
    from sunpy.coordinates.ephemeris import (get_sun_L0, get_sun_B0,
                                             get_sun_P, get_sunearth_distance)

    print('Solar Ephemeris for {} UTC\n'.format(parse_time(t).utc))
    print('Distance = {}'.format(get_sunearth_distance(t)))
    print('Semidiameter = {}'.format(solar_semidiameter_angular_size(t)))
    print('True (long, lat) = ({}, {})'.format(true_longitude(t).to_string(),
                                               true_latitude(t).to_string()))
    print('Apparent (long, lat) = ({}, {})'.format(apparent_longitude(t).to_string(),
                                                   apparent_latitude(t).to_string()))
    print('True (RA, Dec) = ({}, {})'.format(true_rightascension(t).to_string(),
                                             true_declination(t).to_string()))
    print('Apparent (RA, Dec) = ({}, {})'.format(apparent_rightascension(t).to_string(),
                                                 apparent_declination(t).to_string()))
    print('Heliographic long. and lat of disk center = ({}, {})'.format(get_sun_L0(t).to_string(),
                                                                        get_sun_B0(t).to_string()))
    print('Position angle of north pole = {}'.format(get_sun_P(t)))
    print('Carrington Rotation Number = {}'.format(carrington_rotation_number(t)))
