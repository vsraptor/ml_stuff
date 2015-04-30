# ml_stuff
Random stuff for Machine Learning ...

## fft.py

Fourier Transform model for scikit-learn.
Can be used standalone.
Allows you to predict() future values.
In general repetition of the signal may have sufficed, but I decompose the signal to frequencies
and then you can plot() or predict() using just top N frequencies, instead the full spectrum.
