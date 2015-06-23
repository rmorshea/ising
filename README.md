## Ising Model Animation and Analysis

A quick implamentation of a classic, and simple, representation
of ferromagnetism from thermodynamics

## Installation

This module can be installed with
[antipackage](https://github.com/ellisonbg/antipackage)
using the following commands:

```
import antipackage
from github.rmorshea.ising import ising
```

**Dependancies:** [IPython](http://ipython.org/), [PIL](http://www.pythonware.com/products/pil/), [images2gif](https://pypi.python.org/pypi/images2gif)

## Usage

+ **Animated GIFs:**

	Begin by making a lattice populated with upward or downward polarized ferromagnets:

	```python
	lat = ising.Lattice(x, y, dist, T, nghbrs, size)
	lat
	```

	```
        y : int
            length of the lattice's y dimension
        x : int
            length of the lattice's x dimension
        dist : float
            the distribution of spin up to spin down (between 0 and 1)
        T : float or list
            Given a number, the lattice will remain at a constant temp
            throughout anamations and analysis. However given a list of
            temperatures the lattice will progress through them during
            animation.
        nghbrs : int
            the number of neighbors influencing a particular unit (4 or 8)
        size : int
            size of the rendered units
	```

	Animate `lat` by specifying how many saved frames should be used,
	and how many time steps each one will represent (this step may take some time).
	Then to prepare the frames for `images2gif`, save each one in a directory as
	numbered png files with:

	```python
	lat.animate(time_steps, frames)
	lat.make_pngs()
	```
	
	Finally the last step is to create your GIF with `lat.make_gif()`:

	<img width=200 height=200 src="https://raw.githubusercontent.com/rmorshea/ising/master/docs/Teq1.5.GIF">

+ **Model Analysis:**

	Standard information about the model is given by the output of `lat.analyze()`. This returns the average magnitization, avg energy, and heat capacity at each frame of animation. Alternatively, `lat.get_potentials` returns the average energy and squared average anergy at each frame.

	For more detailed information see `lat.U`, `lat.S`, and `lat.rgbs` for raw data potential, spin, and rgb arrays from each frame of the model's animation.