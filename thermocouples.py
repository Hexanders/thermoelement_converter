"""
Thermocouple conversion functions using NIST ITS-90 polynomial coefficients.
Provides temperature <-> voltage conversion for standard thermocouple types.
"""

import numpy as np
from scipy.optimize import fsolve


class Thermocouple:
    """Base class for thermocouple types."""

    def __init__(self, name, temp_ranges, emf_coeffs, inv_coeffs, inv_voltage_ranges, temp_to_emf_ranges=None):
        """
        Initialize thermocouple.

        Args:
            name: Thermocouple type (e.g., 'K', 'J')
            temp_ranges: List of (min_temp, max_temp) tuples for each coefficient set
            emf_coeffs: List of polynomial coefficient arrays for temp->EMF conversion
            inv_coeffs: List of polynomial coefficient arrays for EMF->temp conversion
            inv_voltage_ranges: List of (min_mv, max_mv) tuples for each inverse coefficient set
            temp_to_emf_ranges: Optional separate ranges for temp->EMF (if different from temp_ranges)
        """
        self.name = name
        self.temp_ranges = temp_ranges
        self.emf_coeffs = emf_coeffs
        self.inv_coeffs = inv_coeffs
        self.inv_voltage_ranges = inv_voltage_ranges
        self.temp_to_emf_ranges = temp_to_emf_ranges or temp_ranges

    def emf_mVC(self, temp_c, Tref=0.0):
        """
        Convert temperature (Celsius) to EMF (millivolts).

        Args:
            temp_c: Temperature in Celsius
            Tref: Reference junction temperature in Celsius (default 0°C)

        Returns:
            EMF in millivolts
        """
        emf_hot = self._temp_to_emf(temp_c)
        emf_ref = self._temp_to_emf(Tref)
        return emf_hot - emf_ref

    def inverse_CmV(self, emf_mv, Tref=0.0):
        """
        Convert EMF (millivolts) to temperature (Celsius).

        Args:
            emf_mv: EMF in millivolts
            Tref: Reference junction temperature in Celsius (default 0°C)

        Returns:
            Temperature in Celsius
        """
        # Add reference junction EMF
        emf_ref = self._temp_to_emf(Tref)
        emf_total = emf_mv + emf_ref

        return self._emf_to_temp(emf_total)

    def get_voltage_range(self):
        """
        Get the valid voltage range for this thermocouple type.

        Returns:
            Tuple of (min_voltage, max_voltage) in millivolts
        """
        min_v = self.inv_voltage_ranges[0][0]
        max_v = self.inv_voltage_ranges[-1][1]
        return (min_v, max_v)

    def _temp_to_emf(self, temp_c):
        """Convert temperature to EMF using polynomial coefficients."""
        for i, (t_min, t_max) in enumerate(self.temp_to_emf_ranges):
            if t_min <= temp_c <= t_max:
                coeffs = self.emf_coeffs[i]
                # Use Horner's method for polynomial evaluation
                result = 0.0
                for j, coeff in enumerate(coeffs):
                    result += coeff * (temp_c ** j)
                return result

        raise ValueError(f"Temperature {temp_c}°C out of range for type {self.name}")

    def _emf_to_temp(self, emf_mv):
        """Convert EMF to temperature using polynomial coefficients."""
        # Find the correct voltage range
        for i, (v_min, v_max) in enumerate(self.inv_voltage_ranges):
            if v_min <= emf_mv <= v_max:
                coeffs = self.inv_coeffs[i]
                # Use Horner's method for polynomial evaluation
                result = 0.0
                for j, coeff in enumerate(coeffs):
                    result += coeff * (emf_mv ** j)
                return result

        # If no range matches, use numerical solver
        def equation(t):
            return self._temp_to_emf(t) - emf_mv

        # Estimate initial guess
        t_guess = emf_mv * 25  # Rough estimate
        try:
            result = fsolve(equation, t_guess)[0]
            return result
        except:
            raise ValueError(f"EMF {emf_mv} mV out of range for type {self.name}")


# Type K Thermocouple (Chromel-Alumel)
# Temperature range: -270°C to 1372°C
TYPE_K = Thermocouple(
    name='K',
    temp_ranges=[(-270, 0), (0, 1372)],
    emf_coeffs=[
        # -270 to 0°C
        np.array([
            0.000000000000E+00,
            0.394501280250E-01,
            0.236223735980E-04,
            -0.328589067840E-06,
            -0.499048287770E-08,
            -0.675090591730E-10,
            -0.574103274280E-12,
            -0.310888728940E-14,
            -0.104516093650E-16,
            -0.198892668780E-19,
            -0.163226974860E-22
        ]),
        # 0 to 1372°C
        np.array([
            -0.176004136860E-01,
            0.389212049750E-01,
            0.185587700320E-04,
            -0.994575928740E-07,
            0.318409457190E-09,
            -0.560728448890E-12,
            0.560750590590E-15,
            -0.320207200030E-18,
            0.971511471520E-22,
            -0.121047212750E-25
        ])
    ],
    inv_coeffs=[
        # -5.891 to 0 mV
        np.array([
            0.0000000E+00,
            2.5173462E+01,
            -1.1662878E+00,
            -1.0833638E+00,
            -8.9773540E-01,
            -3.7342377E-01,
            -8.6632643E-02,
            -1.0450598E-02,
            -5.1920577E-04
        ]),
        # 0 to 20.644 mV
        np.array([
            0.000000E+00,
            2.508355E+01,
            7.860106E-02,
            -2.503131E-01,
            8.315270E-02,
            -1.228034E-02,
            9.804036E-04,
            -4.413030E-05,
            1.057734E-06,
            -1.052755E-08
        ]),
        # 20.644 to 54.886 mV
        np.array([
            -1.318058E+02,
            4.830222E+01,
            -1.646031E+00,
            5.464731E-02,
            -9.650715E-04,
            8.802193E-06,
            -3.110810E-08
        ])
    ],
    inv_voltage_ranges=[
        (-5.891, 0.0),
        (0.0, 20.644),
        (20.644, 54.886)
    ]
)

# Type J Thermocouple (Iron-Constantan)
# Temperature range: -210°C to 1200°C
TYPE_J = Thermocouple(
    name='J',
    temp_ranges=[(-210, 760), (760, 1200)],
    emf_coeffs=[
        # -210 to 760°C
        np.array([
            0.000000000000E+00,
            0.503811878150E-01,
            0.304758369300E-04,
            -0.856810657200E-07,
            0.132281952950E-09,
            -0.170529583370E-12,
            0.209480906970E-15,
            -0.125383953360E-18,
            0.156317256970E-22
        ]),
        # 760 to 1200°C
        np.array([
            0.296456256810E+03,
            -0.149761277860E+01,
            0.317871039240E-02,
            -0.318476867010E-05,
            0.157208190040E-08,
            -0.306913690560E-12
        ])
    ],
    inv_coeffs=[
        # -8.095 to 0 mV
        np.array([
            0.0000000E+00,
            1.9528268E+01,
            -1.2286185E+00,
            -1.0752178E+00,
            -5.9086933E-01,
            -1.7256713E-01,
            -2.8131513E-02,
            -2.3963370E-03,
            -8.3823321E-05
        ]),
        # 0 to 42.919 mV
        np.array([
            0.000000E+00,
            1.978425E+01,
            -2.001204E-01,
            1.036969E-02,
            -2.549687E-04,
            3.585153E-06,
            -5.344285E-08,
            5.099890E-10
        ]),
        # 42.919 to 69.553 mV
        np.array([
            -3.11358187E+03,
            3.00543684E+02,
            -9.94773230E+00,
            1.70276630E-01,
            -1.43033468E-03,
            4.73886084E-06
        ])
    ],
    inv_voltage_ranges=[
        (-8.095, 0.0),
        (0.0, 42.919),
        (42.919, 69.553)
    ]
)

# Type T Thermocouple (Copper-Constantan)
# Temperature range: -270°C to 400°C
TYPE_T = Thermocouple(
    name='T',
    temp_ranges=[(-270, 0), (0, 400)],
    emf_coeffs=[
        # -270 to 0°C
        np.array([
            0.000000000000E+00,
            0.387481063640E-01,
            0.441944343470E-04,
            0.118443231050E-06,
            0.200329735540E-07,
            0.901380195590E-09,
            0.226511565930E-10,
            0.360711542050E-12,
            0.384939398830E-14,
            0.282135219250E-16,
            0.142515947790E-18,
            0.487686622860E-21,
            0.107955392700E-23,
            0.139450270620E-26,
            0.797951539270E-30
        ]),
        # 0 to 400°C
        np.array([
            0.000000000000E+00,
            0.387481063640E-01,
            0.332922278800E-04,
            0.206182434040E-06,
            -0.218822568460E-08,
            0.109968809280E-10,
            -0.308157587720E-13,
            0.454791352900E-16,
            -0.275129016730E-19
        ])
    ],
    inv_coeffs=[
        # -5.603 to 0 mV
        np.array([
            0.0000000E+00,
            2.5949192E+01,
            -2.1316967E-01,
            7.9018692E-01,
            4.2527777E-01,
            1.3304473E-01,
            2.0241446E-02,
            1.2668171E-03
        ]),
        # 0 to 20.872 mV
        np.array([
            0.000000E+00,
            2.592800E+01,
            -7.602961E-01,
            4.637791E-02,
            -2.165394E-03,
            6.048144E-05,
            -7.293422E-07
        ])
    ],
    inv_voltage_ranges=[
        (-5.603, 0.0),
        (0.0, 20.872)
    ]
)

# Type E Thermocouple (Chromel-Constantan)
# Temperature range: -270°C to 1000°C
TYPE_E = Thermocouple(
    name='E',
    temp_ranges=[(-270, 0), (0, 1000)],
    emf_coeffs=[
        # -270 to 0°C
        np.array([
            0.000000000000E+00,
            0.586655087080E-01,
            0.454109771240E-04,
            -0.779980486860E-06,
            -0.258001608430E-07,
            -0.594525830570E-09,
            -0.932140586670E-11,
            -0.102876055340E-12,
            -0.803701236210E-15,
            -0.439794973910E-17,
            -0.164147763550E-19,
            -0.396736195160E-22,
            -0.558273287210E-25,
            -0.346578420130E-28
        ]),
        # 0 to 1000°C
        np.array([
            0.000000000000E+00,
            0.586655087080E-01,
            0.450322755820E-04,
            0.289084072120E-07,
            -0.330568966520E-09,
            0.650244032700E-12,
            -0.191974955040E-15,
            -0.125366004970E-17,
            0.214892175690E-20,
            -0.143880417820E-23,
            0.359608994810E-27
        ])
    ],
    inv_coeffs=[
        # -8.825 to 0 mV
        np.array([
            0.0000000E+00,
            1.6977288E+01,
            -4.3514970E-01,
            -1.5859697E-01,
            -9.2502871E-02,
            -2.6084314E-02,
            -4.1360199E-03,
            -3.4034030E-04,
            -1.1564890E-05
        ]),
        # 0 to 76.373 mV
        np.array([
            0.0000000E+00,
            1.7057035E+01,
            -2.3301759E-01,
            6.5435585E-03,
            -7.3562749E-05,
            -1.7896001E-06,
            8.4036165E-08,
            -1.3735879E-09,
            1.0629823E-11,
            -3.2447087E-14
        ])
    ],
    inv_voltage_ranges=[
        (-8.825, 0.0),
        (0.0, 76.373)
    ]
)

# Type N Thermocouple (Nicrosil-Nisil)
# Temperature range: -270°C to 1300°C
TYPE_N = Thermocouple(
    name='N',
    temp_ranges=[(-270, 0), (0, 1300)],
    emf_coeffs=[
        # -270 to 0°C
        np.array([
            0.000000000000E+00,
            0.261591059620E-01,
            0.109574842280E-04,
            -0.938411115540E-07,
            -0.464120397590E-10,
            -0.263033577160E-11,
            -0.226534380030E-13,
            -0.760893007910E-16,
            -0.934196678350E-19
        ]),
        # 0 to 1300°C
        np.array([
            0.000000000000E+00,
            0.259293946010E-01,
            0.157101418800E-04,
            0.438256272370E-07,
            -0.252611697940E-09,
            0.643118193390E-12,
            -0.100634715190E-14,
            0.997453389920E-18,
            -0.608632456070E-21,
            0.208492293390E-24,
            -0.306821961510E-28
        ])
    ],
    inv_coeffs=[
        # -3.990 to 0 mV
        np.array([
            0.0000000E+00,
            3.8436847E+01,
            1.1010485E+00,
            5.2229312E+00,
            7.2060525E+00,
            5.8488586E+00,
            2.7754916E+00,
            7.7075166E-01,
            1.1582665E-01,
            7.3138868E-03
        ]),
        # 0 to 20.613 mV
        np.array([
            0.00000E+00,
            3.86896E+01,
            -1.08267E+00,
            4.70205E-02,
            -2.12169E-06,
            -1.17272E-04,
            5.39280E-06,
            -7.98156E-08
        ]),
        # 20.613 to 47.513 mV
        np.array([
            1.972485E+01,
            3.300943E+01,
            -3.915159E-01,
            9.855391E-03,
            -1.274371E-04,
            7.767022E-07
        ])
    ],
    inv_voltage_ranges=[
        (-3.990, 0.0),
        (0.0, 20.613),
        (20.613, 47.513)
    ]
)

# Type S Thermocouple (Platinum-10% Rhodium/Platinum)
# Temperature range: -50°C to 1768°C
TYPE_S = Thermocouple(
    name='S',
    temp_ranges=[(-50, 1064.18), (1064.18, 1664.5), (1664.5, 1768)],
    emf_coeffs=[
        # -50 to 1064.18°C
        np.array([
            0.000000000000E+00,
            0.540313308631E-02,
            0.125934289740E-04,
            -0.232477968689E-07,
            0.322028823036E-10,
            -0.331465196389E-13,
            0.255744251786E-16,
            -0.125068871393E-19,
            0.271443176145E-23
        ]),
        # 1064.18 to 1664.5°C
        np.array([
            0.132900444085E+01,
            0.334509311344E-02,
            0.654805192818E-05,
            -0.164856259209E-08,
            0.129989605174E-13
        ]),
        # 1664.5 to 1768°C
        np.array([
            0.146628232636E+03,
            -0.258430516752E+00,
            0.163693574641E-03,
            -0.330439046987E-07,
            -0.943223690612E-14
        ])
    ],
    inv_coeffs=[
        # -0.235 to 1.874 mV
        np.array([
            0.00000000E+00,
            1.84949460E+02,
            -8.00504062E+01,
            1.02237430E+02,
            -1.52248592E+02,
            1.88821343E+02,
            -1.59085941E+02,
            8.23027880E+01,
            -2.34181944E+01,
            2.79786260E+00
        ]),
        # 1.874 to 11.950 mV
        np.array([
            1.291507177E+01,
            1.466298863E+02,
            -1.534713402E+01,
            3.145945973E+00,
            -4.163257839E-01,
            3.187963771E-02,
            -1.291637500E-03,
            2.183475087E-05,
            -1.447379511E-07,
            8.211272125E-09
        ]),
        # 11.950 to 18.693 mV
        np.array([
            -8.087801117E+01,
            1.621573104E+02,
            -8.536869453E+00,
            4.719686976E-01,
            -1.441693666E-02,
            2.081618890E-04
        ])
    ],
    inv_voltage_ranges=[
        (-0.235, 1.874),
        (1.874, 11.950),
        (11.950, 18.693)
    ]
)

# Type R Thermocouple (Platinum-13% Rhodium/Platinum)
# Temperature range: -50°C to 1768°C
TYPE_R = Thermocouple(
    name='R',
    temp_ranges=[(-50, 1064.18), (1064.18, 1664.5), (1664.5, 1768)],
    emf_coeffs=[
        # -50 to 1064.18°C
        np.array([
            0.000000000000E+00,
            0.528961729765E-02,
            0.139166589782E-04,
            -0.238855693017E-07,
            0.356916001063E-10,
            -0.462347666298E-13,
            0.500777441034E-16,
            -0.373105886191E-19,
            0.157716482367E-22,
            -0.281038625251E-26
        ]),
        # 1064.18 to 1664.5°C
        np.array([
            0.295157925316E+01,
            -0.252061251332E-02,
            0.159564501865E-04,
            -0.764085947576E-08,
            0.205305291024E-11,
            -0.293359668173E-15
        ]),
        # 1664.5 to 1768°C
        np.array([
            0.152232118209E+03,
            -0.268819888545E+00,
            0.171280280471E-03,
            -0.345895706453E-07,
            -0.934633971046E-14
        ])
    ],
    inv_coeffs=[
        # -0.226 to 1.923 mV
        np.array([
            0.0000000E+00,
            1.8891380E+02,
            -9.3835290E+01,
            1.3068619E+02,
            -2.2703580E+02,
            3.5145659E+02,
            -3.8953900E+02,
            2.8239471E+02,
            -1.2607281E+02,
            3.1353611E+01,
            -3.3187769E+00
        ]),
        # 1.923 to 13.228 mV
        np.array([
            1.334584505E+01,
            1.472644573E+02,
            -1.844024844E+01,
            4.031129726E+00,
            -6.249428360E-01,
            6.468412046E-02,
            -4.458750426E-03,
            1.994710149E-04,
            -5.313401790E-06,
            6.481976217E-08
        ]),
        # 13.228 to 19.739 mV (approximation)
        np.array([
            -8.199599416E+01,
            1.553962042E+02,
            -8.342197663E+00,
            4.279433549E-01,
            -1.191577910E-02,
            1.492290091E-04
        ])
    ],
    inv_voltage_ranges=[
        (-0.226, 1.923),
        (1.923, 13.228),
        (13.228, 19.739)
    ]
)

# Type B Thermocouple (Platinum-30% Rhodium/Platinum-6% Rhodium)
# Temperature range: 0°C to 1820°C
TYPE_B = Thermocouple(
    name='B',
    temp_ranges=[(0, 630.615), (630.615, 1820)],
    emf_coeffs=[
        # 0 to 630.615°C
        np.array([
            0.000000000000E+00,
            -0.246508183460E-03,
            0.590404211710E-05,
            -0.132579316360E-08,
            0.156682919010E-11,
            -0.169445292400E-14,
            0.629903470940E-18
        ]),
        # 630.615 to 1820°C
        np.array([
            -0.389381686210E+01,
            0.285717474700E-01,
            -0.848851047850E-04,
            0.157852801640E-06,
            -0.168353448640E-09,
            0.111097940130E-12,
            -0.445154310330E-16,
            0.989756408210E-20,
            -0.937913302890E-24
        ])
    ],
    inv_coeffs=[
        # 0.291 to 2.431 mV
        np.array([
            9.8423321E+01,
            6.9971500E+02,
            -8.4765304E+02,
            1.0052644E+03,
            -8.3345952E+02,
            4.5508542E+02,
            -1.5523037E+02,
            2.9886750E+01,
            -2.4742860E+00
        ]),
        # 2.431 to 13.820 mV
        np.array([
            2.1315071E+02,
            2.8510504E+02,
            -5.2742887E+01,
            9.9160804E+00,
            -1.2965303E+00,
            1.1195870E-01,
            -6.0625199E-03,
            1.8661696E-04,
            -2.4878585E-06
        ])
    ],
    inv_voltage_ranges=[
        (0.291, 2.431),
        (2.431, 13.820)
    ]
)

# Create dictionary for easy access
thermocouples = {
    'K': TYPE_K,
    'J': TYPE_J,
    'T': TYPE_T,
    'E': TYPE_E,
    'N': TYPE_N,
    'S': TYPE_S,
    'R': TYPE_R,
    'B': TYPE_B
}


if __name__ == "__main__":
    # Simple test
    tc = thermocouples['K']
    print(f"Type K: 1.0 mV at Tref=23°C = {tc.inverse_CmV(1.0, Tref=23.0):.2f}°C")
    print(f"Type K: 47°C at Tref=23°C = {tc.emf_mVC(47.0, Tref=23.0):.4f} mV")
