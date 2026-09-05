# Biquadratics

Reproducible computations for research on biquadratic forms, sum-of-squares
rank, and related extremal graph problems by Johan Löfberg and collaborators.

| Project | Contents |
|---|---|
| [Second order Zarankiewicz numbers](second_order_zarankiewicz_numbers/) | Exact searches, explicit witnesses, independent verifiers, and data for the work of Johan Löfberg and Liqun Qi. |

## Quick start

Python 3.10 or later is sufficient; the required computations use only the
standard library.

~~~console
git clone https://github.com/johanlofberg/biquadratics.git
cd biquadratics/second_order_zarankiewicz_numbers
python scripts/verify_manifest.py
python reproduce.py verify
python reproduce.py all --reference --research
python -m unittest discover -s tests -v
~~~

On Windows, use py -3 in place of python if necessary. See the
[project README](second_order_zarankiewicz_numbers/README.md) for individual
searches, data formats, and the optional independent C++ check.

The [claim-to-evidence index](second_order_zarankiewicz_numbers/CLAIMS.md)
distinguishes exact finite results, supporting checks of analytic theorems,
and unresolved research cases.

Software and accompanying documentation are provided under the [MIT license](LICENSE).
